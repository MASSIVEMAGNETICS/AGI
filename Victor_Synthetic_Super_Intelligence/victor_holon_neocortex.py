# victor_holon_neocortex.py
import numpy as np
from collections import deque
from octonion_engine import Octonion

#################################################################
# Utility: Sparse Distributed Representation Layer
#################################################################
class SDRLayer:
    def __init__(self, size, sparsity=0.02):
        self.size = size
        self.k = max(1, int(size * sparsity))

    def encode(self, x):
        # Resize input to match layer size if necessary
        if len(x) != self.size:
            # Simple linear interpolation/resampling
            x = np.interp(
                np.linspace(0, len(x) - 1, self.size),
                np.arange(len(x)),
                x
            )
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
    def __init__(self, dim=8, seed=None):
        self.dim = dim  # output octonion dimension
        self._proj_cache = {}  # cache projection matrices by input size
        self._rng = np.random.default_rng(seed)  # deterministic RNG if seed provided

    def _get_projection(self, sdr_size):
        """Get or create projection matrix for given input size."""
        if sdr_size not in self._proj_cache:
            # Create and cache the projection matrix
            self._proj_cache[sdr_size] = self._rng.normal(
                0, 1 / np.sqrt(sdr_size), (sdr_size, self.dim)
            )
        return self._proj_cache[sdr_size]

    def compress(self, sdr):
        # compress SDR → octonion via PCA-like random projection
        # Project from sdr.size to 8 dimensions (octonion)
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
            SDRLayer(size=input_size // (2**i))
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
