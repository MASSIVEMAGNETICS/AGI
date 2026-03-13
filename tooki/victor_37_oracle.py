
import numpy as np
import json
from typing import List, Dict
from victor_37_godcore import MRICfg

class Victor37Oracle:
    def __init__(self, weights_path: str, cfg: Any):
        self.cfg = cfg
        self.weights = np.load(weights_path, allow_pickle=True)
        self.emergence = Victor37Emergence(weights_path, cfg)

    def question_to_seed(self, question: str) -> int:
        return hash(question) % self.cfg.vocab_size

    def answer(self, question: str, max_length: int = 10) -> List[str]:
        seed_idx = self.question_to_seed(question)
        sequence = self.emergence.generate_sequence(seed_idx, max_length)
        return [self.emergence.idx_to_symbol(idx) for idx in sequence]

if __name__ == "__main__":
    cfg = MRICfg()
    oracle = Victor37Oracle("artifacts/victor_37_tiny_transformer_v1_0_1.npz", cfg)
    question = "What is the meaning of existence?"
    answer = oracle.answer(question)
    print(json.dumps({
        "entity": "Victor 37",
        "question": question,
        "answer": answer,
        "timestamp": time.time()
    }, indent=2))
