# FILE: advanced_ai/octonion_engine.py
# VERSION: v1.0.0
# PURPOSE: Octonion mathematics engine for Victor Neocortex
# LICENSE: Bloodline Locked - Victor Ecosystem

import numpy as np
from typing import Union


class Octonion:
    """
    Octonion class implementing 8-dimensional hypercomplex numbers.
    
    Octonions extend quaternions and have the form:
    q = a + bi + cj + dk + el + fm + gn + ho
    
    They are non-associative but normed division algebra.
    """
    
    # Cayley-Dickson multiplication table for octonion basis elements
    # e_i * e_j = MULT_TABLE[i][j] (sign, index)
    # Index 0 = 1 (real), indices 1-7 = imaginary units
    MULT_TABLE = [
        # e0  e1   e2   e3   e4   e5   e6   e7
        [(1,0), (1,1), (1,2), (1,3), (1,4), (1,5), (1,6), (1,7)],  # e0 *
        [(1,1), (-1,0), (1,3), (-1,2), (1,5), (-1,4), (-1,7), (1,6)],  # e1 *
        [(1,2), (-1,3), (-1,0), (1,1), (1,6), (1,7), (-1,4), (-1,5)],  # e2 *
        [(1,3), (1,2), (-1,1), (-1,0), (1,7), (-1,6), (1,5), (-1,4)],  # e3 *
        [(1,4), (-1,5), (-1,6), (-1,7), (-1,0), (1,1), (1,2), (1,3)],  # e4 *
        [(1,5), (1,4), (-1,7), (1,6), (-1,1), (-1,0), (-1,3), (1,2)],  # e5 *
        [(1,6), (1,7), (1,4), (-1,5), (-1,2), (1,3), (-1,0), (-1,1)],  # e6 *
        [(1,7), (-1,6), (1,5), (1,4), (-1,3), (-1,2), (1,1), (-1,0)],  # e7 *
    ]
    
    def __init__(self, data: Union[np.ndarray, list] = None):
        """
        Initialize an Octonion.
        
        Args:
            data: 8-element array [a, b, c, d, e, f, g, h] where
                  q = a + bi + cj + dk + el + fm + gn + ho
                  If None, creates zero octonion.
        """
        if data is None:
            self.data = np.zeros(8, dtype=np.float64)
        else:
            self.data = np.asarray(data, dtype=np.float64)
            if self.data.shape != (8,):
                raise ValueError(f"Octonion requires exactly 8 components, got shape {self.data.shape}")
    
    def __repr__(self) -> str:
        return f"Octonion({self.data})"
    
    def __str__(self) -> str:
        labels = ['', 'i', 'j', 'k', 'l', 'm', 'n', 'o']
        parts = []
        for i, (val, label) in enumerate(zip(self.data, labels)):
            if abs(val) > 1e-10:
                if i == 0:
                    parts.append(f"{val:.4f}")
                else:
                    sign = '+' if val >= 0 else ''
                    parts.append(f"{sign}{val:.4f}{label}")
        return ''.join(parts) if parts else "0"
    
    def __eq__(self, other: 'Octonion') -> bool:
        if not isinstance(other, Octonion):
            return False
        return np.allclose(self.data, other.data)
    
    def __add__(self, other: 'Octonion') -> 'Octonion':
        """Add two octonions component-wise."""
        if isinstance(other, (int, float)):
            result = self.data.copy()
            result[0] += other
            return Octonion(result)
        if not isinstance(other, Octonion):
            return NotImplemented
        return Octonion(self.data + other.data)
    
    def __radd__(self, other) -> 'Octonion':
        return self.__add__(other)
    
    def __sub__(self, other: 'Octonion') -> 'Octonion':
        """Subtract two octonions component-wise."""
        if isinstance(other, (int, float)):
            result = self.data.copy()
            result[0] -= other
            return Octonion(result)
        if not isinstance(other, Octonion):
            return NotImplemented
        return Octonion(self.data - other.data)
    
    def __rsub__(self, other) -> 'Octonion':
        if isinstance(other, (int, float)):
            result = -self.data.copy()
            result[0] += other
            return Octonion(result)
        return NotImplemented
    
    def __neg__(self) -> 'Octonion':
        """Negate an octonion."""
        return Octonion(-self.data)
    
    def __mul__(self, other: Union['Octonion', float, int]) -> 'Octonion':
        """
        Multiply two octonions using Cayley-Dickson construction.
        
        Note: Octonion multiplication is non-associative and non-commutative.
        """
        if isinstance(other, (int, float)):
            return Octonion(self.data * other)
        
        if not isinstance(other, Octonion):
            return NotImplemented
        
        result = np.zeros(8, dtype=np.float64)
        
        for i in range(8):
            for j in range(8):
                sign, idx = self.MULT_TABLE[i][j]
                result[idx] += sign * self.data[i] * other.data[j]
        
        return Octonion(result)
    
    def __rmul__(self, other: Union[float, int]) -> 'Octonion':
        """Right multiplication by scalar."""
        if isinstance(other, (int, float)):
            return Octonion(self.data * other)
        return NotImplemented
    
    def __truediv__(self, other: Union['Octonion', float, int]) -> 'Octonion':
        """Divide octonion by scalar or another octonion."""
        if isinstance(other, (int, float)):
            return Octonion(self.data / other)
        if isinstance(other, Octonion):
            return self * other.inverse()
        return NotImplemented
    
    def conjugate(self) -> 'Octonion':
        """
        Return the conjugate of this octonion.
        
        conj(a + bi + cj + dk + el + fm + gn + ho) = a - bi - cj - dk - el - fm - gn - ho
        """
        result = self.data.copy()
        result[1:] = -result[1:]
        return Octonion(result)
    
    def norm(self) -> float:
        """
        Return the norm (magnitude) of this octonion.
        
        |q| = sqrt(sum of squares of all components)
        """
        return float(np.sqrt(np.sum(self.data ** 2)))
    
    def norm_squared(self) -> float:
        """Return the squared norm of this octonion."""
        return float(np.sum(self.data ** 2))
    
    def normalize(self) -> 'Octonion':
        """Return a unit octonion in the same direction."""
        n = self.norm()
        if n < 1e-10:
            return Octonion(np.zeros(8))
        return Octonion(self.data / n)
    
    def inverse(self) -> 'Octonion':
        """
        Return the multiplicative inverse of this octonion.
        
        q^(-1) = conj(q) / |q|^2
        """
        n_sq = self.norm_squared()
        if n_sq < 1e-20:
            raise ZeroDivisionError("Cannot invert octonion with zero norm")
        return Octonion(self.conjugate().data / n_sq)
    
    @classmethod
    def unit(cls, index: int = 0) -> 'Octonion':
        """Create a unit octonion with 1 in the specified component."""
        data = np.zeros(8)
        data[index] = 1.0
        return cls(data)
    
    @classmethod
    def random(cls, seed: int = None) -> 'Octonion':
        """Create a random octonion."""
        if seed is not None:
            np.random.seed(seed)
        return cls(np.random.randn(8))
    
    @classmethod
    def from_quaternion(cls, q: np.ndarray) -> 'Octonion':
        """Create an octonion from a quaternion (4 components)."""
        data = np.zeros(8)
        data[:4] = q
        return cls(data)
    
    def real(self) -> float:
        """Return the real (scalar) part of the octonion."""
        return self.data[0]
    
    def imag(self) -> np.ndarray:
        """Return the imaginary (vector) part of the octonion."""
        return self.data[1:].copy()
    
    def dot(self, other: 'Octonion') -> float:
        """Compute the dot product with another octonion."""
        if not isinstance(other, Octonion):
            raise TypeError("Can only dot product with another Octonion")
        return float(np.dot(self.data, other.data))
    
    def exp(self) -> 'Octonion':
        """
        Compute the exponential of this octonion.
        
        exp(q) = exp(a) * (cos|v| + v/|v| * sin|v|)
        where q = a + v, a is scalar, v is vector part
        """
        a = self.data[0]
        v = self.data[1:]
        v_norm = np.sqrt(np.sum(v ** 2))
        
        exp_a = np.exp(a)
        
        if v_norm < 1e-10:
            result = np.zeros(8)
            result[0] = exp_a
            return Octonion(result)
        
        result = np.zeros(8)
        result[0] = exp_a * np.cos(v_norm)
        result[1:] = exp_a * np.sin(v_norm) * v / v_norm
        return Octonion(result)
    
    def log(self) -> 'Octonion':
        """
        Compute the natural logarithm of this octonion.
        
        log(q) = log|q| + v/|v| * arccos(a/|q|)
        """
        q_norm = self.norm()
        if q_norm < 1e-10:
            raise ValueError("Cannot take log of zero octonion")
        
        a = self.data[0]
        v = self.data[1:]
        v_norm = np.sqrt(np.sum(v ** 2))
        
        result = np.zeros(8)
        result[0] = np.log(q_norm)
        
        if v_norm > 1e-10:
            theta = np.arccos(np.clip(a / q_norm, -1, 1))
            result[1:] = theta * v / v_norm
        
        return Octonion(result)
    
    def tolist(self) -> list:
        """Convert to Python list."""
        return self.data.tolist()
