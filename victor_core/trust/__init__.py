"""
Victor Core Trust Module
========================

SAVE3 trust framework for secure module orchestration and dependency management.

This module provides production-grade implementations of:
    - SAVE3Envelope: Secure message envelopes with HMAC-SHA256 signatures
    - TrustModelBeta: Time-decay and latency-weighted trust scoring
    - LegoContext: Service registry and dependency resolution
    - Module discovery and topological initialization ordering

Author: Brandon Emery x Victor
License: Proprietary - Massive Magnetics
"""

from victor_core.trust.save3 import (
    # Core classes
    SAVE3Envelope,
    SAVE3ModuleSpec,
    LegoContext,
    TrustModelBeta,
    # Functions
    discover_specs,
    resolve_init_order,
    lego_build,
    wrap_spec,
    # Errors
    Save3Error,
    SpecError,
    SignatureError,
    DependencyError,
)

__all__ = [
    "SAVE3Envelope",
    "SAVE3ModuleSpec",
    "LegoContext",
    "TrustModelBeta",
    "discover_specs",
    "resolve_init_order",
    "lego_build",
    "wrap_spec",
    "Save3Error",
    "SpecError",
    "SignatureError",
    "DependencyError",
]
