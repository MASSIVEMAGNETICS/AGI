# Victor / AGI Integration

This PR adds a self-contained package and does not silently modify the imported
subtrees. That keeps the first merge reversible.

## Runtime import

From the monorepo root:

```bash
python -m pip install -e packages/mm-lgt
```

Then:

```python
from bando_lgt import LGTLanguageModel, ModelConfig
```

## Diagnostics bridge

`LGTLanguageModel.forward()` returns `(logits, loss, telemetry)`. Convert the
telemetry to a `CognitionPulse` for Victor's existing diagnostics boundary:

```python
from bando_lgt import CognitionPulse

pulse = CognitionPulse.from_telemetry(
    component="mm-lgt",
    telemetry=telemetry,
    correlation_id=current_correlation_id,
)
diagnostics.emit(pulse.as_dict())
```

The pulse contains metrics only. It does not expose or persist hidden
chain-of-thought.

## Memory bridge

Use `GravitationalMemoryStore` as an adapter-backed experimental store, not as
the sole Victor memory authority. Import verified records with their original
source, confidence, timestamp, and relation IDs. Never convert model-generated
reflections into observations.

Recommended data location on Windows:

```text
%LOCALAPPDATA%\MassiveMagnetics\Victor\data\lgt_memory.sqlite3
```

## Safe next integration

1. Add a feature flag such as `MM_LGT_ENABLED=0`.
2. Instantiate LGT only when the selected model checkpoint was trained with
   this operator.
3. Emit telemetry into the existing diagnostics stream.
4. Run shadow benchmarks beside the current attention implementation.
5. Promote only after measured quality, latency, and memory gates pass.

An LGT layer is not a drop-in replacement for a standard-attention checkpoint.
Weights must be trained or adapted for this architecture.

