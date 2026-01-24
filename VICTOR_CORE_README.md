# Victor AGI Core - Production-Grade Foundation

A unified, production-grade foundation for the Victor AGI system with comprehensive tensor operations, trust framework, and cognitive modules.

## 🚀 Features

### 🧮 Tensor & Autograd Engine
- **Complete automatic differentiation** with topological sort
- **Broadcasting support** with proper gradient reduction
- **Standard operations**: add, mul, matmul, sum, mean, reshape, transpose
- **Activation functions**: ReLU, Sigmoid, Tanh, Softmax
- **Loss functions**: MSE, Binary Cross-Entropy, Cross-Entropy
- **Optimizers**: SGD (with momentum), Adam, RMSprop
- **Save/load functionality** for model checkpoints
- **Zero dependencies** except NumPy

### 🔐 SAVE3 Trust Framework
- **TrustModelBeta**: Time-decay and latency-weighted trust scoring
- **SAVE3Envelope**: Secure message envelopes with HMAC-SHA256 signatures
- **LegoContext**: Service registry and dependency injection
- **Module discovery**: Automatic scanning and compatibility checking
- **Dependency resolution**: Topological sort with cycle detection
- **Lego build orchestration**: Initialize modules in correct order

### 🧠 Cognitive Modules
- Placeholder for future cognitive architectures
- Integration hooks ready for reasoning systems
- Meta-cognitive loop support (coming in Phase 2)

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/MASSIVEMAGNETICS/tooki.git
cd tooki

# Install dependencies (only NumPy required for core functionality)
pip install numpy

# Optional: Install development dependencies for testing
pip install pytest pytest-cov
```

## 🏗️ Project Structure

```
tooki/
├── victor_core/              # Core package
│   ├── __init__.py           # Package initialization
│   ├── tensor/               # Tensor & autograd engine
│   │   ├── __init__.py
│   │   └── engine.py         # Complete tensor implementation
│   ├── trust/                # SAVE3 trust framework
│   │   ├── __init__.py
│   │   └── save3.py          # Trust model & orchestration
│   ├── cognitive/            # Cognitive modules (Phase 2)
│   │   └── __init__.py
│   └── utils.py              # Utilities (logging, config, etc.)
├── tests/                    # Comprehensive test suite
│   ├── conftest.py           # Pytest fixtures
│   ├── test_tensor.py        # Tensor engine tests (40 tests)
│   └── test_trust.py         # Trust framework tests (40 tests)
├── examples/                 # Usage examples
│   ├── tensor_basics.py      # Basic tensor operations
│   ├── neural_network.py     # Neural network training
│   └── save3_framework.py    # Trust framework demo
├── docs/                     # Documentation (Sphinx)
└── README.md                 # This file
```

## 🎯 Quick Start

### Tensor Operations

```python
from victor_core.tensor import Tensor, relu, Adam

# Create tensors
x = Tensor([[1.0, 2.0], [3.0, 4.0]], requires_grad=True)
y = Tensor([[2.0], [3.0]], requires_grad=True)

# Operations
z = relu(x @ y)
loss = z.mean()

# Backpropagation
loss.backward()
print(x.grad)  # Gradients computed!

# Training with optimizer
optimizer = Adam([x, y], lr=0.01)
optimizer.step()
optimizer.zero_grad()
```

### SAVE3 Trust Framework

```python
from victor_core.trust import TrustModelBeta, SAVE3Envelope, lego_build

# Trust scoring
trust = TrustModelBeta()
trust.record_success("service_a", score_gain=10, latency_ms=50)
score = trust.get_trust("service_a")  # Returns trust score

# Secure envelopes
envelope = SAVE3Envelope(
    module_id="my.module",
    module_name="My Module",
    module_version="v1.0.0",
    payload={"config": {"timeout": 30}}
)
envelope.finalize(secret=b"shared_secret")
envelope.verify(secret=b"shared_secret")  # Cryptographic verification

# Module orchestration
result = lego_build("/path/to/modules")
print(result["capabilities_published"])
```

## 📚 Examples

Run the included examples to see the system in action:

```bash
# Set Python path
export PYTHONPATH=/path/to/tooki:$PYTHONPATH

# Basic tensor operations
python3 examples/tensor_basics.py

# Train a neural network
python3 examples/neural_network.py

# SAVE3 trust framework
python3 examples/save3_framework.py
```

## 🧪 Testing

The project includes a comprehensive test suite with 80+ tests covering all functionality:

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=victor_core --cov-report=html

# Run specific test file
pytest tests/test_tensor.py -v
```

### Test Coverage

- **Tensor Engine**: 40 tests covering operations, gradients, optimizers, save/load
- **Trust Framework**: 40 tests covering trust scoring, envelopes, dependency resolution
- **Current Status**: ✅ 80/80 tests passing

## 🔧 Key Components

### Tensor Class

The `Tensor` class is the foundation of the autograd engine:

```python
class Tensor:
    """N-dimensional array with automatic differentiation."""
    
    def __init__(self, data, requires_grad=False, dtype=np.float32)
    def backward(self, gradient=None, retain_graph=False)
    def detach(self) -> Tensor
    
    # Operations: +, -, *, /, **, @, sum, mean, reshape, transpose, ...
```

### SAVE3Envelope

Secure message wrapper with cryptographic signatures:

```python
@dataclass
class SAVE3Envelope:
    """Secure message envelope with HMAC-SHA256 signatures."""
    
    def finalize(self, secret: Optional[bytes] = None) -> SAVE3Envelope
    def verify(self, secret: Optional[bytes] = None) -> None
```

### TrustModelBeta

Time-decay and latency-weighted trust scoring:

```python
class TrustModelBeta:
    """Trust scoring with time decay and latency penalties."""
    
    def record_success(self, entity_id, score_gain=5.0, latency_ms=0.0) -> float
    def record_failure(self, entity_id, score_penalty=10.0) -> float
    def get_trust(self, entity_id) -> float
```

## 📖 Documentation

- **API Reference**: See docstrings in code (Sphinx docs coming in Phase 2)
- **Architecture Guide**: `docs/architecture.md` (coming soon)
- **Tutorials**: Example scripts in `examples/`

## 🛠️ Development

### Code Style

- **PEP 8** compliant
- **Type hints** for all public APIs
- **Comprehensive docstrings** with examples
- **No external dependencies** (except NumPy)

### Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass: `pytest tests/ -v`
5. Submit a pull request

## 🗺️ Roadmap

### ✅ Phase 1: Foundation (Current)
- [x] Unified tensor/autograd engine
- [x] SAVE3 trust framework
- [x] Comprehensive test suite (80+ tests)
- [x] Example scripts
- [x] Basic utilities

### 🚧 Phase 2: Advanced Features (Next)
- [ ] Sphinx documentation
- [ ] Cognitive module implementations
- [ ] GPU acceleration support
- [ ] Extended optimizer library
- [ ] Model zoo and pre-trained models

### 🔮 Phase 3: Production (Future)
- [ ] Distributed training
- [ ] Model serving infrastructure
- [ ] Advanced cognitive architectures
- [ ] Integration with external systems

## 📊 Performance

The tensor engine is designed for **correctness and clarity** over premature optimization:

- Pure NumPy backend for portability
- Efficient gradient computation via topological sort
- Minimal memory overhead
- Future: GPU acceleration planned for Phase 2

## 🔒 Security

- **HMAC-SHA256** signatures for message integrity
- **Time-decay trust** prevents stale scores
- **Dependency resolution** prevents circular dependencies
- **No external network calls** in core functionality

## 📄 License

Proprietary - Massive Magnetics / Ethica AI / BHeard Network

**Author**: Brandon "iambandobandz" Emery x Victor  
**Version**: 1.0.0  
**Status**: Production-Ready Phase 1

## 🙏 Acknowledgments

This codebase consolidates best practices from multiple tensor implementations:
- `tensor_autograd_engine.py`
- `victorch_core_tensor.py`
- `victorch_core_autograd_Version2.py`
- Qwen implementations
- OmegaTensor patterns

Special thanks to all contributors and collaborators.

---

**Last Updated**: January 2026  
**Repository**: https://github.com/MASSIVEMAGNETICS/tooki
