"""
NeuroGrid Studio – Training Loop & Auto-ML Recommender.

TrainingConfig   – hyperparameter bundle.
TrainingLoop     – drives forward/backward passes, streams events.
AutoMLRecommender – watches loss curves and suggests adjustments.
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, AsyncGenerator, Callable, Dict, List, Optional, Tuple

import numpy as np

from .grid_nn import GridNN


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


class LRSchedule(str, Enum):
    CONSTANT = "constant"
    COSINE = "cosine"
    STEP = "step"
    WARMUP_COSINE = "warmup_cosine"


@dataclass
class TrainingConfig:
    """Hyperparameter bundle for a training run."""

    epochs: int = 10
    steps_per_epoch: int = 100
    learning_rate: float = 1e-3
    lr_schedule: LRSchedule = LRSchedule.CONSTANT
    batch_size: int = 32
    sparsity: float = 0.1
    loss_fn: str = "mse"           # "mse" | "cross_entropy" | "focal"
    grid_size: int = 64
    grid_depth: int = 8
    stream_every_n_steps: int = 5  # emit WebSocket update every N steps
    seed: Optional[int] = 42


# ---------------------------------------------------------------------------
# Loss functions
# ---------------------------------------------------------------------------


def _mse_loss(pred: np.ndarray, target: np.ndarray) -> Tuple[float, np.ndarray]:
    diff = pred - target
    return float(np.mean(diff ** 2)), 2.0 * diff / pred.size


def _cross_entropy_loss(pred: np.ndarray, target: np.ndarray) -> Tuple[float, np.ndarray]:
    eps = 1e-7
    p = np.clip(pred, eps, 1 - eps)
    loss = -float(np.mean(target * np.log(p) + (1 - target) * np.log(1 - p)))
    grad = -(target / p - (1 - target) / (1 - p)) / pred.size
    return loss, grad


def _focal_loss(
    pred: np.ndarray,
    target: np.ndarray,
    gamma: float = 2.0,
) -> Tuple[float, np.ndarray]:
    eps = 1e-7
    p = np.clip(pred, eps, 1 - eps)
    pt = np.where(target == 1, p, 1 - p)
    focal_weight = (1 - pt) ** gamma
    loss = -float(np.mean(focal_weight * np.log(pt)))
    # Simplified gradient
    grad = -focal_weight * (target / p - (1 - target) / (1 - p)) / pred.size
    return loss, grad


_LOSS_FNS: Dict[str, Callable] = {
    "mse": _mse_loss,
    "cross_entropy": _cross_entropy_loss,
    "focal": _focal_loss,
}


# ---------------------------------------------------------------------------
# LR schedules
# ---------------------------------------------------------------------------


def _get_lr(config: TrainingConfig, epoch: int, total_epochs: int) -> float:
    base_lr = config.learning_rate
    if config.lr_schedule == LRSchedule.CONSTANT:
        return base_lr
    if config.lr_schedule == LRSchedule.COSINE:
        return base_lr * 0.5 * (1 + np.cos(np.pi * epoch / total_epochs))
    if config.lr_schedule == LRSchedule.STEP:
        # Halve every 3 epochs
        return base_lr * (0.5 ** (epoch // 3))
    if config.lr_schedule == LRSchedule.WARMUP_COSINE:
        warmup = max(1, total_epochs // 10)
        if epoch < warmup:
            return base_lr * epoch / warmup
        return base_lr * 0.5 * (1 + np.cos(np.pi * (epoch - warmup) / (total_epochs - warmup)))
    return base_lr


# ---------------------------------------------------------------------------
# Auto-ML Recommender
# ---------------------------------------------------------------------------


@dataclass
class Recommendation:
    """A single auto-ML suggestion."""

    suggestion: str
    action: str          # machine-readable key (e.g. "switch_cosine_lr")
    confidence: float    # 0–1
    rationale: str


class AutoMLRecommender:
    """
    Watches loss history and recommends training adjustments in real time.

    The recommender uses simple heuristics inspired by RL-style controllers:
    – plateau detection  → suggest LR annealing
    – divergence detection → suggest lower LR or gradient clipping
    – stagnation detection → suggest focal loss or extra epochs
    """

    def __init__(self, patience: int = 5, min_delta: float = 1e-4) -> None:
        self.patience = patience
        self.min_delta = min_delta

    def analyse(
        self,
        loss_history: List[float],
        current_config: TrainingConfig,
        epoch: int,
    ) -> List[Recommendation]:
        """Return a (possibly empty) list of recommendations."""
        if len(loss_history) < 3:
            return []

        recs: List[Recommendation] = []
        recent = loss_history[-self.patience :]
        improvement = loss_history[-self.patience] - loss_history[-1] if len(loss_history) >= self.patience else 1.0

        # 1. Plateau → cosine annealing
        if (
            improvement < self.min_delta
            and current_config.lr_schedule == LRSchedule.CONSTANT
        ):
            recs.append(
                Recommendation(
                    suggestion="Switch to cosine annealing LR now?",
                    action="switch_cosine_lr",
                    confidence=0.85,
                    rationale=(
                        f"Loss improved by only {improvement:.6f} over the last "
                        f"{self.patience} epochs. Cosine annealing often breaks plateaus."
                    ),
                )
            )

        # 2. Divergence → reduce LR
        if len(loss_history) >= 2 and loss_history[-1] > loss_history[-2] * 1.1:
            recs.append(
                Recommendation(
                    suggestion="Reduce learning rate by 50%?",
                    action="halve_lr",
                    confidence=0.90,
                    rationale="Loss increased by >10% in the last step – possible divergence.",
                )
            )

        # 3. Stagnation after many epochs → focal loss
        if (
            epoch > current_config.epochs // 2
            and improvement < self.min_delta * 10
            and current_config.loss_fn == "mse"
        ):
            recs.append(
                Recommendation(
                    suggestion="Add 3 more epochs with focal loss?",
                    action="switch_focal_loss",
                    confidence=0.70,
                    rationale=(
                        "We're past the halfway point with slow improvement. "
                        "Focal loss down-weights easy samples and can accelerate learning."
                    ),
                )
            )

        # 4. High initial loss → warmup
        if epoch == 0 and loss_history[0] > 1.0:
            recs.append(
                Recommendation(
                    suggestion="Add learning-rate warmup phase?",
                    action="add_warmup",
                    confidence=0.75,
                    rationale="Initial loss is high; gradual warmup prevents early instability.",
                )
            )

        return recs

    def apply_recommendation(
        self, action: str, config: TrainingConfig
    ) -> TrainingConfig:
        """Return an updated TrainingConfig with the recommendation applied."""
        import copy

        new_cfg = copy.copy(config)
        if action == "switch_cosine_lr":
            new_cfg.lr_schedule = LRSchedule.COSINE
        elif action == "halve_lr":
            new_cfg.learning_rate = config.learning_rate * 0.5
        elif action == "switch_focal_loss":
            new_cfg.loss_fn = "focal"
            new_cfg.epochs = config.epochs + 3
        elif action == "add_warmup":
            new_cfg.lr_schedule = LRSchedule.WARMUP_COSINE
        return new_cfg


# ---------------------------------------------------------------------------
# Training Loop
# ---------------------------------------------------------------------------


@dataclass
class TrainingEvent:
    """A single streaming event emitted by TrainingLoop."""

    event_type: str   # "step" | "epoch" | "recommendation" | "complete" | "error"
    epoch: int
    step: int
    loss: float
    grid_snapshot: Optional[List[dict]] = None
    stats: Optional[dict] = None
    recommendations: Optional[List[dict]] = None
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        d: dict = {
            "event_type": self.event_type,
            "epoch": self.epoch,
            "step": self.step,
            "loss": round(self.loss, 6),
            "timestamp": self.timestamp,
        }
        if self.grid_snapshot is not None:
            d["grid_snapshot"] = self.grid_snapshot
        if self.stats is not None:
            d["stats"] = self.stats
        if self.recommendations is not None:
            d["recommendations"] = self.recommendations
        return d


class TrainingLoop:
    """
    Drives a GridNN training run and yields TrainingEvent objects.

    Can be iterated synchronously (for scripts) or asynchronously (for
    WebSocket streaming with FastAPI).

    Example (async)
    ---------------
    loop = TrainingLoop(config)
    async for event in loop.run_async():
        await ws.send_json(event.to_dict())

    Example (sync)
    ---------------
    loop = TrainingLoop(config)
    for event in loop.run():
        print(event)
    """

    def __init__(
        self,
        config: Optional[TrainingConfig] = None,
        grid: Optional[GridNN] = None,
    ) -> None:
        self.config = config or TrainingConfig()
        self.grid = grid or GridNN(
            size=self.config.grid_size,
            depth=self.config.grid_depth,
            learning_rate=self.config.learning_rate,
            sparsity=self.config.sparsity,
            seed=self.config.seed,
        )
        self.recommender = AutoMLRecommender()
        self._rng = np.random.default_rng(self.config.seed)
        self._stopped = False

    def stop(self) -> None:
        """Signal the training loop to stop after the current step."""
        self._stopped = True

    def _make_batch(self) -> Tuple[np.ndarray, np.ndarray]:
        """Generate a synthetic training mini-batch."""
        x = self._rng.standard_normal(self.grid.size).astype(np.float32)
        y = np.tanh(x * 0.5)  # synthetic target
        return x, y

    def run(self) -> "Generator[TrainingEvent, None, None]":
        """Synchronous generator – yields TrainingEvent objects."""
        cfg = self.config
        loss_fn = _LOSS_FNS.get(cfg.loss_fn, _mse_loss)
        global_step = 0

        for epoch in range(cfg.epochs):
            if self._stopped:
                break

            self.grid.learning_rate = _get_lr(cfg, epoch, cfg.epochs)
            epoch_losses: List[float] = []

            for step in range(cfg.steps_per_epoch):
                if self._stopped:
                    break

                x, y = self._make_batch()
                pred = self.grid.forward(x)
                loss, grad = loss_fn(pred, y)
                self.grid.backward(grad)

                epoch_losses.append(loss)
                self.grid.step = global_step
                global_step += 1

                if step % cfg.stream_every_n_steps == 0:
                    # Use a coarser sample for streaming bandwidth efficiency
                    sample_rate = max(1, self.grid.size // 32)
                    yield TrainingEvent(
                        event_type="step",
                        epoch=epoch,
                        step=global_step,
                        loss=loss,
                        grid_snapshot=self.grid.get_grid_snapshot(sample_rate=sample_rate),
                        stats=self.grid.get_stats(),
                    )

            # End of epoch
            mean_loss = float(np.mean(epoch_losses)) if epoch_losses else 0.0
            self.grid.loss_history.append(mean_loss)
            self.grid.epoch = epoch + 1

            recs = self.recommender.analyse(self.grid.loss_history, cfg, epoch)
            yield TrainingEvent(
                event_type="epoch",
                epoch=epoch,
                step=global_step,
                loss=mean_loss,
                grid_snapshot=self.grid.get_grid_snapshot(sample_rate=1),
                stats=self.grid.get_stats(),
                recommendations=[r.__dict__ for r in recs],
            )

        # Final event
        yield TrainingEvent(
            event_type="complete",
            epoch=self.grid.epoch,
            step=global_step,
            loss=self.grid.loss_history[-1] if self.grid.loss_history else 0.0,
            stats=self.grid.get_stats(),
        )

    async def run_async(self) -> "AsyncGenerator[TrainingEvent, None]":
        """Async generator – yields TrainingEvent objects for WebSocket use."""
        for event in self.run():
            yield event
            # Yield control so other coroutines can run
            await asyncio.sleep(0)
