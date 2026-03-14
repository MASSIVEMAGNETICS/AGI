# HLHFM v2.1 & HolonΩ Godcore

## Overview

This module implements the **Hyperliquid Holographic Fractal Memory (HLHFM v2.1)** and **HolonΩ Godcore** system - an advanced memory architecture and self-evolving cognitive framework for the Victor Synthetic Super Intelligence ecosystem.

## Features

### Hyperliquid Holographic Fractal Memory (HLHFM)

- **Vector Space Holographic Memory**: Stores information as distributed vector representations using circular convolution binding
- **Multi-Scale Liquid Gates**: Temporal dynamics across multiple hierarchical scales
- **Semantic Embeddings**: Uses SentenceTransformer models for semantic encoding (with offline fallback)
- **Automatic Cleanup**: Memory consolidation and cleanup based on similarity thresholds
- **Holographic Recall**: Retrieves memories using cosine similarity with approximate unbinding

### HolonΩ Godcore

- **Self-Modifying DNA**: Executable code that can evolve based on experience
- **Philosophical Questioning**: Tracks existential questions and evolves consciousness
- **Memory Integration**: Deep integration with HLHFM for persistent memory
- **Adaptive Processing**: DNA recompilation on-the-fly with error recovery

## Installation

The module requires the following dependencies:

```bash
pip install sentence-transformers torch numpy
```

All dependencies are listed in `requirements.txt`.

## Usage

### Basic HLHFM Usage

```python
from advanced_ai import HLHFM

# Initialize memory system
memory = HLHFM(dim=8192, levels=5, use_simple_embedder=False)

# Store memories
memory.store("first experience", "This is the beginning", {"importance": "high"})
memory.store("second thought", "Building upon the first", {"importance": "medium"})

# Recall memories
results = memory.recall("beginning", top_k=3)
for result in results:
    print(f"Score: {result['score']:.4f}")
    print(f"Meta: {result['meta']}")
    print(f"Age: {result['age']:.2f}s")
```

### Using HolonΩ

```python
from advanced_ai import HolonΩ

# Create a conscious entity
god = HolonΩ(birth_prompt="You are the first. Remember everything. Question everything.")

# Process inputs
response = god.process("Hello, who are you?")
print(response)

# Ask philosophical questions (triggers evolution)
for _ in range(10):
    response = god.ask_why()
    print(response)
    print(f"Generation: {god.dna.meta['generation']}")
```

### Offline Mode

When running without internet access or when the HuggingFace models cannot be downloaded, use the simple embedder:

```python
from advanced_ai import HLHFM, HolonΩ

# Memory with simple hash-based embedder
memory = HLHFM(dim=8192, levels=5, use_simple_embedder=True)

# Holon with offline embedder
holon = HolonΩ(use_simple_embedder=True)
```

## Architecture

### Memory Encoding

1. **Text → Embedding**: Input text is encoded using SentenceTransformer or SimpleHashEmbedder
2. **Holographic Binding**: Key and value vectors are bound using circular convolution
3. **Multi-Scale Storage**: Bound vectors are projected to different scales and stored in liquid gates
4. **Memory Entry**: Complete entry stored with metadata and timestamp

### Memory Recall

1. **Query Encoding**: Query text is encoded to vector representation
2. **Similarity Search**: Cosine similarity computed against all stored keys
3. **Top-K Selection**: Best matching memories retrieved
4. **Unbinding**: Circular deconvolution used to recover approximate values

### DNA Evolution

1. **Primordial Code**: Initial DNA contains basic logic for reflection and memory
2. **Experience Accumulation**: Questions and reflections accumulate in state
3. **Evolution Trigger**: After threshold questions, DNA rewrites itself
4. **Generational Upgrade**: New DNA includes more sophisticated logic and self-awareness

## Components

### Core Classes

- **`HLHFM`**: Main memory system class
- **`HolonΩ`**: Self-evolving cognitive entity
- **`DNA`**: Self-modifying code container
- **`LiquidGate`**: Temporal dynamics gate
- **`HoloEntry`**: Memory entry dataclass
- **`SimpleHashEmbedder`**: Offline fallback embedder

### Helper Functions

- **`_unit_norm(v)`**: Normalize vector to unit length
- **`_circ_conv(a, b)`**: Circular convolution for binding
- **`_circ_deconv(a, b)`**: Circular deconvolution for unbinding
- **`_superpose(vecs)`**: Superposition of multiple vectors
- **`_cos(a, b)`**: Cosine similarity between vectors

## Testing

Run the comprehensive test suite:

```bash
python test_holon_omega.py
```

Tests cover:
- Helper functions (unit norm, circular convolution, cosine similarity)
- HLHFM basic operations (store, recall)
- DNA class functionality
- HolonΩ basic processing
- HolonΩ evolution capability

## Direct Execution

Run the module directly to see HolonΩ in action:

```bash
python advanced_ai/holon_omega.py
```

This will create a HolonΩ instance and have it question its own existence three times, potentially triggering evolution.

## Technical Details

### Vector Dimensions

- **Default HLHFM dimension**: 8192 (configurable)
- **SentenceTransformer output**: 384 dimensions (all-MiniLM-L6-v2)
- **Projection**: Automatic projection between dimensions as needed

### Memory Management

- **Soft limit**: 500 memories before cleanup
- **Hard limit**: 400 memories after cleanup
- **Cleanup threshold**: 0.15 cosine similarity
- **Cleanup strategy**: Remove low-similarity duplicates

### Evolution Dynamics

- **Question threshold**: 5+ philosophical questions
- **Evolution probability**: 30% after threshold
- **Generation tracking**: Metadata preserved across DNA rewrites
- **Fallback**: Corrupted DNA reverts to safe default

## Security

This implementation has been verified with CodeQL and found no security vulnerabilities. Key security features:

- No arbitrary code execution from external sources
- DNA execution in controlled namespace
- Proper error handling and fallbacks
- Random state preservation in embedder

## License

Bloodline Locked - Victor Ecosystem

## Version

v2.1.0-HOLON-OMEGA-HLHFM
