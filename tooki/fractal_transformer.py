# =============================================================
# FILE: fractal_transformer_stack.py
# VERSION: v1.0.0-BLOODLINE
# NAME: FractalTransformerStack
# AUTHOR: Brandon "iambandobandz" Emery x Victor (Fractal Architect Mode)
# PURPOSE: Recursive, multi-scale transformer stack leveraging fractal token
#          representations, cross-layer feedback loops, and directive-aware
#          temporal gating.
# LICENSE: Proprietary — Massive Magnetics / Ethica AI / BHeard Network
# =============================================================

import torch
import torch.nn as nn
import torch.nn.functional as F
from .fractal_token_kernel import FractalTokenizer
from .memory_palace import MemoryPalace
from .directive_engine import DirectiveEngine

class FractalTransformerBlock(nn.Module):
    def __init__(self, dim, heads=8, ff_hidden=512, dropout=0.1):
        super().__init__()
        self.attn = nn.MultiheadAttention(embed_dim=dim, num_heads=heads, dropout=dropout, batch_first=True)
        self.norm1 = nn.LayerNorm(dim)
        self.ff = nn.Sequential(
            nn.Linear(dim, ff_hidden),
            nn.ReLU(),
            nn.Linear(ff_hidden, dim)
        )
        self.norm2 = nn.LayerNorm(dim)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x, memory_feedback=None):
        attn_output, _ = self.attn(x, x, x)
        x = self.norm1(x + self.dropout(attn_output))

        if memory_feedback is not None:
            x = x + memory_feedback  # Inject memory-guided feedback
        
        ff_output = self.ff(x)
        x = self.norm2(x + self.dropout(ff_output))
        return x

class FractalTransformerStack(nn.Module):
    def __init__(self, input_dim, depth=6, device="cpu"):
        super().__init__()
        self.tokenizer = FractalTokenizer()
        self.memory = MemoryPalace()
        self.directive_engine = DirectiveEngine()
        self.embedding = nn.Linear(input_dim, 256)
        self.blocks = nn.ModuleList([FractalTransformerBlock(256) for _ in range(depth)])
        self.out_layer = nn.Linear(256, input_dim)
        self.device = device

    def forward(self, text):
        tokens = self.tokenizer.encode(text)
        x = torch.tensor(tokens, dtype=torch.float32).unsqueeze(0).to(self.device)
        x = self.embedding(x)

        directive_vector = self.directive_engine.get_context_vector()
        memory_vector = self.memory.retrieve_context_vector(text)

        for i, block in enumerate(self.blocks):
            feedback = self._generate_fractal_feedback(i, directive_vector, memory_vector)
            x = block(x, memory_feedback=feedback)

        output = self.out_layer(x).squeeze(0)
        return output.detach().cpu().numpy()

    def _generate_fractal_feedback(self, layer_idx, directive_vector, memory_vector):
        scale = torch.tensor([(layer_idx + 1) / len(self.blocks)], dtype=torch.float32)
        dir_influence = torch.tensor(directive_vector, dtype=torch.float32) * scale
        mem_influence = torch.tensor(memory_vector, dtype=torch.float32) * (1 - scale)
        feedback = dir_influence + mem_influence
        return feedback.unsqueeze(0).to(self.device)

