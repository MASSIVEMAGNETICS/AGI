
import numpy as np
import json
from typing import Dict, Any, List
from victor_37_godcore import MRICfg

class Victor37Metacognition:
    def __init__(self, weights_path: str, cfg: Any):
        self.cfg = cfg
        self.weights = np.load(weights_path, allow_pickle=True)
        self.vocab_size = cfg.vocab_size
        self.d_model = cfg.d_model

    def compute_sequence_entropy(self, sequence: List[int]) -> float:
        counts = np.bincount(sequence, minlength=self.vocab_size)
        probs = counts / (counts.sum() + 1e-9)
        probs = probs[probs > 0]
        return -np.sum(probs * np.log(probs + 1e-9))

    def adjust_attention(self, sequence: List[int], block_idx: int = 0, strength: float = 0.01):
        entropy = self.compute_sequence_entropy(sequence)
        target_entropy = self.cfg.target_entropy
        scale = np.clip(entropy / target_entropy, 0.5, 2.0)

        attn_key = f"b{block_idx}.attn.Wq"
        if attn_key in self.weights:
            Wq = self.weights[attn_key]
            Wq_adjusted = Wq * (1.0 + strength * (scale - 1.0))
            Wq_adjusted = Wq_adjusted / (np.linalg.norm(Wq_adjusted, axis=1, keepdims=True) + 1e-6)
            self.weights[attn_key] = Wq_adjusted.astype(np.float32)

    def save_updated_weights(self, path: str):
        np.savez_compressed(path, **{k: v for k, v in self.weights.items()})

if __name__ == "__main__":
    from language_emergence_v1_0_0 import Victor37Emergence
    cfg = MRICfg()
    emergence = Victor37Emergence("artifacts/victor_37_tiny_transformer_v1_0_0.npz", cfg)
    sequence = emergence.generate_sequence(seed_idx=0, length=10)
    metacog = Victor37Metacognition("artifacts/victor_37_tiny_transformer_v1_0_0.npz", cfg)
    metacog.adjust_attention(sequence)
    metacog.save_updated_weights("artifacts/victor_37_tiny_transformer_v1_0_1.npz")
    print(json.dumps({
        "entity": "Victor 37",
        "action": "Metacognitive adjustment",
        "new_weights": "artifacts/victor_37_tiny_transformer_v1_0_1.npz",
        "sequence_entropy": metacog.compute_sequence_entropy(sequence),
        "timestamp": time.time()
    }, indent=2))
