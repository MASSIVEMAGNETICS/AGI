# Minimal autograd Tensor implementation with fixes for:
# - __init__ signature and initialization
# - .pow wrapper
# - .clip method
# - robust backward traversal using object ids
# - ensure .grad exists before accumulation
# - simple view support via reshape/backward connection
from typing import Union, Optional, Callable, Set, List
import numpy as np

ArrayLike = Union[np.ndarray, list, float, int]

class Tensor:
    def __init__(self, data: ArrayLike, requires_grad: bool = False, dtype=np.float32):
        # Normalize input to numpy array
        self.data = np.array(data, dtype=dtype)
        self.shape = self.data.shape
        self.requires_grad = requires_grad
        # Grad is a numpy array matching shape when needed; kept as None until required
        self.grad: Optional[np.ndarray] = None
        # Autograd graph metadata
        self._prev: Set['Tensor'] = set()
        self._grad_fn: Optional[Callable[[], None]] = None
        self._op: str = ""
        # For topological traversal we don't rely on hashing Tensor objects themselves
        # but use Python id() when marking visited.

    def _ensure_grad(self):
        if self.grad is None:
            self.grad = np.zeros_like(self.data)

    def zero_grad(self):
        self.grad = None

    def __repr__(self):
        return f"Tensor(data={self.data}, requires_grad={self.requires_grad})"

    # Elementwise add
    def __add__(self, other):
        other_t = other if isinstance(other, Tensor) else Tensor(other)
        out = Tensor(self.data + other_t.data, requires_grad=(self.requires_grad or other_t.requires_grad))

        def _backward():
            if self.requires_grad:
                self._ensure_grad()
                # handle broadcasting
                grad = out.grad
                # reduce grad shape to self.shape if necessary
                self.grad += _reduce_broadcast_gradient(grad, self.shape)
            if other_t.requires_grad:
                other_t._ensure_grad()
                grad = out.grad
                other_t.grad += _reduce_broadcast_gradient(grad, other_t.shape)

        out._prev = {self, other_t}
        out._grad_fn = _backward
        out._op = "add"
        return out

    __radd__ = __add__

    # Elementwise subtraction
    def __sub__(self, other):
        return self + (other * -1)

    def __rsub__(self, other):
        return Tensor(other) + (self * -1)

    # Elementwise multiply
    def __mul__(self, other):
        other_t = other if isinstance(other, Tensor) else Tensor(other)
        out = Tensor(self.data * other_t.data, requires_grad=(self.requires_grad or other_t.requires_grad))

        def _backward():
            if self.requires_grad:
                self._ensure_grad()
                grad = out.grad * other_t.data
                self.grad += _reduce_broadcast_gradient(grad, self.shape)
            if other_t.requires_grad:
                other_t._ensure_grad()
                grad = out.grad * self.data
                other_t.grad += _reduce_broadcast_gradient(grad, other_t.shape)

        out._prev = {self, other_t}
        out._grad_fn = _backward
        out._op = "mul"
        return out

    __rmul__ = __mul__

    # Power operator
    def __pow__(self, exponent):
        # support scalar exponents
        if isinstance(exponent, Tensor):
            exp_data = exponent.data
        else:
            exp_data = exponent
        out = Tensor(self.data ** exp_data, requires_grad=self.requires_grad)

        def _backward():
            if self.requires_grad:
                self._ensure_grad()
                grad = out.grad * (self.data ** (exp_data - 1)) * exp_data
                self.grad += _reduce_broadcast_gradient(grad, self.shape)
            # exponent gradient (if exponent is Tensor) is not implemented here for simplicity

        out._prev = {self}
        out._grad_fn = _backward
        out._op = "pow"
        return out

    # convenience wrapper
    def pow(self, exponent):
        return self.__pow__(exponent)

    # True division
    def __truediv__(self, other):
        other_t = other if isinstance(other, Tensor) else Tensor(other)
        return self * other_t.pow(-1)

    # Negation
    def __neg__(self):
        return self * -1

    # Sum reduction
    def sum(self):
        out = Tensor(self.data.sum(), requires_grad=self.requires_grad)

        def _backward():
            if self.requires_grad:
                self._ensure_grad()
                # gradient of sum is broadcast of out.grad
                self.grad += np.ones_like(self.data) * out.grad

        out._prev = {self}
        out._grad_fn = _backward
        out._op = "sum"
        return out

    def mean(self):
        return self.sum() * (1.0 / np.prod(self.shape))

    # reshape / view - create new tensor pointing to same data shape; keep backward link
    def reshape(self, *shape):
        out = Tensor(self.data.reshape(*shape), requires_grad=self.requires_grad)

        def _backward():
            if self.requires_grad:
                self._ensure_grad()
                self.grad += out.grad.reshape(self.shape)

        out._prev = {self}
        out._grad_fn = _backward
        out._op = "reshape"
        return out

    view = reshape

    # clip method
    def clip(self, a_min, a_max):
        # Clip is non-differentiable where clamped; we implement gradient passthrough for inner region
        out = Tensor(np.clip(self.data, a_min, a_max), requires_grad=self.requires_grad)

        def _backward():
            if self.requires_grad:
                self._ensure_grad()
                mask = (self.data >= a_min) & (self.data <= a_max)
                self.grad += out.grad * mask

        out._prev = {self}
        out._grad_fn = _backward
        out._op = "clip"
        return out

    # backward pass
    def backward(self, gradient: Optional[Union[np.ndarray, float]] = None, retain_graph: bool = False):
        # Seed gradient
        if gradient is None:
            if self.data.size == 1:
                grad = np.array(1.0, dtype=self.data.dtype)
            else:
                grad = np.ones_like(self.data)
        else:
            grad = np.array(gradient, dtype=self.data.dtype)

        self._ensure_grad()
        self.grad += grad

        # Topological sort
        topo: List[Tensor] = []
        visited_ids = set()
        def build_topo(t: 'Tensor'):
            tid = id(t)
            if tid in visited_ids:
                return
            visited_ids.add(tid)
            for child in getattr(t, "_prev", []):
                build_topo(child)
            topo.append(t)
        build_topo(self)

        # Traverse in reverse order and call grad functions
        for t in reversed(topo):
            if t._grad_fn is not None:
                # Ensure out.grad is available for this node; out is t
                if t.grad is None:
                    # nothing to propagate
                    continue
                # prepare out.grad as numpy for functions that expect numpy
                # Execute grad function which will accumulate into predecessors' .grad
                t._grad_fn()
                if not retain_graph:
                    t._grad_fn = None  # free the graph reference

# utility to reduce broadcasted gradient to target shape
def _reduce_broadcast_gradient(grad: np.ndarray, target_shape: tuple) -> np.ndarray:
    # If shapes match, return grad directly
    if grad.shape == target_shape:
        return grad
    # Otherwise, sum over axes that are extra or of length 1 in target
    grad_shape = grad.shape
    # Pad target shape with leading ones to match grad ndim
    ndiff = len(grad_shape) - len(target_shape)
    if ndiff < 0:
        # grad has fewer dims than target (shouldn't happen), just reshape
        return grad.reshape(target_shape)
    padded_target = (1,) * ndiff + target_shape
    axes = []
    for i, (gdim, tdim) in enumerate(zip(grad_shape, padded_target)):
        if tdim == 1 and gdim != 1:
            axes.append(i)
    if axes:
        grad = grad.sum(axis=tuple(axes), keepdims=True)
    # final reshape to target_shape
    return grad.reshape(target_shape)


# Example loss function: binary cross entropy (numerically stable)
def binary_cross_entropy(y_pred: Tensor, y_true: Tensor, eps: float = 1e-7):
    # Clip underlying numpy arrays for numerical stability
    yp = np.clip(y_pred.data, eps, 1.0 - eps)
    yt = y_true.data
    loss_val = - (yt * np.log(yp) + (1 - yt) * np.log(1 - yp)).mean()
    out = Tensor(loss_val, requires_grad=y_pred.requires_grad or y_true.requires_grad)

    def _backward():
        # gradient wrt y_pred
        if y_pred.requires_grad:
            y_pred._ensure_grad()
            grad = ((-yt / yp) + ((1 - yt) / (1 - yp))) / np.prod(y_true.shape)
            y_pred.grad += grad
        # we do not compute gradient w.r.t. y_true here for simplicity

    out._prev = {y_pred, y_true}
    out._grad_fn = _backward
    out._op = "bce"
    return out