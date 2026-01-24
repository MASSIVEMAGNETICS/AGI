# Victor Monolith v3.2.2 - API Reference

## Configuration

### Config Class

Global configuration accessible via `config` object.

```python
class Config:
    # Core dimensions
    DIM: int = 64                    # Latent dimension
    LR: float = 1e-4                 # Learning rate
    STEPS: int = 20                  # Training steps
    ANCHOR_STR: str = "Bando Empire Architect"  # Identity anchor
    
    # Transformer/MoE config
    RFT_D_MODEL: int = 64           # Model dimension
    RFT_NUM_LAYERS: int = 1         # Number of layers
    RFT_NUM_HEADS: int = 4          # Attention heads
    RFT_NUM_EXPERTS: int = 2        # MoE experts
    RFT_D_FF: int = 256             # FFN dimension
    
    # Generation config
    TOKENIZER_NAME: str = "gpt2"    # Tokenizer
    MAX_SEQ_LEN: int = 50           # Max sequence length
    MAX_NEW_TOKENS: int = 15        # Tokens to generate
    
    # Memory config
    EMBED_DIM: int = 384            # Embedding dimension
    
    # System
    DEVICE: str = "cuda" or "cpu"   # Compute device
    CHECKPOINT_DIR: str = "./victor_checkpoints"
```

## Core Classes

### NeuralMesh3D

Hierarchical predictive coding mesh.

```python
class NeuralMesh3D:
    def __init__(self, layer_dims: List[int], lr: float = 0.01, num_iterations: int = 10)
    def infer(self, sensory_input: torch.Tensor) -> List[torch.Tensor]
    def parameters(self) -> list
```

**Methods**:
- `infer(sensory_input)`: Run predictive coding inference
  - Input: `[1, first_dim]` tensor
  - Output: List of inferred hidden states per layer
  - Iterates until convergence or max iterations

### ConsciousnessLoop

Model predictive control for action selection.

```python
class ConsciousnessLoop:
    def __init__(self, dim: int, lr: float, anchor_str: str)
    def step(self, o_t_scalar: float) -> Dict[str, Any]
```

**Methods**:
- `step(o_t_scalar)`: Execute one MPC planning step
  - Input: Observation as scalar
  - Output: `{'action': float, 'metrics': {...}}`
  - Samples plans, rolls out futures, selects best action

### FractalSoulCore

Recursive identity and self-reflection.

```python
class FractalSoulCore:
    def __init__(self, creator_name: str = "Bando Bandz")
    def recursive_thought(self, input_text: str, depth: int = 3) -> List[str]
    def check_identity_integrity(self) -> Tuple[bool, str]
```

**Methods**:
- `recursive_thought(input_text, depth)`: Generate thought trace
  - Input: Text prompt
  - Output: List of reflections at each depth level
  
- `check_identity_integrity()`: Verify identity hasn't drifted
  - Output: `(is_valid, message)`

### IdentitySoulManager

Manage directives and beliefs.

```python
class IdentitySoulManager:
    def __init__(self, core_identity: str, initial_directives: Optional[List[Dict]])
    async def add_directive(self, goal: str, priority: float, type_tag: str)
    async def assert_belief(self, statement: str, confidence: float, ...)
    async def get_top_beliefs(self, top_n: int = 5) -> List[Tuple[str, float]]
```

**Methods**:
- `add_directive(goal, priority, type_tag)`: Add new directive
- `assert_belief(statement, confidence, ...)`: Add or reinforce belief
- `get_top_beliefs(top_n)`: Get highest confidence beliefs

### HyperFractalMemory

Long-term semantic memory.

```python
class HyperFractalMemory:
    def __init__(self, dim: int = 384)
    def add_memory(self, embed: np.ndarray, summary: str, refs: Any)
    def search(self, query_embed: np.ndarray, k: int = 3)
    def get_summaries_for_indices(self, I) -> List[str]
    def close(self)
```

**Methods**:
- `add_memory(embed, summary, refs)`: Store memory
  - Input: 384-dim embedding, text summary, metadata
  
- `search(query_embed, k)`: Find similar memories
  - Input: Query embedding
  - Output: `(distances, indices)`
  
- `get_summaries_for_indices(I)`: Map FAISS indices to text
  - Input: Index array from search
  - Output: List of summary strings

### TinyMoETransformerDecoder

Mixture of experts transformer decoder.

```python
class TinyMoETransformerDecoder(nn.Module):
    def __init__(self, vocab_size, d_model, n_heads, n_experts, d_ff, max_seq_len)
    def forward(self, tokens: torch.Tensor) -> torch.Tensor
    def generate(self, tokens: torch.Tensor, max_new_tokens: int, max_seq_len: int)
```

**Methods**:
- `forward(tokens)`: Compute logits
  - Input: `[B, T]` token IDs
  - Output: `[B, T, vocab_size]` logits
  
- `generate(tokens, max_new_tokens, max_seq_len)`: Autoregressive decode
  - Input: `[1, T0]` prompt tokens
  - Output: `[1, T0 + max_new_tokens]` completed sequence

### SpeechCoreMoE

RAG-aware generation interface.

```python
class SpeechCoreMoE:
    def __init__(self)
    def generate(self, core_reflection: str, memory_context: str) -> str
```

**Methods**:
- `generate(core_reflection, memory_context)`: Generate response
  - Input: Current thought + retrieved memory context
  - Output: Generated text string

### VictorMonolith

Main system orchestrator.

```python
class VictorMonolith:
    def __init__(self)
    async def start(self)
    async def stop(self)
    async def unified_step(self, current_prompt: str) -> Tuple[Dict, str, str]
```

**Methods**:
- `start()`: Initialize background tasks
- `stop()`: Shutdown and save state
- `unified_step(current_prompt)`: Execute one cognitive cycle
  - Input: Text prompt
  - Output: `(metrics, reflection, generated_output)`

## Helper Functions

### anchor_embed

```python
def anchor_embed(anchor_str: str, dim: int) -> torch.Tensor
```

Generate deterministic identity anchor from string.

### sample_plans

```python
def sample_plans(o_t, z_t, policy_net, num_plans=10, plan_len=5) -> torch.Tensor
```

Sample candidate action sequences from policy.

### rollout

```python
def rollout(predictor, o_t, z_t, plan, H=5)
```

Predict trajectory for given action plan.

### utility

```python
def utility(traj_r: List[float], discount: float = 0.9) -> float
```

Compute discounted return from reward trajectory.

## Event Bus

### FractalPulseExchange

```python
class FractalPulseExchange:
    def subscribe(self, topic: str, callback)
    async def publish(self, topic: str, data: dict, origin: str)
    def start_bus(self)
    def stop_bus(self)
```

**Usage**:
```python
# Subscribe
async def on_directive_shift(pulse):
    print(f"New directive: {pulse.data['new_directive']}")

bus.subscribe("identity.directive_shift", on_directive_shift)

# Publish
await bus.publish("custom.event", {"key": "value"}, "MyComponent")
```

## Environment Variables

Configure via environment:

```bash
export VICTOR_DIM=64
export VICTOR_LR=1e-4
export VICTOR_STEPS=20
export VICTOR_ANCHOR="Bando Empire Architect"
export VICTOR_CKPT_DIR="./victor_checkpoints"
export RFT_D_MODEL=64
export RFT_NUM_EXPERTS=2
export RFT_TOKENIZER="gpt2"
```

## Example Usage

### Basic Execution

```python
import asyncio
from victor_monolith_v3_2_2 import VictorMonolith

async def main():
    victor = VictorMonolith()
    await victor.start()
    
    # Let it run
    await victor._background_task
    
    await victor.stop()

asyncio.run(main())
```

### Custom Configuration

```python
import os
os.environ['VICTOR_DIM'] = '128'
os.environ['VICTOR_STEPS'] = '50'

# Then import and run
```

### Manual Step Execution

```python
victor = VictorMonolith()
await victor.start()

prompt = "What is the nature of consciousness?"
metrics, reflection, output = await victor.unified_step(prompt)

print(f"Reflection: {reflection}")
print(f"Generated: {output}")
print(f"Metrics: {metrics}")

await victor.stop()
```

## File Outputs

### Checkpoints

- `victor_checkpoints/cons_loop_state.pt`: Consciousness loop state
- `victor_checkpoints/meta_state.json`: Runtime metadata

### Logs

- `victor_monolith.log`: Detailed execution log

### Databases

- `victor_memory.db`: SQLite memory storage

---

**Last Updated**: 2026-01-24  
**Version**: v3.2.2-RETRIEVAL-MoE-PC-HIER
