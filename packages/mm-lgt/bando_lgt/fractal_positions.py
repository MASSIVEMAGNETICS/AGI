from __future__ import annotations

import math

import torch


def make_fractal_positions(
    max_seq_len: int,
    pos_dim: int = 8,
    *,
    device: torch.device | str | None = None,
    dtype: torch.dtype = torch.float32,
) -> torch.Tensor:
    """Return deterministic, normalized multi-scale positional coordinates."""
    if max_seq_len < 2:
        raise ValueError("max_seq_len must be at least 2")
    if pos_dim < 3:
        raise ValueError("pos_dim must be at least 3")

    phi = (1.0 + math.sqrt(5.0)) / 2.0
    index = torch.arange(max_seq_len, device=device, dtype=dtype)
    normalized = index / float(max_seq_len - 1)
    columns: list[torch.Tensor] = [normalized, 1.0 - normalized]

    level = 1
    while len(columns) < pos_dim:
        frequency = phi**level
        columns.append(torch.sin(2.0 * math.pi * normalized * frequency))
        if len(columns) < pos_dim:
            columns.append(torch.cos(2.0 * math.pi * normalized * frequency))
        if len(columns) < pos_dim:
            phase = torch.remainder(normalized * (2**level), 2.0)
            fold = 1.0 - 2.0 * torch.abs(phase - 1.0)
            columns.append(fold)
        level += 1

    positions = torch.stack(columns[:pos_dim], dim=-1)
    positions = positions - positions.mean(dim=0, keepdim=True)
    scale = positions.std(dim=0, keepdim=True, unbiased=False).clamp_min(1e-6)
    return positions / scale

