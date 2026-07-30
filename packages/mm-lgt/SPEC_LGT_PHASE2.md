# LGT Phase 2 Technical Specification

## Status

MM-LGT is a research implementation of force-field attention. It is designed
to make the hypothesis falsifiable with code and benchmarks, not to rename
ordinary attention with physics language.

## Core operator

For head \(h\), query token \(i\), and key token \(j\):

\[
F_{hij} =
\frac{G_h m_{hi}m_{hj}}
{\lVert p_{hi}-p_{hj}\rVert^2 +
\alpha\lVert \hat q_{hi}-\hat k_{hj}\rVert^2 + s_h^2 + \epsilon}
\]

where:

- \(G_h>0\) is a learned head-specific field strength;
- \(m_{hi},m_{hj}>0\) are learned token masses;
- \(p\) is a projected deterministic multi-scale positional coordinate;
- \(\alpha\) controls content displacement;
- \(s_h>0\) is learned gravitational softening;
- \(\epsilon\) is numerical protection.

Attention logits are:

\[
L_{hij} = \log(1 + F_{hij}) +
\beta_h\frac{q_{hi}\cdot k_{hj}}{\sqrt{d_h}}
\text{bias}_{hij}
\text{mask}_{ij}
\]

`log1p` is intentional. With `log(F)`, the query mass and per-head gravity
become additive constants across keys and mostly cancel under softmax.
`log1p(F)` preserves a nonlinear, trainable effect while limiting extreme
forces. Learned softening prevents self-distance from producing singular
self-attention.

## Multi-scale positions

The position generator combines:

- normalized forward and reverse position;
- sine/cosine bands spaced by powers of the golden ratio;
- recursive triangular folding.

"Fractal" here means deterministic multi-scale self-similar features. It does
not claim a literal physical spacetime or quantum process.

## Telemetry contract

Every block returns bounded, detached diagnostics:

```json
{
  "mean_mass": 0.71,
  "mean_force": 0.64,
  "max_force": 4.82,
  "mean_attention_entropy": 2.31,
  "gravity_constants": [0.69, 0.71, 0.68, 0.70],
  "softening_constants": [0.69, 0.69, 0.70, 0.68]
}
```

Telemetry is observational and is never reused as hidden reasoning.

## Memory contract

The memory store uses SQLite with WAL mode and schema migrations. Every record
separates content from evidence metadata:

- kind;
- source and source quality;
- timestamp;
- importance;
- confidence;
- embedding model and vector;
- tags and relation IDs;
- supersession link;
- tombstone timestamp.

Retrieval combines non-negative cosine similarity, effective memory mass,
source quality, and exponential recency decay. Returned results expose the
component scores and a compact `why_recalled` explanation. Tombstoned records
are excluded and cannot be resurrected by retrieval.

## Complexity

Like standard dense attention:

- time: \(O(BHT^2d_h)\);
- attention memory: \(O(BHT^2)\).

This implementation targets correctness and measurement, not long-context
efficiency. Sparse or hierarchical routing belongs in a later measured phase.

## Acceptance tests

1. Configuration rejects invalid dimensions and unsafe ranges.
2. Positions are deterministic and finite.
3. Attention returns the expected shape without NaNs.
4. Causal outputs do not depend on future tokens.
5. Gravity, mass, and softening parameters receive gradients.
6. A small deterministic corpus can reduce next-token loss.
7. Memory survives store restart.
8. Retrieval exposes score components and prioritizes relevant, important,
   confident memories.
9. Selective deletion tombstones a record.
10. Export omits tombstones by default.
11. SQLite integrity check passes.

## Benchmark gate for Phase 3

Do not claim an improvement over `torch.nn.MultiheadAttention` until both
operators are compared with matched parameter counts and seeds on:

- validation loss;
- long-range associative recall;
- context perturbation stability;
- wall-clock latency;
- peak resident memory;
- gradient stability;
- ablations for mass, geometry, gravity, softening, and content mixing.

