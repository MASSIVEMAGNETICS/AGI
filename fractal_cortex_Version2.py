"""
FILE: fractal_cortex.py
VERSION: v1.0.1-FRACTAL-CORTEX-RUNNABLE
NAME: FractalCortex (runnable Vic-Torch + FractalStack reference)
AUTHOR: Copied/Adapted for MASSIVEMAGNETICS
PURPOSE: Runnable, self-contained single-file implementation of a
         small autograd (Vic-Torch style) and FractalStack transformer
         primitives. Designed for clarity, correctness, and small-toy
         execution. Pure numpy, no external dependencies.
LICENSE: Use at your own risk; adapted for demonstration and development.
"""

from __future__ import annotations
import math
import numpy as np
from typing import Any, Callable, Dict, List, Optional, Tuple

# -------------------------
# VicTensor: lightweight autograd tensor (NumPy-backed)
# -------------------------

class VicTensor:
    def __init__(self,
                 data: Any,
                 requires_grad: bool = False,
                 _children: Tuple["VicTensor", ...] = (),
                 _op: str = ""):
        self.data = np.array(data, dtype=np.float64)
        self.requires_grad = requires_grad
        # grad is only allocated for leaves when required; operations will
        # ensure grad arrays exist when needed.
        self.grad: Optional[np.ndarray] = np.zeros_like(self.data) if self.requires_grad else None

        # autograd graph
        self._backward: Callable[[], None] = lambda: None
        self._prev: Tuple["VicTensor", ...] = tuple(_children)
        self._op = _op

    def __repr__(self):
        return f"VicTensor(shape={self.data.shape}, req_grad={self.requires_grad}, op={self._op})"

    # -------------------------
    # Graph traversal & backward
    # -------------------------
    def backward(self, gradient: Optional[np.ndarray] = None):
        """
        Backpropagate from this tensor. If gradient is provided, uses it as
        initial gradient (useful when this tensor is not scalar).
        """
        # Build topo (postorder)
        topo: List[VicTensor] = []
        visited = set()

        def build(v: VicTensor):
            if id(v) in visited:
                return
            visited.add(id(v))
            for child in v._prev:
                build(child)
            topo.append(v)

        build(self)

        # initialize gradient of self
        if gradient is None:
            grad = np.ones_like(self.data)
        else:
            grad = np.array(gradient, dtype=np.float64)
        if self.requires_grad:
            if self.grad is None:
                self.grad = np.zeros_like(self.data)
            self.grad += grad
        else:
            # If self isn't marked requires_grad, still allow gradient accumulation
            self.grad = grad

        for node in reversed(topo):
            node._backward()

    # -------------------------
    # Utilities & factories
    # -------------------------
    @property
    def shape(self) -> Tuple[int, ...]:
        return self.data.shape

    @property
    def ndim(self) -> int:
        return self.data.ndim

    @property
    def T(self) -> "VicTensor":
        axes = tuple(reversed(range(self.ndim)))
        return self.transpose(axes)

    def clone(self) -> "VicTensor":
        return VicTensor(self.data.copy(), requires_grad=self.requires_grad)

    def zero_grad(self) -> None:
        if self.grad is not None:
            self.grad = np.zeros_like(self.data)

    def item(self):
        return self.data.item()

    # factory helpers
    @classmethod
    def randn(cls, shape: Tuple[int, ...], requires_grad: bool = False, scale: float = 1.0) -> "VicTensor":
        return cls(np.random.randn(*shape) * scale, requires_grad=requires_grad)

    @classmethod
    def zeros(cls, shape: Tuple[int, ...], requires_grad: bool = False) -> "VicTensor":
        return cls(np.zeros(shape), requires_grad=requires_grad)

    @classmethod
    def ones(cls, shape: Tuple[int, ...], requires_grad: bool = False) -> "VicTensor":
        return cls(np.ones(shape), requires_grad=requires_grad)

    # -------------------------
    # Basic arithmetic ops
    # -------------------------
    def _ensure_out(self, out_data: np.ndarray, children: Tuple["VicTensor", ...], op: str) -> "VicTensor":
        requires = any(getattr(c, "requires_grad", False) for c in children)
        out = VicTensor(out_data, requires_grad=requires, _children=children, _op=op)

        def _backward():
            # called when out.grad is set; ensure out.grad shape exists
            if out.grad is None:
                return
            for c in children:
                if not c.requires_grad:
                    continue
            # Actual gradients handled per-op in op-specific closures
            return

        out._backward = _backward
        return out

    def __add__(self, other: Any) -> "VicTensor":
        other = other if isinstance(other, VicTensor) else VicTensor(other)
        out = VicTensor(self.data + other.data, requires_grad=(self.requires_grad or other.requires_grad),
                        _children=(self, other), _op='+')

        def _backward():
            if out.grad is None:
                return
            if self.requires_grad:
                if self.grad is None:
                    self.grad = np.zeros_like(self.data)
                # broadcast out.grad to self.shape
                self.grad += np.broadcast_to(out.grad, self.data.shape)
            if other.requires_grad:
                if other.grad is None:
                    other.grad = np.zeros_like(other.data)
                other.grad += np.broadcast_to(out.grad, other.data.shape)

        out._backward = _backward
        return out

    def __radd__(self, other: Any) -> "VicTensor":
        return self.__add__(other)

    def __neg__(self) -> "VicTensor":
        out = VicTensor(-self.data, requires_grad=self.requires_grad, _children=(self,), _op='neg')

        def _backward():
            if out.grad is None:
                return
            if self.requires_grad:
                if self.grad is None:
                    self.grad = np.zeros_like(self.data)
                self.grad += -out.grad
        out._backward = _backward
        return out

    def __sub__(self, other: Any) -> "VicTensor":
        other = other if isinstance(other, VicTensor) else VicTensor(other)
        return self + (-other)

    def __mul__(self, other: Any) -> "VicTensor":
        other = other if isinstance(other, VicTensor) else VicTensor(other)
        out = VicTensor(self.data * other.data, requires_grad=(self.requires_grad or other.requires_grad),
                        _children=(self, other), _op='*')

        def _backward():
            if out.grad is None:
                return
            if self.requires_grad:
                if self.grad is None:
                    self.grad = np.zeros_like(self.data)
                self.grad += (other.data * out.grad)
            if other.requires_grad:
                if other.grad is None:
                    other.grad = np.zeros_like(other.data)
                other.grad += (self.data * out.grad)
        out._backward = _backward
        return out

    def __rmul__(self, other: Any) -> "VicTensor":
        return self.__mul__(other)

    def __truediv__(self, other: Any) -> "VicTensor":
        other = other if isinstance(other, VicTensor) else VicTensor(other)
        return self * (other ** -1)

    def __pow__(self, power: float) -> "VicTensor":
        out = VicTensor(self.data ** power, requires_grad=self.requires_grad, _children=(self,), _op=f'**{power}')

        def _backward():
            if out.grad is None:
                return
            if self.requires_grad:
                if self.grad is None:
                    self.grad = np.zeros_like(self.data)
                self.grad += (power * (self.data ** (power - 1))) * out.grad
        out._backward = _backward
        return out

    # -------------------------
    # Matrix multiply
    # -------------------------
    def __matmul__(self, other: Any) -> "VicTensor":
        other = other if isinstance(other, VicTensor) else VicTensor(other)
        out = VicTensor(self.data @ other.data, requires_grad=(self.requires_grad or other.requires_grad),
                        _children=(self, other), _op='@')

        def _backward():
            if out.grad is None:
                return
            if self.requires_grad:
                if self.grad is None:
                    self.grad = np.zeros_like(self.data)
                # (A @ B).grad w.r.t A is grad @ B.T
                self.grad += out.grad @ other.data.T
            if other.requires_grad:
                if other.grad is None:
                    other.grad = np.zeros_like(other.data)
                other.grad += self.data.T @ out.grad
        out._backward = _backward
        return out

    # -------------------------
    # Reductions and activation
    # -------------------------
    def sum(self, axis: Optional[int] = None, keepdims: bool = False) -> "VicTensor":
        out_data = np.sum(self.data, axis=axis, keepdims=keepdims)
        out = VicTensor(out_data, requires_grad=self.requires_grad, _children=(self,), _op='sum')

        def _backward():
            if out.grad is None:
                return
            if self.requires_grad:
                grad = out.grad
                # broadcast to input shape
                if axis is None:
                    grad_b = np.ones_like(self.data) * grad
                else:
                    shape = list(self.data.shape)
                    if not keepdims:
                        shape[axis] = 1
                        grad = np.reshape(grad, tuple(shape))
                    grad_b = np.ones_like(self.data) * grad
                if self.grad is None:
                    self.grad = np.zeros_like(self.data)
                self.grad += grad_b
        out._backward = _backward
        return out

    def mean(self, axis: Optional[int] = None, keepdims: bool = False) -> "VicTensor":
        out_data = np.mean(self.data, axis=axis, keepdims=keepdims)
        out = VicTensor(out_data, requires_grad=self.requires_grad, _children=(self,), _op='mean')

        def _backward():
            if out.grad is None:
                return
            if self.requires_grad:
                if axis is None:
                    denom = self.data.size
                    grad_b = np.ones_like(self.data) * (out.grad / denom)
                else:
                    # number of elements reduced
                    denom = self.data.shape[axis]
                    grad = out.grad
                    if not keepdims:
                        # expand dims
                        grad = np.expand_dims(grad, axis=axis)
                    grad_b = np.ones_like(self.data) * (grad / denom)
                if self.grad is None:
                    self.grad = np.zeros_like(self.data)
                self.grad += grad_b
        out._backward = _backward
        return out

    def relu(self) -> "VicTensor":
        out_data = np.maximum(0.0, self.data)
        out = VicTensor(out_data, requires_grad=self.requires_grad, _children=(self,), _op='relu')

        def _backward():
            if out.grad is None:
                return
            if self.requires_grad:
                mask = (self.data > 0).astype(np.float64)
                if self.grad is None:
                    self.grad = np.zeros_like(self.data)
                self.grad += mask * out.grad
        out._backward = _backward
        return out

    def tanh(self) -> "VicTensor":
        out_data = np.tanh(self.data)
        out = VicTensor(out_data, requires_grad=self.requires_grad, _children=(self,), _op='tanh')

        def _backward():
            if out.grad is None:
                return
            if self.requires_grad:
                deriv = 1.0 - out.data ** 2
                if self.grad is None:
                    self.grad = np.zeros_like(self.data)
                self.grad += deriv * out.grad
        out._backward = _backward
        return out

    def exp(self) -> "VicTensor":
        out_data = np.exp(self.data)
        out = VicTensor(out_data, requires_grad=self.requires_grad, _children=(self,), _op='exp')

        def _backward():
            if out.grad is None:
                return
            if self.requires_grad:
                if self.grad is None:
                    self.grad = np.zeros_like(self.data)
                self.grad += out.data * out.grad
        out._backward = _backward
        return out

    def log(self) -> "VicTensor":
        out_data = np.log(self.data)
        out = VicTensor(out_data, requires_grad=self.requires_grad, _children=(self,), _op='log')

        def _backward():
            if out.grad is None:
                return
            if self.requires_grad:
                if self.grad is None:
                    self.grad = np.zeros_like(self.data)
                self.grad += (1.0 / self.data) * out.grad
        out._backward = _backward
        return out

    # -------------------------
    # Softmax (vectorized along axis)
    # -------------------------
    def softmax(self, axis: int = -1) -> "VicTensor":
        shifted = self.data - np.max(self.data, axis=axis, keepdims=True)
        exp_data = np.exp(shifted)
        out_data = exp_data / np.sum(exp_data, axis=axis, keepdims=True)
        out = VicTensor(out_data, requires_grad=self.requires_grad, _children=(self,), _op='softmax')

        def _backward():
            if out.grad is None:
                return
            if not self.requires_grad:
                return
            g = out.grad
            s = out.data
            # gradient for softmax along axis: grad_in = s * (g - sum(g * s))
            inner = np.sum(g * s, axis=axis, keepdims=True)
            grad_in = s * (g - inner)
            if self.grad is None:
                self.grad = np.zeros_like(self.data)
            self.grad += grad_in
        out._backward = _backward
        return out

    # -------------------------
    # Shape ops: reshape, transpose, indexing
    # -------------------------
    def reshape(self, *newshape: int) -> "VicTensor":
        out_data = self.data.reshape(*newshape)
        out = VicTensor(out_data, requires_grad=self.requires_grad, _children=(self,), _op='reshape')

        def _backward():
            if out.grad is None:
                return
            if self.requires_grad:
                grad = out.grad.reshape(self.data.shape)
                if self.grad is None:
                    self.grad = np.zeros_like(self.data)
                self.grad += grad
        out._backward = _backward
        return out

    def transpose(self, axes: Tuple[int, ...]) -> "VicTensor":
        out_data = np.transpose(self.data, axes)
        out = VicTensor(out_data, requires_grad=self.requires_grad, _children=(self,), _op='transpose')

        def _backward():
            if out.grad is None:
                return
            if self.requires_grad:
                inv = np.argsort(axes)
                grad = np.transpose(out.grad, inv)
                if self.grad is None:
                    self.grad = np.zeros_like(self.data)
                self.grad += grad
        out._backward = _backward
        return out

    def __getitem__(self, idx) -> "VicTensor":
        out_data = self.data[idx]
        out = VicTensor(out_data, requires_grad=self.requires_grad, _children=(self,), _op='slice')

        def _backward():
            if out.grad is None:
                return
            if self.requires_grad:
                if self.grad is None:
                    self.grad = np.zeros_like(self.data)
                # place out.grad back to self.grad at slices
                np.add.at(self.grad, idx, out.grad)
        out._backward = _backward
        return out

    # JVP (simple directional sensitivity using stored grads after backward)
    def jvp(self, v: np.ndarray) -> float:
        if not self.requires_grad:
            return 0.0
        if self.grad is None:
            raise RuntimeError("jvp requires running backward() first to populate .grad")
        v = np.array(v, dtype=np.float64)
        if v.shape != self.data.shape:
            raise ValueError(f"jvp: direction shape {v.shape} != tensor shape {self.data.shape}")
        return float(np.sum(self.grad * v))

# -------------------------
# Module system (FractalStack)
# -------------------------

class Module:
    def __init__(self):
        self._modules: Dict[str, "Module"] = {}
        self._parameters: Dict[str, VicTensor] = {}
        self.training: bool = True

    def register_parameter(self, name: str, param: Optional[VicTensor]):
        if param is None:
            self._parameters.pop(name, None)
        else:
            self._parameters[name] = param

    def add_module(self, name: str, module: "Module"):
        self._modules[name] = module
        module.train(self.training)

    def __setattr__(self, name: str, value: Any):
        # treat VicTensor leaves as parameters when they require grad
        if isinstance(value, VicTensor) and getattr(value, "requires_grad", False):
            # don't call object.__setattr__ to avoid recursion; store in _parameters
            self._parameters[name] = value
        elif isinstance(value, Module):
            # store as submodule
            self._modules[name] = value
            value.train(getattr(self, "training", True))
        else:
            object.__setattr__(self, name, value)

    def __getattr__(self, name: str):
        if "_modules" in self.__dict__ and name in self._modules:
            return self._modules[name]
        if "_parameters" in self.__dict__ and name in self._parameters:
            return self._parameters[name]
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    def forward(self, *args, **kwargs):
        raise NotImplementedError

    def __call__(self, *args, **kwargs):
        return self.forward(*args, **kwargs)

    def parameters(self) -> List[VicTensor]:
        params = list(self._parameters.values())
        for m in self._modules.values():
            params.extend(m.parameters())
        return params

    def zero_grad(self):
        for p in self.parameters():
            p.zero_grad()

    def train(self, mode: bool = True):
        self.training = mode
        for m in self._modules.values():
            m.train(mode)

    def eval(self):
        self.train(False)

    def state_dict(self, prefix: str = "", result: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if result is None:
            result = {}
        for name, p in self._parameters.items():
            result[prefix + name] = p.data.copy()
        for name, m in self._modules.items():
            m.state_dict(prefix + name + ".", result)
        return result

    def load_state_dict(self, state_dict: Dict[str, Any], prefix: str = ""):
        for name, p in self._parameters.items():
            key = prefix + name
            if key in state_dict:
                if p.data.shape != state_dict[key].shape:
                    print(f"WARNING: shape mismatch for {key}, skipping")
                    continue
                p.data = state_dict[key].copy()
        for name, m in self._modules.items():
            m.load_state_dict(state_dict, prefix + name + ".")

# -------------------------
# Layers
# -------------------------

class Linear(Module):
    def __init__(self, in_features: int, out_features: int, bias: bool = True):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        std = math.sqrt(2.0 / max(1, in_features))
        self.weight = VicTensor.randn((out_features, in_features), requires_grad=True, scale=std)
        if bias:
            self.bias = VicTensor.zeros((out_features,), requires_grad=True)
        else:
            self.register_parameter("bias", None)

    def forward(self, x: VicTensor) -> VicTensor:
        # x shape: (..., in_features)
        # weight: (out_features, in_features)
        # Perform a matmul on the last dimension: we expect x.data to be shape (B, T, in_features)
        # To use VicTensor matmul semantics, we'll reshape weight to be used via explicit matmul
        # Implement as: out_data = x @ weight.T
        wT = self.weight.T  # VicTensor
        out = x @ wT
        if getattr(self, "bias", None) is not None:
            # broadcast bias to out.shape
            b = self.bias
            # ensure bias shape matches last dim
            # create broadcastable view by reshaping
            shape = list(out.data.shape)
            shape[-1] = b.data.shape[0]
            b_shaped = VicTensor(b.data.reshape((1,) * (out.ndim - 1) + b.data.shape), requires_grad=b.requires_grad)
            out = out + b_shaped
        return out

class LayerNorm(Module):
    def __init__(self, normalized_shape: int, eps: float = 1e-5):
        super().__init__()
        self.normalized_shape = (normalized_shape,)
        self.eps = eps
        self.weight = VicTensor.ones(self.normalized_shape, requires_grad=True)
        self.bias = VicTensor.zeros(self.normalized_shape, requires_grad=True)

    def forward(self, x: VicTensor) -> VicTensor:
        # compute mean & variance along last axis
        mean = x.mean(axis=-1, keepdims=True)  # returns VicTensor
        # var = mean((x - mean)^2)
        diff = x - mean
        var = (diff * diff).mean(axis=-1, keepdims=True)
        inv_std = (var + self.eps) ** -0.5
        x_norm = (x - mean) * inv_std  # VicTensor arithmetic
        # scale and shift: x_norm * weight + bias
        # need to broadcast weight and bias to x_norm shape
        w = self.weight
        b = self.bias
        # reshape w and b for broadcasting
        shape_prefix = (1,) * (x_norm.ndim - 1)
        w_view = VicTensor(w.data.reshape(shape_prefix + w.data.shape), requires_grad=w.requires_grad)
        b_view = VicTensor(b.data.reshape(shape_prefix + b.data.shape), requires_grad=b.requires_grad)
        return x_norm * w_view + b_view

class Dropout(Module):
    def __init__(self, p: float = 0.1):
        super().__init__()
        self.p = p

    def forward(self, x: VicTensor) -> VicTensor:
        if not self.training or self.p == 0.0:
            return x
        mask = (np.random.rand(*x.data.shape) >= self.p).astype(np.float64) / (1.0 - self.p)
        mask_t = VicTensor(mask, requires_grad=False)
        return x * mask_t

# -------------------------
# Attention & MLP
# -------------------------

class FlowerAttention(Module):
    def __init__(self, embed_dim: int, num_heads: int, dropout: float = 0.0):
        super().__init__()
        assert embed_dim % num_heads == 0, "embed_dim must be divisible by num_heads"
        self.embed_dim = embed_dim
        self.num_heads = num_heads
        self.head_dim = embed_dim // num_heads
        self.c_qkv = Linear(embed_dim, 3 * embed_dim)
        self.c_proj = Linear(embed_dim, embed_dim)
        self.dropout = Dropout(dropout)
        self.scale = 1.0 / math.sqrt(self.head_dim)

    def forward(self, x: VicTensor) -> VicTensor:
        # x: (B, T, C)
        B, T, C = x.shape
        qkv = self.c_qkv(x)  # (B, T, 3*C)
        # reshape to (B, T, 3, nh, hs)
        newshape = (B, T, 3, self.num_heads, self.head_dim)
        qkv = qkv.reshape(*newshape)
        # transpose to (3, B, nh, T, hs)
        qkv = qkv.transpose((2, 0, 3, 1, 4))
        q = qkv[0]
        k = qkv[1]
        v = qkv[2]
        # k_t: (B, nh, hs, T)
        k_t = k.transpose((0,1,3,2))
        # att: (B, nh, T, T)
        att = (q @ k_t) * self.scale
        att = att.softmax(axis=-1)
        att = self.dropout(att)
        y = att @ v  # (B, nh, T, hs)
        y = y.transpose((0,2,1,3))  # (B, T, nh, hs)
        y = y.reshape(B, T, C)
        y = self.c_proj(y)
        return y

class FractalMLP(Module):
    def __init__(self, embed_dim: int, expand_mult: int = 4):
        super().__init__()
        self.c_fc = Linear(embed_dim, embed_dim * expand_mult)
        self.c_proj = Linear(embed_dim * expand_mult, embed_dim)

    def gelu(self, x: VicTensor) -> VicTensor:
        # Approximate GELU with tanh-based formula
        # 0.5 * x * (1 + tanh(sqrt(2/pi) * (x + 0.044715 * x^3)))
        a = 0.044715
        k = math.sqrt(2.0 / math.pi)
        x3 = x * (x * x)
        inner = (x + a * x3) * k
        return 0.5 * x * (1.0 + inner.tanh())

    def forward(self, x: VicTensor) -> VicTensor:
        h = self.c_fc(x)
        h = self.gelu(h)
        h = self.c_proj(h)
        return h

# -------------------------
# SeedBlock and FractalStack
# -------------------------

class SeedBlock(Module):
    def __init__(self, embed_dim: int, num_heads: int):
        super().__init__()
        self.ln1 = LayerNorm(embed_dim)
        self.attn = FlowerAttention(embed_dim, num_heads)
        self.ln2 = LayerNorm(embed_dim)
        self.mlp = FractalMLP(embed_dim)

    def forward(self, x: VicTensor) -> VicTensor:
        x = x + self.attn(self.ln1(x))
        x = x + self.mlp(self.ln2(x))
        return x

class FractalStack(Module):
    def __init__(self, layers: List[Module]):
        super().__init__()
        self.layers = layers
        for i, layer in enumerate(layers):
            self.add_module(f"seed_{i}", layer)

    def forward(self, x: VicTensor) -> VicTensor:
        for layer in self.layers:
            x = layer(x)
        return x

# -------------------------
# Simple Adam optimizer
# -------------------------

class Adam:
    def __init__(self, params: List[VicTensor], lr: float = 1e-3, betas: Tuple[float, float] = (0.9, 0.999), eps: float = 1e-8):
        self.params = [p for p in params if p.requires_grad]
        self.lr = lr
        self.beta1, self.beta2 = betas
        self.eps = eps
        self.m = [np.zeros_like(p.data) for p in self.params]
        self.v = [np.zeros_like(p.data) for p in self.params]
        self.t = 0

    def zero_grad(self):
        for p in self.params:
            p.zero_grad()

    def step(self):
        self.t += 1
        for i, p in enumerate(self.params):
            if p.grad is None:
                continue
            g = p.grad
            self.m[i] = self.beta1 * self.m[i] + (1 - self.beta1) * g
            self.v[i] = self.beta2 * self.v[i] + (1 - self.beta2) * (g * g)
            m_hat = self.m[i] / (1 - self.beta1 ** self.t)
            v_hat = self.v[i] / (1 - self.beta2 ** self.t)
            update = self.lr * m_hat / (np.sqrt(v_hat) + self.eps)
            p.data -= update
            # clear grad after update
            p.grad = np.zeros_like(p.data)

# -------------------------
# Demo: small sanity-check run
# -------------------------

def demo_fractal_cortex():
    print("=== Fractal Cortex Demo (toy size) ===")
    B, T, C = 2, 6, 32
    # random input with requires_grad=True to test gradient flow to inputs
    x = VicTensor.randn((B, T, C), requires_grad=True)
    # small stack
    model = FractalStack([SeedBlock(C, num_heads=4) for _ in range(3)])
    params = model.parameters()
    optimizer = Adam(params, lr=1e-3)

    def mse_loss(pred: VicTensor, target: VicTensor) -> VicTensor:
        return ((pred - target) * (pred - target)).mean()

    # target as zero tensor
    y_target = VicTensor.zeros((B, T, C), requires_grad=False)

    for epoch in range(3):
        optimizer.zero_grad()
        out = model(x)
        loss = mse_loss(out, y_target)
        # backward
        loss.backward()
        # check grads
        g_counts = sum(1 for p in params if p.grad is not None and np.any(p.grad != 0.0))
        print(f"Epoch {epoch} | loss={float(loss.data):.6f} | params_with_grad={g_counts}/{len(params)}")
        optimizer.step()

    # JVP check: run backward then compute jvp on input
    out = model(x)
    loss = mse_loss(out, y_target)
    loss.backward()
    v = np.zeros_like(x.data)
    v[0,0,:] = 1e-6
    jvp_val = x.jvp(v)
    print(f"JVP (tiny perturbation at token 0): {jvp_val:.8e}")

    print("Demo complete. Basic forward/backward and optimizer step executed.")

if __name__ == "__main__":
    demo_fractal_cortex()