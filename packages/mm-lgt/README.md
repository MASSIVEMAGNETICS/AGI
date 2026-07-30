# MM-LGT: Learned Gravitational Transformer

MM-LGT is an experimental, CPU-runnable attention and memory package for the
Massive Magnetics / Victor monorepo. It turns the original LGT Phase 2 concept
into executable software:

- learned positive token mass;
- learned per-head gravitational strength and softening;
- deterministic multi-scale ("fractal") positional geometry;
- content-aware force-field attention;
- bounded telemetry for Victor diagnostics;
- transactional SQLite memory with provenance, confidence, tombstones,
  export, and integrity checks;
- a deterministic toy training loop and automated tests.

This is an experimental inductive bias, not evidence of AGI, consciousness, or
superiority to standard attention. The included demo proves that the operator
is differentiable, trainable, persistent, and inspectable. Comparative quality
claims require the benchmark plan in `SPEC_LGT_PHASE2.md`.

## Windows quick start

Double-click:

```text
run_lgt_demo.bat
```

The launcher creates `.venv`, installs the package, runs tests, and starts the
CPU demo. The first install downloads PyTorch and can take several minutes.

## Manual install

```bash
cd packages/mm-lgt
python -m venv .venv
```

Windows:

```powershell
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m pytest -q
python run_lgt_demo.py --steps 40
```

Linux/macOS:

```bash
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m pytest -q
python run_lgt_demo.py --steps 40
```

## Python API

```python
from bando_lgt import LGTLanguageModel, ModelConfig

config = ModelConfig(
    vocab_size=256,
    d_model=96,
    n_heads=4,
    n_layers=2,
    max_seq_len=128,
)
model = LGTLanguageModel(config)
```

Persistent memory:

```python
from bando_lgt import GravitationalMemoryStore, MemoryRecord

store = GravitationalMemoryStore("data/lgt_memory.sqlite3")
record_id = store.add(
    MemoryRecord(
        content="Victor preserves verified continuity across model replacement.",
        vector=[1.0, 0.0, 0.0],
        kind="semantic",
        importance=0.95,
        confidence=0.90,
        source="user-confirmed",
        tags=["victor", "continuity"],
    )
)

results = store.retrieve([1.0, 0.0, 0.0], top_k=5)
for result in results:
    print(result.score, result.record.content, result.why_recalled)
```

## Hardware profile

The default demo is deliberately small for Brandon's CPU-only Windows laptop:

- Python 3.11+;
- one process and one training loop;
- `d_model=64`, four heads, two blocks;
- 64-token context;
- SQLite WAL persistence;
- no cloud service and no listening network port.

LGT attention remains quadratic in context length. Keep context at or below 256
tokens on older dual-core laptop CPUs until measured benchmarks justify more.

## Repository layout

```text
packages/mm-lgt/
├── bando_lgt/
│   ├── interfaces.py
│   ├── fractal_positions.py
│   ├── lgt_attention.py
│   ├── memory.py
│   ├── model.py
│   └── training.py
├── tests/
├── INTEGRATION.md
├── SPEC_LGT_PHASE2.md
├── pyproject.toml
├── run_lgt_demo.bat
└── run_lgt_demo.py
```

## Validation

```bash
python -m compileall -q bando_lgt run_lgt_demo.py
python -m pytest -q
python run_lgt_demo.py --steps 12 --no-sample
```

