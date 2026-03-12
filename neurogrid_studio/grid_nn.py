"""
GridNN – The 1024×1024 super-intelligent neural lattice.

Every cell in the grid stores three channels:
  - hue        (0–360°)   layer depth / neuron type
  - intensity  (0–100%)   weight magnitude / activation strength
  - symbol     overlay    categorical metadata (pruned, attention, recurrent, …)

The grid can be used at arbitrary sizes (default 64×64 for CPU-friendly demos;
set size=1024 for full enterprise scale).
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple

import numpy as np


class NeuronSymbol(str, Enum):
    """Categorical overlay symbols rendered on each grid cell."""

    NONE = ""           # pruned / sparse – no symbol
    SUMMATION = "∑"     # summation neuron
    ATTENTION = "⊗"     # attention mechanism
    RECURRENT = "→"     # recurrent connection
    ATTENTION_HEAD = "★"  # multi-head attention head
    INPUT = "▶"         # input layer neuron
    OUTPUT = "◼"        # output layer neuron


# Hue mapping for semantic neuron types (0–360°)
LAYER_HUE: Dict[str, float] = {
    "input": 260.0,    # indigo
    "hidden_shallow": 120.0,  # green
    "hidden_deep": 160.0,     # emerald
    "output": 30.0,    # orange
    "attention": 300.0,  # violet
    "recurrent": 200.0,  # cyan
}


@dataclass
class GridCell:
    """A single neuron cell within the GridNN lattice."""

    row: int
    col: int
    hue: float = 260.0         # 0–360°  – encodes layer / type
    intensity: float = 0.0     # 0–100%  – activation / weight magnitude
    symbol: NeuronSymbol = NeuronSymbol.NONE
    weight: float = 0.0        # raw synaptic weight
    activation: float = 0.0    # post-activation value
    gradient: float = 0.0      # latest gradient magnitude
    layer_depth: int = 0       # 0 = input, N = deepest hidden, N+1 = output

    def to_dict(self) -> dict:
        return {
            "row": self.row,
            "col": self.col,
            "hue": round(self.hue, 2),
            "intensity": round(self.intensity, 2),
            "symbol": self.symbol.value,
            "weight": round(self.weight, 4),
            "activation": round(self.activation, 4),
            "gradient": round(self.gradient, 6),
            "layer_depth": self.layer_depth,
        }


class GridNN:
    """
    A 2-D neural lattice where every neuron is visualisable as a coloured cell.

    Parameters
    ----------
    size : int
        Grid side length (size × size neurons).  Default 64 for CPU demos;
        use 1024 for full enterprise-scale deployment.
    depth : int
        Number of logical layers mapped across the grid height.
    learning_rate : float
        Initial learning rate for gradient-descent training.
    sparsity : float
        Fraction of neurons to prune (set to NeuronSymbol.NONE) each epoch.
    """

    def __init__(
        self,
        size: int = 64,
        depth: int = 8,
        learning_rate: float = 1e-3,
        sparsity: float = 0.1,
        seed: Optional[int] = None,
    ) -> None:
        self.size = size
        self.depth = depth
        self.learning_rate = learning_rate
        self.sparsity = sparsity

        rng = np.random.default_rng(seed)

        # Core weight / activation tensors  (size × size)
        self._weights: np.ndarray = rng.standard_normal((size, size)).astype(np.float32) * 0.1
        self._activations: np.ndarray = np.zeros((size, size), dtype=np.float32)
        self._gradients: np.ndarray = np.zeros((size, size), dtype=np.float32)

        # Derived visualisation arrays (recomputed each step)
        self._hues: np.ndarray = self._init_hues()
        self._intensities: np.ndarray = np.zeros((size, size), dtype=np.float32)
        self._symbols: np.ndarray = self._init_symbols(rng)

        # Training state
        self.epoch: int = 0
        self.step: int = 0
        self.loss_history: List[float] = []
        self.created_at: float = time.time()

        # Recompute derived arrays once at init
        self._update_visual_arrays()

    # ------------------------------------------------------------------
    # Initialisation helpers
    # ------------------------------------------------------------------

    def _init_hues(self) -> np.ndarray:
        """Assign hue by row (row 0 = input layer, last row = output layer)."""
        hues = np.zeros((self.size, self.size), dtype=np.float32)
        for row in range(self.size):
            depth_fraction = row / max(self.size - 1, 1)
            if depth_fraction < 0.05:
                hue = LAYER_HUE["input"]
            elif depth_fraction > 0.95:
                hue = LAYER_HUE["output"]
            elif depth_fraction < 0.5:
                hue = LAYER_HUE["hidden_shallow"]
            else:
                hue = LAYER_HUE["hidden_deep"]
            hues[row, :] = hue
        return hues

    def _init_symbols(self, rng: np.random.Generator) -> np.ndarray:
        """Randomly seed initial symbol overlay; most cells start sparse."""
        symbols = np.full((self.size, self.size), NeuronSymbol.NONE, dtype=object)
        # ~5 % attention heads
        mask_att = rng.random((self.size, self.size)) < 0.05
        symbols[mask_att] = NeuronSymbol.ATTENTION_HEAD
        # ~3 % recurrent
        mask_rec = rng.random((self.size, self.size)) < 0.03
        symbols[mask_rec] = NeuronSymbol.RECURRENT
        # Input and output rows
        symbols[0, :] = NeuronSymbol.INPUT
        symbols[-1, :] = NeuronSymbol.OUTPUT
        return symbols

    # ------------------------------------------------------------------
    # Forward pass
    # ------------------------------------------------------------------

    def forward(self, x: np.ndarray) -> np.ndarray:
        """
        One forward pass through the lattice.

        Parameters
        ----------
        x : np.ndarray shape (size,)  – input activation row.

        Returns
        -------
        np.ndarray shape (size,) – output activation row.
        """
        if x.shape[0] != self.size:
            raise ValueError(
                f"Input length {x.shape[0]} != grid size {self.size}"
            )

        act = x.astype(np.float32)
        self._activations[0, :] = act

        for row in range(1, self.size):
            # Simple dense-layer approximation: row weights × previous row
            row_weights = self._weights[row, :]
            raw = act * row_weights
            act = np.tanh(raw)
            self._activations[row, :] = act

        self._update_visual_arrays()
        return self._activations[-1, :]

    # ------------------------------------------------------------------
    # Backward pass (single-step SGD)
    # ------------------------------------------------------------------

    def backward(self, loss_grad: np.ndarray) -> float:
        """
        One backward pass with simple SGD weight update.

        Parameters
        ----------
        loss_grad : np.ndarray shape (size,) – gradient of loss w.r.t output.

        Returns
        -------
        float – mean absolute gradient magnitude.
        """
        grad = loss_grad.astype(np.float32)
        self._gradients[-1, :] = np.abs(grad)

        for row in range(self.size - 2, -1, -1):
            # Gradient propagated back through tanh
            act = self._activations[row + 1, :]
            dtanh = 1.0 - act ** 2
            grad = grad * dtanh * self._weights[row + 1, :]
            self._gradients[row, :] = np.abs(grad)

            # Weight update
            self._weights[row + 1, :] -= self.learning_rate * grad * self._activations[row, :]

        self._apply_sparsity()
        self._update_visual_arrays()
        return float(np.mean(self._gradients))

    # ------------------------------------------------------------------
    # Pruning / sparsity
    # ------------------------------------------------------------------

    def _apply_sparsity(self) -> None:
        """Zero out the lowest-magnitude weights according to sparsity ratio."""
        flat = np.abs(self._weights).ravel()
        threshold_idx = int(len(flat) * self.sparsity)
        if threshold_idx == 0:
            return
        threshold = np.partition(flat, threshold_idx)[threshold_idx]
        pruned_mask = np.abs(self._weights) < threshold
        self._weights[pruned_mask] = 0.0
        # Mark pruned neurons with NONE symbol
        self._symbols[pruned_mask] = NeuronSymbol.NONE

    # ------------------------------------------------------------------
    # Visual array sync
    # ------------------------------------------------------------------

    def _update_visual_arrays(self) -> None:
        """Sync hue / intensity arrays from current weights & activations."""
        weight_mag = np.abs(self._weights)
        max_w = weight_mag.max() or 1.0
        self._intensities = (weight_mag / max_w * 100.0).astype(np.float32)

        # Shift hue slightly towards attention hue for high-gradient neurons
        grad_mag = self._gradients
        max_g = grad_mag.max() or 1.0
        grad_norm = grad_mag / max_g
        self._hues = self._hues * (1.0 - 0.1 * grad_norm) + LAYER_HUE["attention"] * 0.1 * grad_norm

    # ------------------------------------------------------------------
    # Grid snapshot
    # ------------------------------------------------------------------

    def get_grid_snapshot(self, sample_rate: int = 1) -> List[dict]:
        """
        Return a list of cell dicts suitable for JSON serialisation.

        Parameters
        ----------
        sample_rate : int
            Return every Nth cell (1 = all cells, 4 = every 4th, …) for
            bandwidth-limited streaming.
        """
        cells = []
        for row in range(0, self.size, sample_rate):
            for col in range(0, self.size, sample_rate):
                depth_fraction = row / max(self.size - 1, 1)
                cell = {
                    "row": row,
                    "col": col,
                    "hue": round(float(self._hues[row, col]), 2),
                    "intensity": round(float(self._intensities[row, col]), 2),
                    "symbol": self._symbols[row, col].value
                    if isinstance(self._symbols[row, col], NeuronSymbol)
                    else str(self._symbols[row, col]),
                    "weight": round(float(self._weights[row, col]), 4),
                    "activation": round(float(self._activations[row, col]), 4),
                    "gradient": round(float(self._gradients[row, col]), 6),
                    "layer_depth": int(depth_fraction * self.depth),
                }
                cells.append(cell)
        return cells

    def get_cell(self, row: int, col: int) -> GridCell:
        """Return a GridCell object for a specific position."""
        if not (0 <= row < self.size and 0 <= col < self.size):
            raise IndexError(f"Cell ({row}, {col}) out of bounds for grid size {self.size}")
        depth_fraction = row / max(self.size - 1, 1)
        return GridCell(
            row=row,
            col=col,
            hue=float(self._hues[row, col]),
            intensity=float(self._intensities[row, col]),
            symbol=self._symbols[row, col]
            if isinstance(self._symbols[row, col], NeuronSymbol)
            else NeuronSymbol.NONE,
            weight=float(self._weights[row, col]),
            activation=float(self._activations[row, col]),
            gradient=float(self._gradients[row, col]),
            layer_depth=int(depth_fraction * self.depth),
        )

    def explain_cell(self, row: int, col: int) -> dict:
        """
        Produce a plain-English explanation of what neuron (row, col) is doing.
        Implements the "AI Co-Pilot" click-to-explain feature.
        """
        cell = self.get_cell(row, col)
        depth_fraction = row / max(self.size - 1, 1)

        if depth_fraction < 0.05:
            role = "an input neuron that receives raw data"
        elif depth_fraction > 0.95:
            role = "an output neuron that produces the model's prediction"
        elif depth_fraction < 0.5:
            role = "a shallow hidden neuron that learns low-level features"
        else:
            role = "a deep hidden neuron that encodes abstract representations"

        symbol_desc = {
            NeuronSymbol.NONE: "sparse/pruned – it is not actively contributing",
            NeuronSymbol.SUMMATION: "a summation gate accumulating multiple signals",
            NeuronSymbol.ATTENTION: "an attention mechanism weighting input relevance",
            NeuronSymbol.RECURRENT: "a recurrent connection feeding its output back",
            NeuronSymbol.ATTENTION_HEAD: "a multi-head attention head",
            NeuronSymbol.INPUT: "an input receptor",
            NeuronSymbol.OUTPUT: "a final output projector",
        }.get(cell.symbol, "unknown role")

        return {
            "cell": cell.to_dict(),
            "explanation": (
                f"Neuron [{row}, {col}] is {role}. "
                f"Its current activation is {cell.activation:.4f} and "
                f"its weight magnitude is {cell.weight:.4f}. "
                f"It acts as {symbol_desc}. "
                f"Intensity {cell.intensity:.1f}% indicates "
                + ("strong" if cell.intensity > 60 else "moderate" if cell.intensity > 30 else "weak")
                + " influence on the network's output."
            ),
        }

    def get_stats(self) -> dict:
        """Return a summary of the current grid state."""
        active_mask = self._intensities > 10
        pruned_count = int(np.sum(self._symbols == NeuronSymbol.NONE))
        return {
            "size": self.size,
            "total_neurons": self.size * self.size,
            "active_neurons": int(np.sum(active_mask)),
            "pruned_neurons": pruned_count,
            "mean_weight": round(float(np.mean(np.abs(self._weights))), 6),
            "max_intensity": round(float(self._intensities.max()), 2),
            "mean_intensity": round(float(self._intensities.mean()), 2),
            "epoch": self.epoch,
            "step": self.step,
            "loss_history_len": len(self.loss_history),
            "latest_loss": round(self.loss_history[-1], 6) if self.loss_history else None,
        }
