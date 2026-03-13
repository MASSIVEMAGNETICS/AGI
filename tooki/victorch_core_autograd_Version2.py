"""
Maximal-robust autograd engine for Vic-Torch (pure NumPy backend).

Goals:
- Context / Function pattern (save_for_backward)
- Function.apply that works with repo Tensor (duck-typed)
- Common ops implemented: Add, Sub, Mul, Div, MatMul, Sum, Mean, Reshape, Transpose
- Broadcasting-aware gradient unroll
- no_grad context manager
- Lightweight hooks + deterministic, iterative backprop helpers (used by Tensor.backward)
Notes:
- This module expects a Tensor-like class at victorch.core.tensor.Tensor with:
    - .data (np.ndarray)
    - __init__(data, requires_grad=False)
    - set_creator(func_instance)   # attaches creator and parents
    - requires_grad boolean flag
    - grad/accumulation handled by Tensor.backward (we provide helpers)
- Function.backward implementations receive (ctx, grad_output) and must return a tuple
  of grads aligned to the Tensor parents order.
"""

from __future__ import annotations
import numpy as np
import contextlib
from typing import Any, Tuple, Sequence, Optional

# Global grad mode
_grad_enabled = True

@contextlib.contextmanager
def no_grad():
    global _grad_enabled
    prev = _grad_enabled
    _grad_enabled = False
    try:
        yield
    finally:
        _grad_enabled = prev

def grad_enabled() -> bool:
    return _grad_enabled

# Context to save tensors / intermediates for backward
class Context:
    def __init__(self):
        self._saved: Tuple[Any, ...] = ()
        self.needs_input_grad: Optional[Tuple[bool, ...]] = None

    def save_for_backward(self, *tensors):
        # store references (small, usually)
        self._saved = tensors

    @property
    def saved_tensors(self):
        return self._saved

# Base Function class
class Function:
    """
    Subclasses should implement:
      @staticmethod
      def forward(ctx: Context, *args) -> np.ndarray

      @staticmethod
      def backward(ctx: Context, grad_output: np.ndarray) -> Tuple[np.ndarray, ...]
    """
    def __init__(self, ctx: Context, parents: Sequence[Any]):
        self.ctx = ctx
        # parents should be the Tensor instances corresponding to inputs
        self.parents = tuple(parents)

    @classmethod
    def apply(cls, *args):
        """
        Apply function. Accepts Tensor instances and raw numpy/scalars.
        Returns a Tensor (from victorch.core.tensor) when possible.
        """
        # Fast-return when grad disabled globally
        if not grad_enabled():
            # call forward and return raw Tensor-like wrapper if available
            ctx = Context()
            raw_args = [a.data if hasattr(a, 'data') else a for a in args]
            out_data = cls.forward(ctx, *raw_args)
            from victorch.core.tensor import Tensor  # local import to avoid import cycle
            return Tensor(out_data, requires_grad=False)

        # Normal path
        ctx = Context()
        # Collect raw arrays for forward
        raw_args = [a.data if hasattr(a, 'data') else a for a in args]
        out_data = cls.forward(ctx, *raw_args)

        # Determine requires_grad from any Tensor inputs
        requires_grad = any(hasattr(a, 'requires_grad') and a.requires_grad for a in args)
        from victorch.core.tensor import Tensor  # local import to avoid import cycle
        out = Tensor(out_data, requires_grad=requires_grad)

        if requires_grad:
            # collect only Tensor parents (in order)
            parents = [a for a in args if hasattr(a, 'data')]
            func_instance = cls(ctx, parents)
            out.set_creator(func_instance)
        return out

# -------------------
# Utilities
# -------------------

def _ensure_ndarray(x):
    if isinstance(x, np.ndarray):
        return x
    if hasattr(x, 'data'):
        return x.data
    return np.array(x)

def _unbroadcast(grad: np.ndarray, target_shape: Tuple[int, ...]) -> np.ndarray:
    """
    Reduce grad (which may have been broadcasted) to target_shape by summing
    across broadcasted axes.
    """
    if grad.shape == target_shape:
        return grad
    # Sum leading dims if grad ndim > target ndim
    while grad.ndim > len(target_shape):
        grad = grad.sum(axis=0)
    # Sum across axes where target has dim=1
    for axis, (g_dim, t_dim) in enumerate(zip(grad.shape, target_shape)):
        if t_dim == 1 and g_dim != 1:
            grad = grad.sum(axis=axis, keepdims=True)
    # Finally, reshape to ensure exact match
    return grad.reshape(target_shape)

# -------------------
# Basic ops
# -------------------

class Add(Function):
    @staticmethod
    def forward(ctx: Context, a, b):
        # No need to save anything other than shapes for unbroadcasting
        a_arr = _ensure_ndarray(a)
        b_arr = _ensure_ndarray(b)
        ctx.save_for_backward(a_arr.shape, b_arr.shape)
        return a_arr + b_arr

    @staticmethod
    def backward(ctx: Context, grad_output):
        ashape, bshape = ctx.saved_tensors
        # passthrough; but must un-broadcast by shape
        return _unbroadcast(grad_output, ashape), _unbroadcast(grad_output, bshape)

class Sub(Function):
    @staticmethod
    def forward(ctx: Context, a, b):
        a_arr = _ensure_ndarray(a)
        b_arr = _ensure_ndarray(b)
        ctx.save_for_backward(a_arr.shape, b_arr.shape)
        return a_arr - b_arr

    @staticmethod
    def backward(ctx: Context, grad_output):
        ashape, bshape = ctx.saved_tensors
        return _unbroadcast(grad_output, ashape), _unbroadcast(-grad_output, bshape)

class Mul(Function):
    @staticmethod
    def forward(ctx: Context, a, b):
        a_arr = _ensure_ndarray(a)
        b_arr = _ensure_ndarray(b)
        ctx.save_for_backward(a_arr, b_arr, a_arr.shape, b_arr.shape)
        return a_arr * b_arr

    @staticmethod
    def backward(ctx: Context, grad_output):
        a, b, ashape, bshape = ctx.saved_tensors
        ga = grad_output * b
        gb = grad_output * a
        return _unbroadcast(ga, ashape), _unbroadcast(gb, bshape)

class Div(Function):
    @staticmethod
    def forward(ctx: Context, a, b):
        a_arr = _ensure_ndarray(a)
        b_arr = _ensure_ndarray(b)
        ctx.save_for_backward(a_arr, b_arr, a_arr.shape, b_arr.shape)
        return a_arr / b_arr

    @staticmethod
    def backward(ctx: Context, grad_output):
        a, b, ashape, bshape = ctx.saved_tensors
        ga = grad_output / b
        gb = -grad_output * a / (b ** 2)
        return _unbroadcast(ga, ashape), _unbroadcast(gb, bshape)

class MatMul(Function):
    @staticmethod
    def forward(ctx: Context, a, b):
        a_arr = _ensure_ndarray(a)
        b_arr = _ensure_ndarray(b)
        ctx.save_for_backward(a_arr, b_arr)
        return a_arr @ b_arr

    @staticmethod
    def backward(ctx: Context, grad_output):
        a, b = ctx.saved_tensors
        # grad_output shapes follow matmul rules
        ga = grad_output @ b.T
        gb = a.T @ grad_output
        return ga, gb

class Reshape(Function):
    @staticmethod
    def forward(ctx: Context, a, new_shape):
        a_arr = _ensure_ndarray(a)
        ctx.save_for_backward(a_arr.shape)
        return a_arr.reshape(new_shape)

    @staticmethod
    def backward(ctx: Context, grad_output):
        (orig_shape,) = ctx.saved_tensors
        return grad_output.reshape(orig_shape)

class Transpose(Function):
    @staticmethod
    def forward(ctx: Context, a, axes):
        a_arr = _ensure_ndarray(a)
        ctx.save_for_backward(axes)
        return a_arr.transpose(axes)

    @staticmethod
    def backward(ctx: Context, grad_output):
        (axes,) = ctx.saved_tensors
        # invert permutation
        inv = np.argsort(axes)
        return grad_output.transpose(inv)

class Sum(Function):
    @staticmethod
    def forward(ctx: Context, a, axis=None, keepdims=False):
        a_arr = _ensure_ndarray(a)
        ctx.save_for_backward(a_arr.shape, axis, keepdims)
        return a_arr.sum(axis=axis, keepdims=keepdims)

    @staticmethod
    def backward(ctx: Context, grad_output):
        ashape, axis, keepdims = ctx.saved_tensors
        # grad_output may be scalar or smaller shape; we need to broadcast to ashape
        if not keepdims and axis is not None:
            # if axis is an int, normalize to tuple
            if isinstance(axis, int):
                axis_tuple = (axis,)
            else:
                axis_tuple = tuple(axis)
            # Expand dims where reduction happened
            for ax in sorted(axis_tuple):
                grad_output = np.expand_dims(grad_output, ax)
        return np.broadcast_to(grad_output, ashape),

class Mean(Function):
    @staticmethod
    def forward(ctx: Context, a, axis=None, keepdims=False):
        a_arr = _ensure_ndarray(a)
        ctx.save_for_backward(a_arr.shape, axis, keepdims)
        return a_arr.mean(axis=axis, keepdims=keepdims)

    @staticmethod
    def backward(ctx: Context, grad_output):
        ashape, axis, keepdims = ctx.saved_tensors
        # compute factor = 1 / (number of elements summed)
        if axis is None:
            denom = np.prod(ashape)
            factor = 1.0 / denom
            return np.broadcast_to(grad_output * factor, ashape),
        # count elements along axis
        a_nd = len(ashape)
        if isinstance(axis, int):
            axis_tuple = (axis,)
        else:
            axis_tuple = tuple(axis)
        denom = 1
        for ax in axis_tuple:
            denom *= ashape[ax]
        factor = 1.0 / denom
        if not keepdims:
            for ax in sorted(axis_tuple):
                grad_output = np.expand_dims(grad_output, ax)
        return np.broadcast_to(grad_output * factor, ashape),

# -------------------
# Convenience API (factory wrappers)
# -------------------

def add(a, b):
    return Add.apply(a, b)

def sub(a, b):
    return Sub.apply(a, b)

def mul(a, b):
    return Mul.apply(a, b)

def div(a, b):
    return Div.apply(a, b)

def matmul(a, b):
    return MatMul.apply(a, b)

def reshape(a, *shape):
    # caller provides new shape as tuple; we pack as single arg
    return Reshape.apply(a, shape)

def transpose(a, axes=None):
    if axes is None:
        # default reverse
        axes = tuple(reversed(range(a.data.ndim)))
    return Transpose.apply(a, axes)

def sum_(a, axis=None, keepdims=False):
    return Sum.apply(a, axis, keepdims)

def mean(a, axis=None, keepdims=False):
    return Mean.apply(a, axis, keepdims)

# === AUTO-EXPAND HOOK ===
def expand():
    print(f'[AUTO_EXPAND] Module {__file__} has no custom logic. Placeholder activated.')