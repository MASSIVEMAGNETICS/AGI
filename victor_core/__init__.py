"""
Victor AGI Core Package
=======================

A production-grade, unified foundation for the Victor AGI system.

Modules:
    tensor: Unified tensor and autograd engine with NumPy backend
    trust: SAVE3 trust framework for secure module orchestration
    cognitive: Cognitive processing modules
    utils: Core utilities and helpers

Version: 1.0.0
Author: Brandon "iambandobandz" Emery x Victor
License: Proprietary - Massive Magnetics / Ethica AI / BHeard Network
"""

__version__ = "1.0.0"
__author__ = "Brandon Emery x Victor"
__license__ = "Proprietary"

# Import main components for convenience
from victor_core.tensor import Tensor
from victor_core.trust import SAVE3Envelope, LegoContext

__all__ = [
    "Tensor",
    "SAVE3Envelope", 
    "LegoContext",
    "__version__",
]
