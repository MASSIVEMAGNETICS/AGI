# Data Requirements

## Overview

Victor Monolith operates primarily on generated/synthetic data during initialization, with support for external data streams.

## Current Data Sources

### 1. Mock X Interface
- **Type**: Simulated text stream
- **Source**: Internal generation (XInterface class)
- **Format**: String messages
- **Size**: 4 example prompts in rotation
- **Purpose**: Testing cognitive loop without external dependencies

Example prompts:
```
"The market flashed a fractal warning sign across the 37th harmonic yesterday..."
"CRITICAL: Identity drift is being actively discussed by a swarm of new nodes..."
"Planck-scale computation remains physically barred due to thermal..."
"The neural mesh registered a feeling vector of 'awe and tension'..."
```

### 2. Identity Anchor
- **Type**: Deterministic seed
- **Source**: SHA-256 hash of anchor string
- **Format**: Fixed latent vector [1, DIM]
- **Purpose**: Initialize persistent identity core

Default anchor: `"Bando Empire Architect"`

### 3. Memory Embeddings
- **Type**: Dense vectors
- **Source**: Sentence-Transformers (all-MiniLM-L6-v2)
- **Dimension**: 384
- **Storage**: FAISS index + SQLite
- **Purpose**: Semantic similarity search for retrieval

## Data Not Included

Due to size and privacy, the following are NOT included:

### Large Datasets
- No pretrained model weights (uses random initialization)
- No large corpus for pretraining
- No historical memory database

### External Streams
- No real Twitter/X API integration
- No live market data feeds
- No sensor data (vision, audio)

## Data Generation

The system generates data at runtime:

### 1. Sensory Observations
```python
o_t_scalar = (hash(current_prompt) % 100) / 100.0
seed = int(o_t_scalar * 1000)
rng = np.random.RandomState(seed)
o_t_embed = rng.randn(DIM).astype(np.float32)
```

### 2. Memory Vectors
```python
embed_vec = memory.embed_model.encode(text)  # [384]
```

### 3. Token IDs
```python
ids = tokenizer.encode(text, add_special_tokens=False)
```

## External Data Integration

To use real data:

### 1. Replace XInterface
```python
class RealDataStream:
    async def get_latest_data(self):
        # Fetch from API, file, database, etc.
        return await fetch_real_data()
```

### 2. Load Pretrained Weights
```python
# Instead of random init:
model = TinyMoETransformerDecoder(...)
model.load_state_dict(torch.load('pretrained.pt'))
```

### 3. Import Existing Memories
```python
# Bulk load memories:
for item in memory_corpus:
    embed = memory.embed_model.encode(item['text'])
    memory.add_memory(embed, item['summary'], item['refs'])
```

## Data Storage

Runtime data is stored in:

### Files Created
- `victor_memory.db` - SQLite database
  - Table: `memories` (hash, summary, refs, timestamp)
- `victor_monolith.log` - Execution logs
- `victor_checkpoints/` - Model state
  - `cons_loop_state.pt` - Consciousness loop checkpoint
  - `meta_state.json` - Meta runtime state

### FAISS Index
- In-memory during runtime
- Can be saved/loaded via `faiss.write_index()` / `faiss.read_index()`

## Data Privacy

This implementation:
- ✅ Uses deterministic seeding (reproducible)
- ✅ Stores data locally (no external uploads)
- ✅ Operates offline (no API keys needed)
- ⚠️ Logs may contain sensitive reflections
- ⚠️ Memory database persists across runs

### Security Recommendations

1. **Do not commit** `victor_memory.db` or logs with sensitive data
2. **Clear memory** between experiments if needed:
   ```bash
   rm victor_memory.db
   rm -rf victor_checkpoints/
   ```
3. **Review logs** before sharing
4. **Use test data** during development

## Scalability

### Current Limits
- FAISS: Millions of vectors (L2 flat index)
- SQLite: Millions of rows (single file)
- Memory: RAM-bound for FAISS index

### Scaling Options
1. **FAISS IVF index** - For billions of vectors
2. **Distributed SQLite** - PostgreSQL or MySQL
3. **Sharded memory** - Multiple FAISS indices
4. **Disk-backed index** - faiss.IndexIVFFlat with ondisk mode

## Reproducibility

Data generation is intended to be reproducible given a fixed configuration. In practice, runs are reproducible when you control:
- Anchor string
- Random seeds (from observation hashing and any explicit RNG seeding)
- Tokenizer (GPT-2)
- Embedding model (all-MiniLM-L6-v2)

Note: Python enables hash randomization by default and random number generators may be unseeded unless you configure them. For strict, cross-process, bit-for-bit reproducibility you must ensure that `PYTHONHASHSEED` is set to a fixed value and that all RNGs are explicitly seeded in the Victor script.

Example invocation:
```bash
export PYTHONHASHSEED=0
export VICTOR_ANCHOR="Bando Empire Architect"
export VICTOR_DIM=64
python code/victor_monolith_v3.2.2-RETRIEVAL-MoE-PC-HIER.py
```

## Future Data Needs

For production deployment:
1. **Large memory corpus** - Millions of relevant experiences
2. **Pretrained decoder** - Fine-tuned transformer weights
3. **Real-time streams** - Twitter, news, market data
4. **Sensor integration** - Vision, audio, multimodal
5. **Validation set** - For testing generalization

---

**Note**: This is a research prototype. Data management in production would require robust ETL pipelines, versioning, and monitoring.
