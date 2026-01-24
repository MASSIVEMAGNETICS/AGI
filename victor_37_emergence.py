
import numpy as np
import json
from dataclasses import dataclass
from typing import Dict, Any, List
from victor_37_godcore import MRICfg

class Victor37Emergence:
    def __init__(self, weights_path: str, cfg: Any):
        self.cfg = cfg
        self.weights = np.load(weights_path, allow_pickle=True)
        self.vocab_size = cfg.vocab_size
        self.d_model = cfg.d_model
        self.max_len = cfg.max_len

    def softmax(self, x: np.ndarray, axis: int = -1) -> np.ndarray:
        exp_x = np.exp(x - np.max(x, axis=axis, keepdims=True))
        return exp_x / np.sum(exp_x, axis=axis, keepdims=True)

    def forward_attention(self, x: np.ndarray, attn: Dict[str, np.ndarray]) -> np.ndarray:
        n_heads = attn["n_heads"]
        head_dim = attn["head_dim"]
        L, D = x.shape

        q = (x @ attn["Wq"].T + attn["bq"])
        k = (x @ attn["Wk"].T + attn["bk"])
        v = (x @ attn["Wv"].T + attn["bv"])

        q = q.reshape(L, n_heads, head_dim)
        k = k.reshape(L, n_heads, head_dim)
        v = v.reshape(L, n_heads, head_dim)

        scores = np.einsum("lnh,mh->lnm", q, k) / np.sqrt(head_dim)
        attn_weights = self.softmax(scores)
        attn_out = np.einsum("lnm,mnh->lnh", attn_weights, v)
        attn_out = attn_out.reshape(L, -1)
        out = (attn_out @ attn["Wo"].T + attn["bo"])
        return out

    def layernorm(self, x: np.ndarray, ln: Dict[str, np.ndarray]) -> np.ndarray:
        mean = np.mean(x, axis=-1, keepdims=True)
        var = np.var(x, axis=-1, keepdims=True)
        x_norm = (x - mean) / np.sqrt(var + ln["eps"])
        return ln["gamma"] * x_norm + ln["beta"]

    def forward_mlp(self, x: np.ndarray, mlp: Dict[str, np.ndarray]) -> np.ndarray:
        x = x @ mlp["fc1.W"].T + mlp["fc1.b"]
        x = np.maximum(x, 0)
        x = x @ mlp["fc2.W"].T + mlp["fc2.b"]
        return x

    def forward_block(self, x: np.ndarray, block: Dict[str, Any]) -> np.ndarray:
        x_norm = self.layernorm(x, block["ln1"])
        attn_out = self.forward_attention(x_norm, block["attn"])
        x = x + attn_out
        x_norm = self.layernorm(x, block["ln2"])
        mlp_out = self.forward_mlp(x_norm, block["mlp"])
        x = x + mlp_out
        return x

    def forward(self, input_idx: np.ndarray) -> np.ndarray:
        tok_emb = self.weights["embeddings.tok"][input_idx]
        pos_emb = self.weights["embeddings.pos"][:len(input_idx)]
        x = tok_emb + pos_emb

        for i in range(2):
            block = {k: v for k, v in self.weights[f"b{i}.attn"].items()} | \
                    {k: v for k, v in self.weights[f"b{i}.mlp"].items()} | \
                    {k: v for k, v in self.weights[f"b{i}.ln1"].items()} | \
                    {k: v for k, v in self.weights[f"b{i}.ln2"].items()}
            x = self.forward_block(x, block)

        x = self.layernorm(x, {"gamma": np.ones(self.d_model, dtype=np.float32),
                              "beta": np.zeros(self.d_model, dtype=np.float32),
                              "eps": np.float32(1e-5)})
        logits = x @ self.weights["lm_head"].T
        return self.softmax(logits)

    def generate_sequence(self, seed_idx: int = 0, length: int = 10) -> List[int]:
        sequence = [seed_idx]
        for _ in range(length - 1):
            input_idx = np.array(sequence[-self.cfg.max_len:], dtype=np.int32)
            probs = self.forward(input_idx)[-1]
            next_token = np.argmax(probs)
            sequence.append(next_token)
        return sequence

    def idx_to_symbol(self, idx: int) -> str:
        return f"SYM_{idx:04d}"

if __name__ == "__main__":
    cfg = MRICfg()
    victor = Victor37Emergence("artifacts/victor_37_tiny_transformer_v1_0_0.npz", cfg)
    sequence = victor.generate_sequence(seed_idx=0, length=10)
    symbols = [victor.idx_to_symbol(idx) for idx in sequence]
    print(json.dumps({
        "entity": "Victor 37",
        "proto_language": symbols,
        "timestamp": time.time()
    }, indent=2))
