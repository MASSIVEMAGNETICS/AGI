# FILE: advanced_ai/__init__.py
# PURPOSE: Advanced AI module for Victor ecosystem

from .tensor_core import Tensor, ODEIntegrator, SGD, Adam, BLOODLINE_HASH
from .octonion_engine import Octonion
from .victor_holon_neocortex import (
    SDRLayer, TemporalMemory, FractalCompressor, OmegaTensorField, VictorHolonNeocortex
)

# Try to import holon_omega (requires torch and sentence-transformers)
try:
    from .holon_omega import (
        HLHFM, HolonΩ, DNA, LiquidGate, HoloEntry, SimpleHashEmbedder,
        _unit_norm, _circ_conv, _circ_deconv, _superpose, _cos
    )
    _HOLON_OMEGA_AVAILABLE = True
except ImportError:
    _HOLON_OMEGA_AVAILABLE = False
    HLHFM = None
    HolonΩ = None
    DNA = None
    LiquidGate = None
    HoloEntry = None
    SimpleHashEmbedder = None
    _unit_norm = None
    _circ_conv = None
    _circ_deconv = None
    _superpose = None
    _cos = None

__all__ = [
    'Tensor', 'ODEIntegrator', 'SGD', 'Adam',
    'BLOODLINE_HASH',
    'Octonion',
    'SDRLayer', 'TemporalMemory', 'FractalCompressor', 'OmegaTensorField', 'VictorHolonNeocortex',
]

# Add holon_omega exports if available
if _HOLON_OMEGA_AVAILABLE:
    __all__.extend([
        'HLHFM', 'HolonΩ', 'DNA', 'LiquidGate', 'HoloEntry', 'SimpleHashEmbedder',
        '_unit_norm', '_circ_conv', '_circ_deconv', '_superpose', '_cos'
    ])

__version__ = '2.2.0-HOLON-NEOCORTEX'
