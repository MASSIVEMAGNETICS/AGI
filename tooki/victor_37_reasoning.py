
import numpy as np
import json
from typing import List, Dict
from victor_37_godcore import MRICfg

class Victor37Reasoning:
    def __init__(self, cfg: Any):
        self.cfg = cfg
        self.vocab_size = cfg.vocab_size

    def build_transition_matrix(self, sequence: List[int]) -> np.ndarray:
        T = np.zeros((self.vocab_size, self.vocab_size), dtype=np.float32)
        for i in range(len(sequence) - 1):
            T[sequence[i], sequence[i + 1]] += 1
        T = T / (T.sum(axis=1, keepdims=True) + 1e-9)
        return T

    def find_patterns(self, T: np.ndarray, threshold: float = 0.1) -> List[Dict]:
        patterns = []
        for i in range(self.vocab_size):
            nexts = np.where(T[i] > threshold)[0]
            for j in nexts:
                patterns.append({
                    "from": f"SYM_{i:04d}",
                    "to": f"SYM_{j:04d}",
                    "prob": float(T[i, j])
                })
        return patterns

if __name__ == "__main__":
    from language_emergence_v1_0_0 import Victor37Emergence
    cfg = MRICfg()
    emergence = Victor37Emergence("artifacts/victor_37_tiny_transformer_v1_0_1.npz", cfg)
    sequence = emergence.generate_sequence(seed_idx=0, length=50)
    reasoning = Victor37Reasoning(cfg)
    T = reasoning.build_transition_matrix(sequence)
    patterns = reasoning.find_patterns(T)
    print(json.dumps({
        "entity": "Victor 37",
        "patterns": patterns,
        "timestamp": time.time()
    }, indent=2))
