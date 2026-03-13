# FILE: tensor_autograd_full.py
# VERSION: v1.0.0-GODCORE-FULL
# AUTHOR: Brandon 'iambandobandz' Emery — Sovereign Integration of Autograd + Optimizers + JVP
# PURPOSE: Complete, standalone autograd engine with optimizers and Jacobian-Vector Products
# LICENSE: Bando Bloodline Sovereign Use Only
# COMPATIBILITY: Python 3.10+, numpy>=1.20

import numpy as np
from typing import List, Tuple, Callable, Optional, Union, Any
from datetime import datetime

# ========================
# TENSOR AUTOGRADE ENGINE
# ========================

class Tensor:
    __slots__ = ('data', 'grad', '_backward', '_prev', '_op', 'requires_grad')

    def __init__(self,  Union[np.ndarray, list, float], requires_grad: bool = False, dtype=np.float32):
        if not isinstance(data, np.ndarray):
            data = np.array(data, dtype=dtype)
        self.data = data.astype(dtype)
        self.grad: Optional[np.ndarray] = None
        self.requires_grad = requires_grad
        self._backward = lambda: None
        self._prev: List['Tensor'] = []
        self._op = ''

    @property
    def shape(self) -> Tuple[int, ...]:
        return self.data.shape

    @property
    def ndim(self) -> int:
        return self.data.ndim

    def __repr__(self):
        return f"Tensor({self.data}, requires_grad={self.requires_grad})"

    def _broadcast_backward(self, grad_out: np.ndarray, orig_shape: Tuple[int, ...]) -> np.ndarray:
        """Reduce broadcasted gradient back to original shape."""
        if grad_out.shape == orig_shape:
            return grad_out
        # Sum over expanded dimensions
        axis = tuple(i for i, (o, g) in enumerate(zip(orig_shape, grad_out.shape)) if o == 1 and g != 1)
        if axis:
            grad_out = np.sum(grad_out, axis=axis, keepdims=True)
        # Remove leading dims added during broadcast
        if len(grad_out.shape) > len(orig_shape):
            grad_out = np.sum(grad_out, axis=tuple(range(len(grad_out.shape) - len(orig_shape))))
        return grad_out

    def __add__(self, other: Union['Tensor', float]) -> 'Tensor':
        other = other if isinstance(other, Tensor) else Tensor(other)
        out = Tensor(self.data + other.data, requires_grad=(self.requires_grad or other.requires_grad))
        out._prev = [self, other]
        out._op = '+'

        def _backward():
            if self.requires_grad:
                grad = self._broadcast_backward(out.grad, self.shape)
                if self.grad is None:
                    self.grad = grad
                else:
                    self.grad += grad
            if other.requires_grad:
                grad = self._broadcast_backward(out.grad, other.shape)
                if other.grad is None:
                    other.grad = grad
                else:
                    other.grad += grad

        out._backward = _backward
        return out

    def __radd__(self, other):
        return self.__add__(other)

    def __neg__(self) -> 'Tensor':
        out = Tensor(-self.data, requires_grad=self.requires_grad)
        out._prev = [self]
        out._op = '-'

        def _backward():
            if self.requires_grad:
                if self.grad is None:
                    self.grad = -out.grad
                else:
                    self.grad -= out.grad

        out._backward = _backward
        return out

    def __sub__(self, other):
        return self + (-other)

    def __rsub__(self, other):
        return (-self) + other

    def __mul__(self, other: Union['Tensor', float]) -> 'Tensor':
        other = other if isinstance(other, Tensor) else Tensor(other)
        out = Tensor(self.data * other.data, requires_grad=(self.requires_grad or other.requires_grad))
        out._prev = [self, other]
        out._op = '*'

        def _backward():
            if self.requires_grad:
                grad = out.grad * other.data
                grad = self._broadcast_backward(grad, self.shape)
                if self.grad is None:
                    self.grad = grad
                else:
                    self.grad += grad
            if other.requires_grad:
                grad = out.grad * self.data
                grad = self._broadcast_backward(grad, other.shape)
                if other.grad is None:
                    other.grad = grad
                else:
                    other.grad += grad

        out._backward = _backward
        return out

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        return self * (other ** -1)

    def __rtruediv__(self, other):
        return other * (self ** -1)

    def __pow__(self, exponent: Union[float, int]) -> 'Tensor':
        assert isinstance(exponent, (int, float)), "Power must be scalar"
        out = Tensor(self.data ** exponent, requires_grad=self.requires_grad)
        out._prev = [self]
        out._op = f'**{exponent}'

        def _backward():
            if self.requires_grad:
                grad = out.grad * exponent * (self.data ** (exponent - 1))
                if self.grad is None:
                    self.grad = grad
                else:
                    self.grad += grad

        out._backward = _backward
        return out

    def __matmul__(self, other: 'Tensor') -> 'Tensor':
        if self.ndim > 2 or other.ndim > 2:
            raise ValueError("Matmul supports up to 2D tensors.")
        out = Tensor(self.data @ other.data, requires_grad=(self.requires_grad or other.requires_grad))
        out._prev = [self, other]
        out._op = '@'

        def _backward():
            if self.requires_grad:
                grad = out.grad @ other.data.T
                if self.grad is None:
                    self.grad = grad
                else:
                    self.grad += grad
            if other.requires_grad:
                grad = self.data.T @ out.grad
                if other.grad is None:
                    other.grad = grad
                else:
                    other.grad += grad

        out._backward = _backward
        return out

    def relu(self) -> 'Tensor':
        out = Tensor(np.maximum(0, self.data), requires_grad=self.requires_grad)
        out._prev = [self]
        out._op = 'relu'

        def _backward():
            if self.requires_grad:
                grad = out.grad * (self.data > 0)
                if self.grad is None:
                    self.grad = grad
                else:
                    self.grad += grad

        out._backward = _backward
        return out

    def sigmoid(self) -> 'Tensor':
        s = 1 / (1 + np.exp(-np.clip(self.data, -709, 709)))  # avoid overflow
        out = Tensor(s, requires_grad=self.requires_grad)
        out._prev = [self]
        out._op = 'sigmoid'

        def _backward():
            if self.requires_grad:
                grad = out.grad * s * (1 - s)
                if self.grad is None:
                    self.grad = grad
                else:
                    self.grad += grad

        out._backward = _backward
        return out

    def tanh(self) -> 'Tensor':
        t = np.tanh(self.data)
        out = Tensor(t, requires_grad=self.requires_grad)
        out._prev = [self]
        out._op = 'tanh'

        def _backward():
            if self.requires_grad:
                grad = out.grad * (1 - t ** 2)
                if self.grad is None:
                    self.grad = grad
                else:
                    self.grad += grad

        out._backward = _backward
        return out

    def exp(self) -> 'Tensor':
        e = np.exp(np.clip(self.data, -709, 709))
        out = Tensor(e, requires_grad=self.requires_grad)
        out._prev = [self]
        out._op = 'exp'

        def _backward():
            if self.requires_grad:
                grad = out.grad * e
                if self.grad is None:
                    self.grad = grad
                else:
                    self.grad += grad

        out._backward = _backward
        return out

    def log(self) -> 'Tensor':
        out = Tensor(np.log(np.clip(self.data, 1e-12, None)), requires_grad=self.requires_grad)
        out._prev = [self]
        out._op = 'log'

        def _backward():
            if self.requires_grad:
                grad = out.grad / np.clip(self.data, 1e-12, None)
                if self.grad is None:
                    self.grad = grad
                else:
                    self.grad += grad

        out._backward = _backward
        return out

    def sum(self, axis=None, keepdims=False) -> 'Tensor':
        out = Tensor(np.sum(self.data, axis=axis, keepdims=keepdims), requires_grad=self.requires_grad)
        out._prev = [self]
        out._op = 'sum'

        def _backward():
            if self.requires_grad:
                grad = out.grad
                if axis is not None and not keepdims:
                    grad = np.expand_dims(grad, axis=axis)
                grad = np.broadcast_to(grad, self.shape)
                if self.grad is None:
                    self.grad = grad
                else:
                    self.grad += grad

        out._backward = _backward
        return out

    def mean(self, axis=None, keepdims=False) -> 'Tensor':
        total = self.data.size if axis is None else self.shape[axis]
        return self.sum(axis, keepdims) / total

    def view(self, shape: Tuple[int, ...]) -> 'Tensor':
        out = Tensor(self.data.reshape(shape), requires_grad=self.requires_grad)
        out._prev = [self]  # for grad flow
        return out

    def detach(self) -> 'Tensor':
        return Tensor(self.data.copy(), requires_grad=False)

    def zero_grad(self) -> None:
        self.grad = None

    def backward(self) -> None:
        if not self.requires_grad:
            raise RuntimeError("Cannot backward on tensor without requires_grad=True")
        if self.grad is None:
            self.grad = np.ones_like(self.data)

        topo: List['Tensor'] = []
        visited = set()

        def build_topo(v: 'Tensor'):
            if v not in visited:
                visited.add(v)
                for child in v._prev:
                    build_topo(child)
                topo.append(v)

        build_topo(self)

        for node in reversed(topo):
            node._backward()


# ========================
# OPTIMIZERS
# ========================

class Optimizer:
    def __init__(self, params: List[Tensor]):
        self.params = params

    def step(self):
        raise NotImplementedError

    def zero_grad(self):
        for p in self.params:
            p.zero_grad()


class SGD(Optimizer):
    def __init__(self, params: List[Tensor], lr: float = 0.01, momentum: float = 0.0, weight_decay: float = 0.0):
        super().__init__(params)
        self.lr = lr
        self.momentum = momentum
        self.weight_decay = weight_decay
        self.velocity = [np.zeros_like(p.data) for p in params]

    def step(self):
        for i, p in enumerate(self.params):
            if p.grad is None:
                continue
            grad = p.grad + self.weight_decay * p.data
            self.velocity[i] = self.momentum * self.velocity[i] + grad
            p.data -= self.lr * self.velocity[i]


class Adam(Optimizer):
    def __init__(self, params: List[Tensor], lr: float = 0.001, betas: Tuple[float, float] = (0.9, 0.999), eps: float = 1e-8, weight_decay: float = 0.0):
        super().__init__(params)
        self.lr = lr
        self.betas = betas
        self.eps = eps
        self.weight_decay = weight_decay
        self.m = [np.zeros_like(p.data) for p in params]
        self.v = [np.zeros_like(p.data) for p in params]
        self.t = 0

    def step(self):
        self.t += 1
        beta1, beta2 = self.betas
        for i, p in enumerate(self.params):
            if p.grad is None:
                continue
            grad = p.grad + self.weight_decay * p.data
            self.m[i] = beta1 * self.m[i] + (1 - beta1) * grad
            self.v[i] = beta2 * self.v[i] + (1 - beta2) * (grad ** 2)
            m_hat = self.m[i] / (1 - beta1 ** self.t)
            v_hat = self.v[i] / (1 - beta2 ** self.t)
            p.data -= self.lr * m_hat / (np.sqrt(v_hat) + self.eps)


class RMSprop(Optimizer):
    def __init__(self, params: List[Tensor], lr: float = 0.01, alpha: float = 0.99, eps: float = 1e-8, weight_decay: float = 0.0, momentum: float = 0.0, centered: bool = False):
        super().__init__(params)
        self.lr = lr
        self.alpha = alpha
        self.eps = eps
        self.weight_decay = weight_decay
        self.momentum = momentum
        self.centered = centered
        self.avg = [np.zeros_like(p.data) for p in params]
        self.avg_grad = [np.zeros_like(p.data) for p in params] if centered else None
        self.buffer = [np.zeros_like(p.data) for p in params] if momentum > 0 else None

    def step(self):
        for i, p in enumerate(self.params):
            if p.grad is None:
                continue
            grad = p.grad + self.weight_decay * p.data
            self.avg[i] = self.alpha * self.avg[i] + (1 - self.alpha) * (grad ** 2)
            if self.centered:
                self.avg_grad[i] = self.alpha * self.avg_grad[i] + (1 - self.alpha) * grad
                denom = np.sqrt(self.avg[i] - self.avg_grad[i] ** 2) + self.eps
            else:
                denom = np.sqrt(self.avg[i]) + self.eps
            if self.momentum > 0:
                self.buffer[i] = self.momentum * self.buffer[i] + grad / denom
                p.data -= self.lr * self.buffer[i]
            else:
                p.data -= self.lr * (grad / denom)


# ========================
# JACOBIAN-VECTOR PRODUCT (JVP)
# ========================

def jvp(func: Callable, primals: Tuple[Tensor, ...], tangents: Tuple[Tensor, ...]) -> Tuple[Tensor, Tensor]:
    class DualTensor:
        def __init__(self, primal: Tensor, tangent: Optional[Tensor] = None):
            self.primal = primal
            self.tangent = tangent if tangent is not None else Tensor(np.zeros_like(primal.data))

        def __add__(self, other):
            other = other if isinstance(other, DualTensor) else DualTensor(other, Tensor(0))
            return DualTensor(self.primal + other.primal, self.tangent + other.tangent)

        def __mul__(self, other):
            other = other if isinstance(other, DualTensor) else DualTensor(other, Tensor(0))
            return DualTensor(
                self.primal * other.primal,
                self.tangent * other.primal + self.primal * other.tangent
            )

        def __pow__(self, exponent):
            p = self.primal ** exponent
            t = exponent * (self.primal ** (exponent - 1)) * self.tangent
            return DualTensor(p, t)

        def exp(self):
            e = self.primal.exp()
            return DualTensor(e, e * self.tangent)

        def log(self):
            l = self.primal.log()
            return DualTensor(l, self.tangent / self.primal)

    duals = [DualTensor(p, t) for p, t in zip(primals, tangents)]
    out_dual = func(*duals)
    return out_dual.primal, out_dual.tangent


# ========================
# MODEL & TRAINING
# ========================

class Linear:
    def __init__(self, in_features: int, out_features: int):
        self.weight = Tensor(np.random.randn(in_features, out_features) * np.sqrt(2 / in_features), requires_grad=True)
        self.bias = Tensor(np.zeros(out_features), requires_grad=True)

    def __call__(self, x: Tensor) -> Tensor:
        return x @ self.weight + self.bias


class MLP:
    def __init__(self):
        self.fc1 = Linear(2, 16)
        self.fc2 = Linear(16, 1)

    def __call__(self, x: Tensor) -> Tensor:
        x = self.fc1(x).relu()
        return self.fc2(x).sigmoid()


def binary_cross_entropy(y_pred: Tensor, y_true: Tensor) -> Tensor:
    return -(y_true * y_pred.log() + (1 - y_true) * (1 - y_pred).log()).mean()


def train_xor_with_adam():
    print("🧠 Training XOR with Adam...")
    model = MLP()
    params = [model.fc1.weight, model.fc1.bias, model.fc2.weight, model.fc2.bias]
    opt = Adam(params, lr=0.01)

    X = Tensor([[0,0], [0,1], [1,0], [1,1]])
    Y = Tensor([[0], [1], [1], [0]])

    for epoch in range(501):
        y_pred = model(X)
        loss = binary_cross_entropy(y_pred, Y)
        loss.backward()
        opt.step()
        opt.zero_grad()

        if epoch % 100 == 0:
            print(f"Epoch {epoch:4d}, Loss: {loss.data.item():.6f}")

    print("✅ Final predictions:", model(X).data.flatten())
    return model


def demo_jvp():
    print("\n🔍 JVP Test: f(x,y) = x²·y + exp(x)")
    def f(x, y):
        return (x ** 2) * y + x.exp()

    x = Tensor(3.0, requires_grad=True)
    y = Tensor(2.0, requires_grad=True)
    vx = Tensor(1.0)
    vy = Tensor(0.5)

    primal, tangent = jvp(f, (x, y), (vx, vy))

    # Manual: df/dx = 2xy + exp(x), df/dy = x² → JVP = (2xy + exp(x))*vx + x²*vy
    manual = (2*3*2 + np.exp(3)) * 1 + (3**2) * 0.5
    print(f"Primal: {primal..6f}")
    print(f"JVP: {tangent..6f}")
    print(f"Manual: {manual:.6f}")
    print(f"Match: {abs(tangent.data - manual) < 1e-5}")


# ========================
# MAIN
# ========================

if __name__ == "__main__":
    print("="*60)
    print("VICTOR-STYLE AUTOGRADE ENGINE — FULL STACK ACTIVATED")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("="*60)

    train_xor_with_adam()
    demo_jvp()

    print("\n✨ Autograd + Optimizers + JVP — Sovereign cognition enabled.")