"""
Victor AGI Core Package
=======================

A production-grade, unified foundation for the Victor AGI system.

Modules:
    tensor: Unified tensor and autograd engine with NumPy backend
    trust: SAVE3 trust framework for secure module orchestration
    cognitive: Cognitive processing modules (reasoning, metacognition, emergence)
    serving: Model serving infrastructure with REST API
    utils: Core utilities and helpers

Version: 2.0.0 (Phase 2 & 3)
Author: Brandon "iambandobandz" Emery x Victor
License: Proprietary - Massive Magnetics / Ethica AI / BHeard Network
"""

__version__ = "2.0.0"
__author__ = "Brandon Emery x Victor"
__license__ = "Proprietary"

# Import main components for convenience
from victor_core.tensor import Tensor
from victor_core.trust import SAVE3Envelope, LegoContext
from victor_core.cognitive import ReasoningEngine, MetacognitiveLoop, EmergenceSystem

__all__ = [
    "Tensor",
    "SAVE3Envelope", 
    "LegoContext",
    "ReasoningEngine",
    "MetacognitiveLoop",
    "EmergenceSystem",
    "__version__",
]
