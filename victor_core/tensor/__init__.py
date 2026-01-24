"""
Victor Core Tensor Module
=========================

Unified tensor and autograd engine with production-grade features.

This module consolidates best practices from multiple tensor implementations
(tensor_autograd_engine.py, victorch, Qwen, OmegaTensor) into a single,
robust, well-tested engine.

Key Features:
    - Complete backward pass with topological sort
    - Broadcasting support with gradient reduction
    - Standard operations (add, mul, matmul, sum, mean, reshape, transpose)
    - Activation functions (ReLU, Sigmoid, Tanh, Softmax)
    - Optimizers (SGD, Adam, RMSprop)
    - JVP (Jacobian-Vector Products) for forward-mode AD
    - Save/load functionality for model checkpoints
    - Zero external dependencies (NumPy only)

Example:
    >>> from victor_core.tensor import Tensor
    >>> x = Tensor([1.0, 2.0, 3.0], requires_grad=True)
    >>> y = (x * 2).sum()
    >>> y.backward()
    >>> print(x.grad)  # [2., 2., 2.]
"""

from victor_core.tensor.engine import (
    Tensor,
    no_grad,
    # Optimizers
    Optimizer,
    SGD,
    Adam,
    RMSprop,
    # Activation functions
    relu,
    sigmoid,
    tanh,
    softmax,
    # Loss functions
    mse_loss,
    binary_cross_entropy,
    cross_entropy,
)

__all__ = [
    "Tensor",
    "no_grad",
    "Optimizer",
    "SGD",
    "Adam", 
    "RMSprop",
    "relu",
    "sigmoid",
    "tanh",
    "softmax",
    "mse_loss",
    "binary_cross_entropy",
    "cross_entropy",
]
