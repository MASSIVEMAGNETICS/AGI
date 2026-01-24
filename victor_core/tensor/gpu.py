"""
GPU Acceleration Module
========================

CuPy backend for GPU-accelerated tensor operations.

Provides seamless GPU acceleration when CuPy is available,
falling back to NumPy for CPU operations.

Author: Brandon Emery x Victor
License: Proprietary - Massive Magnetics
"""

from typing import Union, Optional
import sys

# Try to import CuPy for GPU support
try:
    import cupy as cp
    CUPY_AVAILABLE = True
except ImportError:
    cp = None
    CUPY_AVAILABLE = False

import numpy as np


def is_gpu_available() -> bool:
    """
    Check if GPU acceleration is available.
    
    Returns:
        True if CuPy is installed and GPU is accessible
    """
    return CUPY_AVAILABLE


def get_array_module(array):
    """
    Get the appropriate array module (NumPy or CuPy).
    
    Args:
        array: Input array
        
    Returns:
        numpy or cupy module
    """
    if CUPY_AVAILABLE and isinstance(array, cp.ndarray):
        return cp
    return np


def to_gpu(data: Union[np.ndarray, 'Tensor']) -> Union[np.ndarray, 'cp.ndarray']:
    """
    Move data to GPU.
    
    Args:
        data: NumPy array or Tensor to move to GPU
        
    Returns:
        CuPy array on GPU (or NumPy array if GPU not available)
        
    Example:
        >>> from victor_core.tensor import Tensor
        >>> from victor_core.tensor.gpu import to_gpu
        >>> x = Tensor([1, 2, 3])
        >>> x_gpu = to_gpu(x.data)
    """
    if not CUPY_AVAILABLE:
        print("Warning: CuPy not available, returning CPU array", file=sys.stderr)
        if hasattr(data, 'data'):
            return data.data
        return data
    
    if hasattr(data, 'data'):
        # It's a Tensor
        return cp.asarray(data.data)
    
    return cp.asarray(data)


def to_cpu(data: Union[np.ndarray, 'cp.ndarray']) -> np.ndarray:
    """
    Move data to CPU.
    
    Args:
        data: CuPy array or NumPy array
        
    Returns:
        NumPy array on CPU
        
    Example:
        >>> x_gpu = to_gpu(x)
        >>> x_cpu = to_cpu(x_gpu)
    """
    if CUPY_AVAILABLE and isinstance(data, cp.ndarray):
        return cp.asnumpy(data)
    return np.asarray(data)


def synchronize():
    """Synchronize GPU operations (wait for completion)."""
    if CUPY_AVAILABLE:
        cp.cuda.Stream.null.synchronize()


class GPUTensor:
    """
    GPU-accelerated tensor wrapper.
    
    Automatically uses CuPy when available, falls back to NumPy.
    
    Example:
        >>> from victor_core.tensor.gpu import GPUTensor
        >>> x = GPUTensor([1, 2, 3])
        >>> y = x * 2
        >>> z = y + x
        >>> result = z.cpu()  # Move back to CPU
    """
    
    def __init__(self, data, device='auto'):
        """
        Initialize GPU tensor.
        
        Args:
            data: Input data (list, NumPy array, or CuPy array)
            device: 'cpu', 'gpu', or 'auto' (default: auto-detect)
        """
        if device == 'gpu' and not CUPY_AVAILABLE:
            raise RuntimeError("CuPy not available for GPU operations")
        
        use_gpu = (device == 'gpu') or (device == 'auto' and CUPY_AVAILABLE)
        
        if use_gpu:
            self.data = cp.asarray(data)
            self.xp = cp
        else:
            self.data = np.asarray(data)
            self.xp = np
        
        self.device = 'gpu' if use_gpu else 'cpu'
    
    def __add__(self, other):
        if isinstance(other, GPUTensor):
            return GPUTensor(self.data + other.data, device=self.device)
        return GPUTensor(self.data + other, device=self.device)
    
    def __mul__(self, other):
        if isinstance(other, GPUTensor):
            return GPUTensor(self.data * other.data, device=self.device)
        return GPUTensor(self.data * other, device=self.device)
    
    def __matmul__(self, other):
        if isinstance(other, GPUTensor):
            return GPUTensor(self.data @ other.data, device=self.device)
        return GPUTensor(self.data @ other, device=self.device)
    
    def sum(self, **kwargs):
        """Sum tensor elements."""
        return GPUTensor(self.data.sum(**kwargs), device=self.device)
    
    def mean(self, **kwargs):
        """Mean of tensor elements."""
        return GPUTensor(self.data.mean(**kwargs), device=self.device)
    
    def cpu(self):
        """Move tensor to CPU."""
        if self.device == 'cpu':
            return self.data
        return to_cpu(self.data)
    
    def gpu(self):
        """Move tensor to GPU."""
        if self.device == 'gpu':
            return self.data
        return to_gpu(self.data)
    
    @property
    def shape(self):
        """Get tensor shape."""
        return self.data.shape
    
    def __repr__(self):
        return f"GPUTensor(device={self.device}, shape={self.shape})"


def print_gpu_info():
    """Print GPU device information."""
    if not CUPY_AVAILABLE:
        print("CuPy not available - GPU acceleration disabled")
        return
    
    print("GPU Acceleration Available")
    print(f"CuPy version: {cp.__version__}")
    
    device = cp.cuda.Device()
    print(f"GPU Device: {device.id}")
    print(f"GPU Name: {cp.cuda.runtime.getDeviceProperties(device.id)['name'].decode()}")
    
    mem_info = cp.cuda.runtime.memGetInfo()
    free_mem = mem_info[0] / (1024 ** 3)  # Convert to GB
    total_mem = mem_info[1] / (1024 ** 3)
    print(f"GPU Memory: {free_mem:.2f} GB free / {total_mem:.2f} GB total")
