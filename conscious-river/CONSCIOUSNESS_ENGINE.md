# Consciousness Engine

A complete consciousness engine implementation with multiple sensory inputs, attention mechanisms, memory with importance weighting, data pruning, and stream merging.

## Overview

The Consciousness Engine integrates multiple sensory and cognitive streams into a unified consciousness state. It features:

- **Multiple Sensory Streams**: Support for any number of input streams (visual, auditory, emotional, cognitive, etc.)
- **Attention Mechanism**: Dynamic attention weighting using softmax with contextual modulation
- **Memory System**: Importance-weighted memory with salience-based retrieval and automatic pruning
- **Data Pruning**: Automatic removal of low-salience memories to maintain capacity
- **Stream Merging**: Weighted combination of all streams into a coherent consciousness state
- **System Instructions**: Configurable behavioral instructions integrated into processing

## Architecture

### Core Components

#### 1. StreamData
Represents data from a single sensory or cognitive stream:
- Stream name and content
- Timestamp
- Importance score (0.0 - 1.0)
- Novelty score
- Metadata and tags

#### 2. AttentionMechanism
Manages dynamic attention across streams:
- Softmax-based attention weights
- Context-aware modulation
- Smooth transitions using exponential moving average
- Top-k stream selection

#### 3. MemorySystem
Stores and manages memories with importance weighting:
- Capacity-limited storage
- Salience-based retrieval
- Automatic pruning of low-salience memories
- Duplicate detection and merging
- Tag-based retrieval

**Salience Calculation:**
```
salience = importance × time_decay + access_boost + recency_boost
```

#### 4. StreamMerger
Combines multiple streams into unified consciousness:
- Attention-weighted merging
- Coherence calculation
- Dominant stream identification
- Memory context integration

#### 5. ConsciousnessEngine
Main orchestrator that integrates all components:
- Stream ingestion
- Consciousness processing loop
- Energy and coherence tracking
- Statistics and monitoring

## Usage

### Basic Example

```python
from consciousness_engine import ConsciousnessEngine

# Define your streams
streams = ["visual", "auditory", "emotional", "cognitive", 
           "memory_recall", "intent", "body_state", "environment"]

# Create engine
engine = ConsciousnessEngine(
    stream_names=streams,
    memory_capacity=500,
    system_instructions="Integrate sensory data coherently"
)

# Ingest stream data
engine.ingest_stream(
    stream_name="visual",
    data={"objects": ["tree", "bird"], "brightness": 0.8},
    importance=0.7,
    metadata={"tags": ["nature", "outdoor"]}
)

engine.ingest_stream(
    stream_name="emotional",
    data={"mood": "calm", "valence": 0.8},
    importance=0.6
)

# Process consciousness
state = engine.process_consciousness()

# Get summary
print(engine.get_consciousness_summary())
```

### Advanced Example

See `integration_example.py` for a complete cognitive agent simulation with:
- Multiple scenarios
- Dynamic stream importance
- Memory retrieval
- Data pruning demonstration

## Key Features

### Attention Mechanism

The attention mechanism dynamically weights streams based on:
1. **Intrinsic importance**: The importance score of incoming data
2. **Context modulation**: Contextual factors that boost/reduce attention
3. **Smooth transitions**: EMA smoothing prevents rapid attention shifts

```python
# Get top attended streams
top_streams = engine.attention.get_top_k_streams(k=3)
for idx, weight in top_streams:
    print(f"{stream_names[idx]}: {weight:.3f}")
```

### Memory System

Memories are scored by **salience**, which combines:
- **Importance**: Initial importance score
- **Time decay**: Exponential decay over time
- **Access boost**: Frequently accessed memories stay relevant
- **Recency boost**: Recently accessed memories are boosted

```python
# Retrieve memories by tags
memories = engine.memory.retrieve_relevant(
    query_tags=["problem_solving", "cognitive"],
    k=5
)

# Get memory statistics
summary = engine.memory.get_memory_summary()
```

### Data Pruning

Automatic pruning removes low-salience memories when:
1. Memory capacity is exceeded
2. Periodic pruning cycles occur
3. Memories fall below the pruning threshold

Pruning ensures:
- Important memories are retained
- Recently accessed memories are protected
- Capacity constraints are maintained

### Stream Merging

All streams are merged into a unified consciousness state:

```python
consciousness_state = {
    "timestamp": <current_time>,
    "streams": {
        "stream_name": {
            "data": <stream_data>,
            "weight": <attention_weight>,
            "importance": <weighted_importance>
        },
        ...
    },
    "total_importance": <sum_of_weighted_importances>,
    "attention_distribution": [weights...],
    "dominant_streams": [top_stream_names...],
    "memory_context": {
        "relevant_memories": [...],
        "memory_summary": {...}
    },
    "coherence": <coherence_score>,
    "system_instructions": <instructions>,
    "statistics": {...}
}
```

### Coherence

Coherence measures how focused the consciousness is:
- **High coherence (0.7-1.0)**: Attention is concentrated on few streams
- **Medium coherence (0.4-0.7)**: Balanced attention distribution
- **Low coherence (0.0-0.4)**: Diffuse attention across many streams

## Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

Requirements:
- Python 3.8+
- numpy >= 1.24.0
- matplotlib >= 3.7.0 (optional, for visualization)

## Running Examples

```bash
# Basic demo
python consciousness_engine.py

# Full integration example
python integration_example.py

# Run existing river.py (with fixes)
python river.py
```

## API Reference

### ConsciousnessEngine

```python
ConsciousnessEngine(
    stream_names: List[str],
    memory_capacity: int = 1000,
    system_instructions: str = ""
)
```

**Methods:**

- `ingest_stream(stream_name, data, importance, metadata)`: Add stream data
- `process_consciousness()`: Process all streams and return unified state
- `get_consciousness_summary()`: Get human-readable summary
- `set_system_instructions(instructions)`: Update system instructions
- `adjust_energy(delta)`: Adjust consciousness energy level

### MemorySystem

```python
MemorySystem(capacity: int = 1000, prune_threshold: float = 0.1)
```

**Methods:**

- `add_memory(content, importance, tags)`: Store new memory
- `prune_memories()`: Remove low-salience memories
- `retrieve_relevant(query_tags, k)`: Retrieve k most relevant memories
- `get_memory_summary()`: Get memory system statistics

### AttentionMechanism

```python
AttentionMechanism(num_streams: int, attention_window: int = 10)
```

**Methods:**

- `update_attention(importances, context)`: Update attention weights
- `get_top_k_streams(k)`: Get top-k attended streams

## Design Principles

1. **Modularity**: Each component is independent and reusable
2. **Configurability**: All parameters can be tuned
3. **Efficiency**: Automatic pruning prevents unbounded growth
4. **Robustness**: Handles missing streams, duplicates, edge cases
5. **Transparency**: Full introspection of internal state

## Performance Considerations

- **Memory**: O(capacity) for memory storage
- **Attention**: O(num_streams) per update
- **Pruning**: O(n log n) where n = number of memories
- **Retrieval**: O(n) for tag-based search

For high-frequency applications:
- Reduce memory capacity
- Increase prune threshold
- Reduce attention window
- Use batch processing

## Integration with Existing Code

The consciousness engine integrates seamlessly with the existing `river.py` components:

- Compatible with `CognitiveRiver8` streams
- Can be used with `Holon` and `MetaHolon` architectures
- Works alongside `HybridMemorySystem` and other components

## Future Enhancements

Potential improvements:
- [ ] Neural attention mechanisms
- [ ] Hierarchical memory organization
- [ ] Predictive stream weighting
- [ ] Emotional modulation of attention
- [ ] Multi-agent consciousness networks
- [ ] Temporal sequence learning
- [ ] Causal reasoning integration

## License

See repository license.

## Authors

Built for the conscious-river project.
