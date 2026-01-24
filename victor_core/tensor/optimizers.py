"""
Extended Optimizer Library
===========================

Advanced optimizers for training neural networks.

Includes AdamW, Lookahead, LAMB, and other state-of-the-art optimizers.

Author: Brandon Emery x Victor
License: Proprietary - Massive Magnetics
"""

from typing import List, Dict, Tuple
import numpy as np
from victor_core.tensor.engine import Tensor, Optimizer


class AdamW(Optimizer):
    """
    AdamW optimizer (Adam with decoupled weight decay).
    
    Fixes weight decay implementation in Adam by decoupling it from
    the gradient-based update.
    
    Reference: "Decoupled Weight Decay Regularization" (Loshchilov & Hutter, 2019)
    
    Args:
        parameters: List of tensors to optimize
        lr: Learning rate (default: 0.001)
        betas: Coefficients for computing running averages (default: (0.9, 0.999))
        eps: Term added to denominator for numerical stability (default: 1e-8)
        weight_decay: Weight decay coefficient (default: 0.01)
        
    Example:
        >>> from victor_core.tensor import Tensor
        >>> from victor_core.tensor.optimizers import AdamW
        >>> params = [Tensor([[1.0, 2.0]], requires_grad=True)]
        >>> optimizer = AdamW(params, lr=0.001, weight_decay=0.01)
    """
    
    def __init__(
        self,
        parameters: List[Tensor],
        lr: float = 0.001,
        betas: Tuple[float, float] = (0.9, 0.999),
        eps: float = 1e-8,
        weight_decay: float = 0.01
    ):
        super().__init__(parameters, lr)
        self.beta1, self.beta2 = betas
        self.eps = eps
        self.weight_decay = weight_decay
        self.t = 0
        
        # First and second moment estimates
        self.m = {id(p): np.zeros_like(p.data) for p in parameters}
        self.v = {id(p): np.zeros_like(p.data) for p in parameters}
    
    def step(self) -> None:
        """Update parameters using AdamW algorithm."""
        self.t += 1
        
        for p in self.parameters:
            if p.grad is None:
                continue
            
            pid = id(p)
            grad = p.grad
            
            # Apply weight decay directly to parameters (decoupled)
            p.data *= (1 - self.lr * self.weight_decay)
            
            # Update biased first moment estimate
            self.m[pid] = self.beta1 * self.m[pid] + (1 - self.beta1) * grad
            
            # Update biased second raw moment estimate
            self.v[pid] = self.beta2 * self.v[pid] + (1 - self.beta2) * (grad ** 2)
            
            # Compute bias-corrected moment estimates
            m_hat = self.m[pid] / (1 - self.beta1 ** self.t)
            v_hat = self.v[pid] / (1 - self.beta2 ** self.t)
            
            # Update parameters
            p.data -= self.lr * m_hat / (np.sqrt(v_hat) + self.eps)


class Lookahead(Optimizer):
    """
    Lookahead optimizer wrapper.
    
    Wraps another optimizer and performs "look ahead" steps to improve
    convergence and reduce variance.
    
    Reference: "Lookahead Optimizer: k steps forward, 1 step back" (Zhang et al., 2019)
    
    Args:
        base_optimizer: Base optimizer to wrap
        k: Number of fast weights updates before slow weights update (default: 5)
        alpha: Slow weights step size (default: 0.5)
        
    Example:
        >>> from victor_core.tensor import Adam
        >>> from victor_core.tensor.optimizers import Lookahead
        >>> base = Adam(params, lr=0.001)
        >>> optimizer = Lookahead(base, k=5, alpha=0.5)
    """
    
    def __init__(
        self,
        base_optimizer: Optimizer,
        k: int = 5,
        alpha: float = 0.5
    ):
        self.base_optimizer = base_optimizer
        self.k = k
        self.alpha = alpha
        self.step_counter = 0
        
        # Store slow weights
        self.slow_weights = {
            id(p): p.data.copy()
            for p in base_optimizer.parameters
        }
    
    def step(self) -> None:
        """Perform Lookahead optimization step."""
        # Take a step with the base optimizer
        self.base_optimizer.step()
        self.step_counter += 1
        
        # Every k steps, update slow weights
        if self.step_counter % self.k == 0:
            for p in self.base_optimizer.parameters:
                pid = id(p)
                # Slow weights = slow_weights + alpha * (fast_weights - slow_weights)
                self.slow_weights[pid] += self.alpha * (p.data - self.slow_weights[pid])
                # Update fast weights to slow weights
                p.data = self.slow_weights[pid].copy()
    
    def zero_grad(self) -> None:
        """Zero gradients of base optimizer."""
        self.base_optimizer.zero_grad()
    
    @property
    def parameters(self):
        """Get parameters from base optimizer."""
        return self.base_optimizer.parameters


class LAMB(Optimizer):
    """
    LAMB optimizer (Layer-wise Adaptive Moments for Batch training).
    
    Designed for large batch training, LAMB adapts learning rate per layer
    based on the ratio of weight norm to gradient norm.
    
    Reference: "Large Batch Optimization for Deep Learning" (You et al., 2019)
    
    Args:
        parameters: List of tensors to optimize
        lr: Learning rate (default: 0.001)
        betas: Coefficients for computing running averages (default: (0.9, 0.999))
        eps: Term added to denominator (default: 1e-6)
        weight_decay: Weight decay coefficient (default: 0.01)
        
    Example:
        >>> from victor_core.tensor.optimizers import LAMB
        >>> optimizer = LAMB(params, lr=0.001, weight_decay=0.01)
    """
    
    def __init__(
        self,
        parameters: List[Tensor],
        lr: float = 0.001,
        betas: Tuple[float, float] = (0.9, 0.999),
        eps: float = 1e-6,
        weight_decay: float = 0.01
    ):
        super().__init__(parameters, lr)
        self.beta1, self.beta2 = betas
        self.eps = eps
        self.weight_decay = weight_decay
        self.t = 0
        
        # First and second moment estimates
        self.m = {id(p): np.zeros_like(p.data) for p in parameters}
        self.v = {id(p): np.zeros_like(p.data) for p in parameters}
    
    def step(self) -> None:
        """Update parameters using LAMB algorithm."""
        self.t += 1
        
        for p in self.parameters:
            if p.grad is None:
                continue
            
            pid = id(p)
            grad = p.grad
            
            # Add weight decay to gradient
            if self.weight_decay != 0:
                grad = grad + self.weight_decay * p.data
            
            # Update biased first moment estimate
            self.m[pid] = self.beta1 * self.m[pid] + (1 - self.beta1) * grad
            
            # Update biased second raw moment estimate
            self.v[pid] = self.beta2 * self.v[pid] + (1 - self.beta2) * (grad ** 2)
            
            # Compute bias-corrected moment estimates
            m_hat = self.m[pid] / (1 - self.beta1 ** self.t)
            v_hat = self.v[pid] / (1 - self.beta2 ** self.t)
            
            # Compute update
            update = m_hat / (np.sqrt(v_hat) + self.eps)
            
            # Layer-wise learning rate adaptation
            weight_norm = np.linalg.norm(p.data)
            update_norm = np.linalg.norm(update)
            
            if weight_norm > 0 and update_norm > 0:
                trust_ratio = weight_norm / update_norm
            else:
                trust_ratio = 1.0
            
            # Apply update with trust ratio
            p.data -= self.lr * trust_ratio * update


class RAdam(Optimizer):
    """
    RAdam optimizer (Rectified Adam).
    
    Automatically adjusts learning rate warmup based on variance of adaptive
    learning rate, improving training stability.
    
    Reference: "On the Variance of the Adaptive Learning Rate" (Liu et al., 2020)
    
    Args:
        parameters: List of tensors to optimize
        lr: Learning rate (default: 0.001)
        betas: Coefficients for computing running averages (default: (0.9, 0.999))
        eps: Term added to denominator (default: 1e-8)
        
    Example:
        >>> from victor_core.tensor.optimizers import RAdam
        >>> optimizer = RAdam(params, lr=0.001)
    """
    
    def __init__(
        self,
        parameters: List[Tensor],
        lr: float = 0.001,
        betas: Tuple[float, float] = (0.9, 0.999),
        eps: float = 1e-8
    ):
        super().__init__(parameters, lr)
        self.beta1, self.beta2 = betas
        self.eps = eps
        self.t = 0
        
        # First and second moment estimates
        self.m = {id(p): np.zeros_like(p.data) for p in parameters}
        self.v = {id(p): np.zeros_like(p.data) for p in parameters}
    
    def step(self) -> None:
        """Update parameters using RAdam algorithm."""
        self.t += 1
        
        # Compute maximum length of approximated SMA (simple moving average)
        rho_inf = 2 / (1 - self.beta2) - 1
        
        for p in self.parameters:
            if p.grad is None:
                continue
            
            pid = id(p)
            grad = p.grad
            
            # Update biased first moment estimate
            self.m[pid] = self.beta1 * self.m[pid] + (1 - self.beta1) * grad
            
            # Update biased second raw moment estimate
            self.v[pid] = self.beta2 * self.v[pid] + (1 - self.beta2) * (grad ** 2)
            
            # Compute bias-corrected first moment estimate
            m_hat = self.m[pid] / (1 - self.beta1 ** self.t)
            
            # Compute length of approximated SMA
            rho_t = rho_inf - 2 * self.t * (self.beta2 ** self.t) / (1 - self.beta2 ** self.t)
            
            # Check if variance is tractable
            if rho_t > 4:
                # Compute bias-corrected second moment estimate
                v_hat = np.sqrt(self.v[pid] / (1 - self.beta2 ** self.t))
                
                # Compute rectification term
                r_t = np.sqrt(
                    ((rho_t - 4) * (rho_t - 2) * rho_inf) /
                    ((rho_inf - 4) * (rho_inf - 2) * rho_t)
                )
                
                # Adaptive learning rate update
                p.data -= self.lr * r_t * m_hat / (v_hat + self.eps)
            else:
                # Use SGD update when variance not tractable
                p.data -= self.lr * m_hat
