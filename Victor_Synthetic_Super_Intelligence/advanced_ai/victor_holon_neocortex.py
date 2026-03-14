# victor_holon_neocortex.py
import numpy as np
from collections import deque
import os
import sys

# Handle imports flexibly for different execution contexts
_this_dir = os.path.dirname(os.path.abspath(__file__))
if _this_dir not in sys.path:
    sys.path.insert(0, _this_dir)

from octonion_engine import Octonion

#################################################################
# Utility: Sparse Distributed Representation Layer
#################################################################
class SDRLayer:
    def __init__(self, size, sparsity=0.02):
        self.size = size
        self.k = max(1, int(size * sparsity))

    def encode(self, x):
        # Resize input to match layer size if needed
        if len(x) != self.size:
            if len(x) > self.size:
                # Truncate by taking first 'size' elements
                x = x[:self.size]
            else:
                # Pad with zeros
                x = np.concatenate([x, np.zeros(self.size - len(x))])
        # k-winner-take-all
        idx = np.argpartition(x, -self.k)[-self.k:]
        sdr = np.zeros(self.size)
        sdr[idx] = 1.0
        return sdr


#################################################################
# Temporal Memory (HTM-lite)
#################################################################
class TemporalMemory:
    def __init__(self, size, hist=32):
        self.size = size
        self.history = deque(maxlen=hist)
        self.weights = np.zeros((size, size))
        self.lr = 0.01

    def step(self, sdr):
        if len(self.history) > 0:
            prev = self.history[-1]
            # Hebbian: strengthen connections from previous to current
            self.weights += self.lr * np.outer(prev, sdr)

        self.history.append(sdr)
        pred = self.weights.T @ sdr
        return pred


#################################################################
# Fractal Compression Layer
#################################################################
class FractalCompressor:
    def __init__(self, dim=8, sdr_size=None):
        self.dim = dim  # output octonion dimension
        self._sdr_size = sdr_size
        self._proj = None  # Lazy initialization of projection matrix
        
    def _get_projection(self, sdr_size):
        """Get or create the projection matrix for the given SDR size."""
        if self._proj is None or self._sdr_size != sdr_size:
            # Initialize projection matrix once per unique SDR size
            self._sdr_size = sdr_size
            # Use fixed random state for reproducibility
            rng = np.random.RandomState(42 + sdr_size)
            self._proj = rng.normal(0, 1 / np.sqrt(sdr_size), (sdr_size, self.dim))
        return self._proj

    def compress(self, sdr):
        # compress SDR → octonion via PCA-like random projection
        # Project SDR (size n) to 8 coefficients for octonion
        sdr_size = len(sdr)
        proj = self._get_projection(sdr_size)
        coeffs = np.dot(sdr, proj)
        return Octonion(coeffs)

    def refine(self, octoA, octoB):
        return octoA * octoB


#################################################################
# Omega Tensor Module
#################################################################
class OmegaTensorField:
    def __init__(self):
        self.state = Octonion(np.ones(8) / np.sqrt(8))
        self.decay = 0.98

    def update(self, signal):
        self.state = self.state * signal
        # normalize
        norm = self.state.norm()
        if norm > 0:
            self.state = Octonion(self.state.data / norm * self.decay)
        return self.state


#################################################################
# Full Victor Neocortex
#################################################################
class VictorHolonNeocortex:
    def __init__(self, input_size=2048, layers=3):
        self.layers = [
            SDRLayer(size=max(1, input_size // (2**i)))
            for i in range(layers)
        ]
        self.tm = [
            TemporalMemory(size=layer.size)
            for layer in self.layers
        ]
        self.compressors = [
            FractalCompressor()
            for _ in self.layers
        ]
        self.omega = OmegaTensorField()

    #################################################################
    # Forward Pass → Prediction + Ω-field update
    #################################################################
    def forward(self, vector):
        sdrs = []
        octos = []

        x = vector

        for i, layer in enumerate(self.layers):
            sdr = layer.encode(x)
            pred = self.tm[i].step(sdr)
            octo = self.compressors[i].compress(sdr)

            sdrs.append(sdr)
            octos.append(octo)

            x = pred

        # merge octonions via fractal multiplication chain
        merged = octos[0]
        for o in octos[1:]:
            merged = self.compressors[0].refine(merged, o)

        omega_state = self.omega.update(merged)

        return {
            "sdrs": sdrs,
            "octonions": octos,
            "omega_state": omega_state.data.tolist()
        }

    #################################################################
    # Sleep Cycle → Consolidation
    #################################################################
    def sleep(self, cycles=10):
        for _ in range(cycles):
            noise = np.random.randn(self.layers[0].size)
            self.forward(noise)
        return self.omega.state.data.tolist()


#################################################################
# Standalone Test
#################################################################
if __name__ == "__main__":
    neo = VictorHolonNeocortex()
    x = np.random.randn(2048)
    out = neo.forward(x)
    print("Ω State:", out["omega_state"])
