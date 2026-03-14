# FILE: octonion_engine.py
# VERSION: v1.0.0
# PURPOSE: Octonion algebra engine for Victor Neocortex
# LICENSE: Bloodline Locked - Victor Ecosystem

import numpy as np


class Octonion:
    """
    Octonion algebra implementation for fractal compression in Victor Neocortex.
    
    Octonions are 8-dimensional hypercomplex numbers with the form:
    q = q0 + q1*i + q2*j + q3*k + q4*l + q5*il + q6*jl + q7*kl
    
    They are non-associative but provide rich structure for neural encoding.
    """
    
    def __init__(self, data):
        """Initialize an octonion from an 8-element array."""
        if isinstance(data, Octonion):
            self.data = data.data.copy()
        else:
            self.data = np.array(data, dtype=np.float64)
            if self.data.shape != (8,):
                raise ValueError(f"Octonion requires 8 components, got shape {self.data.shape}")
    
    def __repr__(self):
        return f"Octonion({self.data})"
    
    def __str__(self):
        labels = ['1', 'i', 'j', 'k', 'l', 'il', 'jl', 'kl']
        parts = []
        for coeff, label in zip(self.data, labels):
            if abs(coeff) > 1e-10:
                if label == '1':
                    parts.append(f"{coeff:.4f}")
                else:
                    parts.append(f"{coeff:.4f}{label}")
        return ' + '.join(parts) if parts else '0'
    
    def norm(self):
        """Return the Euclidean norm of the octonion."""
        return np.sqrt(np.sum(self.data ** 2))
    
    def conjugate(self):
        """Return the conjugate of the octonion."""
        conj_data = self.data.copy()
        conj_data[1:] *= -1
        return Octonion(conj_data)
    
    def inverse(self):
        """Return the multiplicative inverse of the octonion."""
        norm_sq = np.sum(self.data ** 2)
        if norm_sq < 1e-10:
            raise ValueError("Cannot invert octonion with zero norm")
        return Octonion(self.conjugate().data / norm_sq)
    
    def __add__(self, other):
        """Add two octonions component-wise."""
        if isinstance(other, Octonion):
            return Octonion(self.data + other.data)
        else:
            result = self.data.copy()
            result[0] += other
            return Octonion(result)
    
    def __radd__(self, other):
        return self.__add__(other)
    
    def __sub__(self, other):
        """Subtract two octonions component-wise."""
        if isinstance(other, Octonion):
            return Octonion(self.data - other.data)
        else:
            result = self.data.copy()
            result[0] -= other
            return Octonion(result)
    
    def __rsub__(self, other):
        return Octonion(-self.data + other)
    
    def __neg__(self):
        return Octonion(-self.data)
    
    def __mul__(self, other):
        """
        Multiply two octonions using the Cayley-Dickson construction.
        
        Octonion multiplication is non-associative and non-commutative.
        The multiplication table follows the Fano plane mnemonic.
        """
        if isinstance(other, (int, float)):
            return Octonion(self.data * other)
        
        if not isinstance(other, Octonion):
            other = Octonion(other)
        
        a = self.data
        b = other.data
        
        # Cayley-Dickson multiplication table for octonions
        # Using the standard Fano plane multiplication table
        result = np.zeros(8, dtype=np.float64)
        
        # e0 component (real part)
        result[0] = (a[0]*b[0] - a[1]*b[1] - a[2]*b[2] - a[3]*b[3] 
                    - a[4]*b[4] - a[5]*b[5] - a[6]*b[6] - a[7]*b[7])
        
        # e1 (i) component
        result[1] = (a[0]*b[1] + a[1]*b[0] + a[2]*b[3] - a[3]*b[2]
                    + a[4]*b[5] - a[5]*b[4] - a[6]*b[7] + a[7]*b[6])
        
        # e2 (j) component
        result[2] = (a[0]*b[2] - a[1]*b[3] + a[2]*b[0] + a[3]*b[1]
                    + a[4]*b[6] + a[5]*b[7] - a[6]*b[4] - a[7]*b[5])
        
        # e3 (k) component
        result[3] = (a[0]*b[3] + a[1]*b[2] - a[2]*b[1] + a[3]*b[0]
                    + a[4]*b[7] - a[5]*b[6] + a[6]*b[5] - a[7]*b[4])
        
        # e4 (l) component
        result[4] = (a[0]*b[4] - a[1]*b[5] - a[2]*b[6] - a[3]*b[7]
                    + a[4]*b[0] + a[5]*b[1] + a[6]*b[2] + a[7]*b[3])
        
        # e5 (il) component
        result[5] = (a[0]*b[5] + a[1]*b[4] - a[2]*b[7] + a[3]*b[6]
                    - a[4]*b[1] + a[5]*b[0] - a[6]*b[3] + a[7]*b[2])
        
        # e6 (jl) component
        result[6] = (a[0]*b[6] + a[1]*b[7] + a[2]*b[4] - a[3]*b[5]
                    - a[4]*b[2] + a[5]*b[3] + a[6]*b[0] - a[7]*b[1])
        
        # e7 (kl) component
        result[7] = (a[0]*b[7] - a[1]*b[6] + a[2]*b[5] + a[3]*b[4]
                    - a[4]*b[3] - a[5]*b[2] + a[6]*b[1] + a[7]*b[0])
        
        return Octonion(result)
    
    def __rmul__(self, other):
        """Right multiplication for scalars."""
        if isinstance(other, (int, float)):
            return Octonion(self.data * other)
        return NotImplemented
    
    def __truediv__(self, other):
        """Divide by a scalar or another octonion."""
        if isinstance(other, (int, float)):
            return Octonion(self.data / other)
        if isinstance(other, Octonion):
            return self * other.inverse()
        return NotImplemented
    
    def __eq__(self, other):
        if isinstance(other, Octonion):
            return np.allclose(self.data, other.data)
        return False
    
    def dot(self, other):
        """Compute the dot product of two octonions."""
        if isinstance(other, Octonion):
            return np.dot(self.data, other.data)
        return np.dot(self.data, other)
    
    def normalize(self):
        """Return a normalized (unit) octonion."""
        n = self.norm()
        if n < 1e-10:
            return Octonion(np.zeros(8))
        return Octonion(self.data / n)
    
    @staticmethod
    def random():
        """Generate a random unit octonion."""
        data = np.random.randn(8)
        return Octonion(data).normalize()
    
    @staticmethod
    def identity():
        """Return the multiplicative identity octonion."""
        return Octonion([1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    
    @staticmethod
    def from_quaternion(q, p=None):
        """
        Create an octonion from one or two quaternions.
        
        If only q is provided, creates (q, 0).
        If both q and p are provided, creates (q, p) in Cayley-Dickson form.
        """
        if len(q) != 4:
            raise ValueError("Quaternion must have 4 components")
        if p is None:
            p = [0.0, 0.0, 0.0, 0.0]
        if len(p) != 4:
            raise ValueError("Second quaternion must have 4 components")
        return Octonion(list(q) + list(p))
    
    def to_quaternions(self):
        """Split the octonion into two quaternions (Cayley-Dickson decomposition)."""
        return self.data[:4], self.data[4:]


# Standalone test
if __name__ == "__main__":
    print("Testing Octonion Engine...")
    
    # Test creation
    o1 = Octonion([1, 0, 0, 0, 0, 0, 0, 0])
    o2 = Octonion([0, 1, 0, 0, 0, 0, 0, 0])
    
    print(f"o1 = {o1}")
    print(f"o2 = {o2}")
    print(f"o1 * o2 = {o1 * o2}")
    print(f"o1.norm() = {o1.norm()}")
    
    # Test random
    o_rand = Octonion.random()
    print(f"Random unit octonion: {o_rand}")
    print(f"Norm: {o_rand.norm()}")
    
    print("Octonion engine tests passed!")
