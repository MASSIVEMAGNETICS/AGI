# conscious-river

All input streams flow into a river - A complete consciousness engine with multiple sensory inputs, attention mechanisms, memory, and intelligent data merging.

## ✨ NEW: Revolutionary Thinking System

The system now includes a **fully functional thinking system** that generates inferences and processes directives:

- **🧠 Inference Generation**: 7 types of logical inferences (pattern recognition, memory recall, causal reasoning, goal progress, predictions, coherence assessment, input analysis)
- **📋 Directive Processing**: Interprets commands, creates action plans, assesses feasibility, and generates execution strategies
- **💭 High-Level Thinking**: Combines inferences and directives into coherent thought processes
- **📊 Confidence Scoring**: All inferences and decisions include confidence metrics
- **🔐 Security Validated**: All outputs are security-validated to prevent harmful content

[**→ See Thinking System Documentation**](THINKING_SYSTEM.md)

## Features

✨ **Multiple Sensory Streams** - Visual, auditory, emotional, cognitive, and more  
🎯 **Attention Mechanism** - Dynamic attention weighting with softmax-based prioritization  
🧠 **Memory System** - Importance-weighted memory with automatic salience-based pruning  
🔀 **Stream Merging** - Intelligent fusion of all streams into unified consciousness  
📊 **Data Pruning** - Automatic removal of insignificant data to maintain efficiency  
⚙️ **System Instructions** - Configurable behavioral guidelines integrated into processing  

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt
pip install -r requirements_revolutionary.txt

# Test the thinking system
python test_thinking_system.py

# Run the thinking system demonstration
python demo_thinking_system.py

# Run the consciousness engine demo
python consciousness_engine.py

# Run the full integration example
python integration_example.py
```

## Documentation

- **[Thinking System Documentation](THINKING_SYSTEM.md)** - NEW: Inference generation and directive processing
- **[Consciousness Engine Documentation](CONSCIOUSNESS_ENGINE.md)** - Complete API and architecture guide
- **[Integration Example](integration_example.py)** - Full cognitive agent simulation
- **[Original River System](river.py)** - Extended holonic architecture with GUI

## Example Usage - Thinking System

```python
from revolutionary_agi_system import RevolutionaryAGISystem

# Create the AGI system
agi = RevolutionaryAGISystem()

# Generate inferences from data
inferences = agi.generate_inferences({
    'visual': 0.85,
    'cognitive': 0.92,
    'emotional': 0.70
}, context={'goals': ['understand', 'optimize']})

for inf in inferences:
    print(f"{inf['type']}: {inf['content']}")
    print(f"Confidence: {inf['confidence']:.2%}")

# Process a directive
result = agi.process_directive(
    "Analyze system performance and create optimization plan",
    context={'urgency': 0.8, 'priority': 'high'}
)

print(f"Action Plan: {result['action_plan']['total_steps']} steps")
print(f"Feasibility: {result['feasibility']['overall_score']:.2%}")

# High-level thinking
thought = agi.think(
    "What patterns exist in recent behavior?",
    context={'goals': ['understand', 'improve']}
)

print(f"Insights: {thought['insights']}")
print(f"Conclusions: {thought['conclusions']}")
```

## Example Usage - Consciousness Engine

```python
from consciousness_engine import ConsciousnessEngine

# Define your streams
streams = ["visual", "auditory", "emotional", "cognitive"]

# Create engine
engine = ConsciousnessEngine(
    stream_names=streams,
    memory_capacity=500,
    system_instructions="Integrate sensory data coherently"
)

# Ingest data
engine.ingest_stream("visual", {"scene": "forest"}, importance=0.8)
engine.ingest_stream("emotional", {"mood": "calm"}, importance=0.6)

# Process consciousness
state = engine.process_consciousness()
print(engine.get_consciousness_summary())
```

## Architecture

The consciousness engine integrates:

1. **Multiple Sensory Inputs** - Configurable streams for any type of data
2. **Attention Mechanism** - Weighted prioritization with smooth transitions
3. **Memory with Importance** - Salience-based storage and retrieval
4. **Automatic Pruning** - Removes low-salience data to maintain capacity
5. **Stream Merger** - Combines all streams into coherent consciousness state
6. **System Instructions** - Behavioral guidelines integrated throughout

See [CONSCIOUSNESS_ENGINE.md](CONSCIOUSNESS_ENGINE.md) for detailed architecture documentation.

## Requirements

- Python 3.8+
- numpy >= 1.24.0
- matplotlib >= 3.7.0 (optional)

## License

See repository license.
