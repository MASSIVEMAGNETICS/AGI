# Minimal "Lego" Tensor implementation for Vic-Torch
# Lightweight, numpy-backed, dependency-free.
# Provides basic API used by the repo (constructor, .data, .detach, mean, squeeze, shape()).
from __future__ import annotations

import numpy as np
from typing import Any, Optional, Tuple


class Tensor:
    """
    Minimal Tensor wrapper around numpy arrays.

    Supported:
    - Construction from scalars, lists, numpy arrays, or other Tensor.
    - .data -> raw numpy array
    - .numpy() -> raw numpy array
    - .detach() -> shallow copy Tensor (no autograd)
    - .mean(axis=...) -> Tensor
    - .squeeze(axis=None) -> Tensor
    - .shape() -> tuple (keeps parity with some existing code that calls preds.shape())
    - Basic arithmetic ops returning Tensor
    - .backward() stub that raises NotImplementedError (autograd not implemented)
    """

    def __init__(self, data: Any):
        if isinstance(data, Tensor):
            self._data = np.array(data.data, copy=True)
        else:
            self._data = np.array(data)

    @property
    def data(self) -> np.ndarray:
        return self._data

    def numpy(self) -> np.ndarray:
        return self._data

    def detach(self) -> "Tensor":
        # No autograd in this lightweight implementation; return a copy to mimic detach semantics.
        return Tensor(self._data.copy())

    def mean(self, axis: Optional[int] = None) -> "Tensor":
        return Tensor(self._data.mean(axis=axis))

    def squeeze(self, axis: Optional[int] = None) -> "Tensor":
        return Tensor(np.squeeze(self._data, axis=axis))

    def shape(self) -> Tuple[int, ...]:
        # Some existing code calls preds.shape() (callable), keep compatibility.
        return self._data.shape

    def reshape(self, *shape: int) -> "Tensor":
        return Tensor(self._data.reshape(*shape))

    def astype(self, dtype) -> "Tensor":
        return Tensor(self._data.astype(dtype))

    # Basic arithmetic
    def __add__(self, other: Any) -> "Tensor":
        o = other.data if isinstance(other, Tensor) else other
        return Tensor(self._data + o)

    def __radd__(self, other: Any) -> "Tensor":
        return self.__add__(other)

    def __sub__(self, other: Any) -> "Tensor":
        o = other.data if isinstance(other, Tensor) else other
        return Tensor(self._data - o)

    def __rsub__(self, other: Any) -> "Tensor":
        o = other.data if isinstance(other, Tensor) else other
        return Tensor(o - self._data)

    def __mul__(self, other: Any) -> "Tensor":
        o = other.data if isinstance(other, Tensor) else other
        return Tensor(self._data * o)

    def __rmul__(self, other: Any) -> "Tensor":
        return self.__mul__(other)

    def __truediv__(self, other: Any) -> "Tensor":
        o = other.data if isinstance(other, Tensor) else other
        return Tensor(self._data / o)

    def __rtruediv__(self, other: Any) -> "Tensor":
        o = other.data if isinstance(other, Tensor) else other
        return Tensor(o / self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __repr__(self) -> str:
        return f"Tensor(shape={self._data.shape}, dtype={self._data.dtype})"

    # Minimal stubs for autograd-related calls used in the codebase
    def backward(self, *args, **kwargs) -> None:
        raise NotImplementedError(
            "backward() is not implemented for Lego Tensor. This lightweight Tensor "
            "does not support autograd. Consider integrating a real autograd engine or "
            "refactoring training code to avoid calling backward() on this Tensor."
        )

    # Convenience
    def squeeze_inplace(self) -> "Tensor":
        self._data = np.squeeze(self._data)
        return self