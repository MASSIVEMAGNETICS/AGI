"""
Production-Grade SAVE3 Trust Framework
=======================================

Secure module orchestration with trust scoring, signature verification,
and dependency resolution.

This consolidates and enhances the existing SAVE3 implementation with:
    - TrustModelBeta: Time-decay and latency-weighted trust metrics
    - SAVE3Envelope: Cryptographic message envelopes with HMAC-SHA256
    - LegoContext: Service registry with provenance tracking
    - Module discovery: Automatic scanning and compatibility checking
    - Dependency resolution: Topological sort with cycle detection

Author: Brandon Emery x Victor
License: Proprietary - Massive Magnetics / Ethica AI / BHeard Network
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Tuple, Callable, Set
import hashlib
import hmac
import importlib.util
import inspect
import json
import os
import sys
import time
import warnings


# =============================================================================
# Error Types
# =============================================================================

class Save3Error(Exception):
    """Base exception for SAVE3 framework."""
    pass


class SpecError(Save3Error):
    """Invalid module specification."""
    pass


class SignatureError(Save3Error):
    """Signature verification failed."""
    pass


class DependencyError(Save3Error):
    """Dependency resolution failed."""
    pass


class TrustError(Save3Error):
    """Trust score below threshold."""
    pass


# =============================================================================
# Utility Functions
# =============================================================================

def _sha256_bytes(b: bytes) -> str:
    """Compute SHA-256 hash of bytes."""
    return hashlib.sha256(b).hexdigest()


def _now_iso() -> str:
    """Get current timestamp in ISO format."""
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def _safe_json_dumps(obj: Any) -> str:
    """
    Serialize object to canonical JSON string.
    
    Uses deterministic serialization for consistent hashing.
    """
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _coerce_semver(v: str) -> Tuple[int, int, int]:
    """
    Parse semantic version string to tuple.
    
    Args:
        v: Version string (e.g., "v1.2.3" or "1.2.3")
        
    Returns:
        Tuple of (major, minor, patch)
        
    Raises:
        SpecError: If version format is invalid
    """
    if not isinstance(v, str) or not v:
        raise SpecError(f"Invalid version: {v!r}")
    
    s = v.strip()
    if s.startswith("v"):
        s = s[1:]
    
    parts = s.split(".")
    if len(parts) != 3:
        raise SpecError(f"Version must be semver 'x.y.z' (got {v!r})")
    
    try:
        return (int(parts[0]), int(parts[1]), int(parts[2]))
    except Exception as e:
        raise SpecError(f"Version parts must be ints (got {v!r})") from e


def _semver_ge(a: str, b: str) -> bool:
    """Check if version a >= version b."""
    return _coerce_semver(a) >= _coerce_semver(b)


def _semver_lt(a: str, b: str) -> bool:
    """Check if version a < version b."""
    return _coerce_semver(a) < _coerce_semver(b)


# =============================================================================
# Trust Model Beta
# =============================================================================

@dataclass
class TrustEvent:
    """
    Record of a trust-affecting event.
    
    Attributes:
        timestamp: Unix timestamp of event
        event_type: Type of event (success, failure, timeout, etc.)
        score_delta: Change in trust score
        latency_ms: Response latency in milliseconds
        metadata: Additional event data
    """
    timestamp: float
    event_type: str  # "success", "failure", "timeout", "violation"
    score_delta: float
    latency_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class TrustModelBeta:
    """
    Time-decay and latency-weighted trust scoring model.
    
    Tracks trust scores for entities with exponential time decay and
    latency penalties. Useful for service reliability tracking.
    
    Args:
        decay_halflife: Time (seconds) for trust to decay by half
        latency_penalty_threshold: Latency (ms) above which penalties apply
        latency_penalty_rate: Score reduction per ms above threshold
        min_trust: Minimum trust score (floor)
        max_trust: Maximum trust score (ceiling)
        
    Example:
        >>> trust = TrustModelBeta()
        >>> trust.record_success("service_a", latency_ms=50)
        >>> score = trust.get_trust("service_a")
        >>> print(score > 0)  # True
    """
    
    def __init__(
        self,
        decay_halflife: float = 3600.0,  # 1 hour
        latency_penalty_threshold: float = 1000.0,  # 1 second
        latency_penalty_rate: float = 0.001,
        min_trust: float = 0.0,
        max_trust: float = 100.0,
    ):
        self.decay_halflife = decay_halflife
        self.latency_penalty_threshold = latency_penalty_threshold
        self.latency_penalty_rate = latency_penalty_rate
        self.min_trust = min_trust
        self.max_trust = max_trust
        
        # Entity trust scores and event history
        self._scores: Dict[str, float] = {}
        self._events: Dict[str, List[TrustEvent]] = {}
        self._last_update: Dict[str, float] = {}
    
    def _apply_decay(self, entity_id: str, current_time: float) -> None:
        """Apply exponential time decay to trust score."""
        if entity_id not in self._last_update:
            return
        
        elapsed = current_time - self._last_update[entity_id]
        if elapsed <= 0:
            return
        
        # Exponential decay: score * 0.5^(elapsed / halflife)
        decay_factor = 0.5 ** (elapsed / self.decay_halflife)
        self._scores[entity_id] *= decay_factor
    
    def record_success(
        self,
        entity_id: str,
        score_gain: float = 5.0,
        latency_ms: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> float:
        """
        Record successful interaction with entity.
        
        Args:
            entity_id: Unique identifier for entity
            score_gain: Base score increase for success
            latency_ms: Response latency in milliseconds
            metadata: Additional event data
            
        Returns:
            New trust score after update
        """
        current_time = time.time()
        self._apply_decay(entity_id, current_time)
        
        # Initialize if new entity
        if entity_id not in self._scores:
            self._scores[entity_id] = 50.0  # Start at neutral
            self._events[entity_id] = []
        
        # Apply latency penalty if above threshold
        latency_penalty = 0.0
        if latency_ms > self.latency_penalty_threshold:
            excess_latency = latency_ms - self.latency_penalty_threshold
            latency_penalty = excess_latency * self.latency_penalty_rate
        
        # Update score
        net_delta = score_gain - latency_penalty
        self._scores[entity_id] += net_delta
        self._scores[entity_id] = max(
            self.min_trust,
            min(self.max_trust, self._scores[entity_id])
        )
        
        # Record event
        event = TrustEvent(
            timestamp=current_time,
            event_type="success",
            score_delta=net_delta,
            latency_ms=latency_ms,
            metadata=metadata or {}
        )
        self._events[entity_id].append(event)
        self._last_update[entity_id] = current_time
        
        return self._scores[entity_id]
    
    def record_failure(
        self,
        entity_id: str,
        score_penalty: float = 10.0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> float:
        """
        Record failed interaction with entity.
        
        Args:
            entity_id: Unique identifier for entity
            score_penalty: Score decrease for failure
            metadata: Additional event data
            
        Returns:
            New trust score after update
        """
        current_time = time.time()
        self._apply_decay(entity_id, current_time)
        
        # Initialize if new entity
        if entity_id not in self._scores:
            self._scores[entity_id] = 50.0
            self._events[entity_id] = []
        
        # Apply penalty
        self._scores[entity_id] -= score_penalty
        self._scores[entity_id] = max(self.min_trust, self._scores[entity_id])
        
        # Record event
        event = TrustEvent(
            timestamp=current_time,
            event_type="failure",
            score_delta=-score_penalty,
            metadata=metadata or {}
        )
        self._events[entity_id].append(event)
        self._last_update[entity_id] = current_time
        
        return self._scores[entity_id]
    
    def get_trust(self, entity_id: str) -> float:
        """
        Get current trust score for entity.
        
        Args:
            entity_id: Unique identifier for entity
            
        Returns:
            Trust score (decay applied)
        """
        current_time = time.time()
        self._apply_decay(entity_id, current_time)
        return self._scores.get(entity_id, 50.0)  # Default neutral score
    
    def get_events(
        self,
        entity_id: str,
        since: Optional[float] = None,
        limit: Optional[int] = None
    ) -> List[TrustEvent]:
        """
        Get event history for entity.
        
        Args:
            entity_id: Unique identifier for entity
            since: Only return events after this timestamp
            limit: Maximum number of events to return
            
        Returns:
            List of TrustEvent objects
        """
        events = self._events.get(entity_id, [])
        
        if since is not None:
            events = [e for e in events if e.timestamp >= since]
        
        if limit is not None:
            events = events[-limit:]
        
        return events
    
    def check_threshold(
        self,
        entity_id: str,
        min_score: float = 30.0
    ) -> bool:
        """
        Check if entity trust meets minimum threshold.
        
        Args:
            entity_id: Unique identifier for entity
            min_score: Minimum acceptable trust score
            
        Returns:
            True if trust >= threshold
            
        Raises:
            TrustError: If trust below threshold
        """
        score = self.get_trust(entity_id)
        if score < min_score:
            raise TrustError(
                f"Entity {entity_id} trust {score:.1f} below threshold {min_score}"
            )
        return True


# =============================================================================
# SAVE3 Envelope
# =============================================================================

@dataclass
class SAVE3Envelope:
    """
    Secure message envelope with cryptographic signatures.
    
    Provides integrity verification and optional authentication via HMAC-SHA256.
    
    Attributes:
        schema: Schema identifier (always "SAVE3-ENVELOPE")
        schema_version: Schema version (e.g., "v2.0.0")
        created_at: ISO timestamp of creation
        module_id: Unique module identifier
        module_name: Human-readable module name
        module_version: Semantic version of module
        author: Module author
        license: License identifier
        payload_type: Type of payload data
        payload: Arbitrary payload data
        payload_sha256: SHA-256 hash of payload
        signature_alg: Signature algorithm ("none" or "hmac-sha256")
        signature: Cryptographic signature (hex string)
        
    Example:
        >>> env = SAVE3Envelope(
        ...     module_id="test.module",
        ...     module_name="Test",
        ...     module_version="v1.0.0",
        ...     payload={"data": "hello"}
        ... )
        >>> env.finalize()
        >>> env.verify()  # No secret needed for unsigned
    """
    schema: str = "SAVE3-ENVELOPE"
    schema_version: str = "v2.0.0"
    created_at: str = field(default_factory=_now_iso)
    
    module_id: str = ""
    module_name: str = ""
    module_version: str = ""
    author: str = "Brandon x Victor"
    license: str = "Proprietary"
    
    payload_type: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    
    payload_sha256: str = ""
    signature_alg: str = "none"
    signature: str = ""
    
    def finalize(self, secret: Optional[bytes] = None) -> SAVE3Envelope:
        """
        Finalize envelope by computing hash and signature.
        
        Args:
            secret: Shared secret for HMAC signature (optional)
            
        Returns:
            Self for chaining
            
        Example:
            >>> env = SAVE3Envelope(module_id="test", payload={"x": 1})
            >>> env.finalize(secret=b"shared_secret")
        """
        # Compute canonical payload hash
        canonical_payload = _safe_json_dumps(self.payload).encode("utf-8")
        self.payload_sha256 = _sha256_bytes(canonical_payload)
        
        # Compute signature if secret provided
        if secret:
            self.signature_alg = "hmac-sha256"
            self.signature = hmac.new(
                secret,
                canonical_payload,
                hashlib.sha256
            ).hexdigest()
        else:
            self.signature_alg = "none"
            self.signature = ""
        
        return self
    
    def verify(self, secret: Optional[bytes] = None) -> None:
        """
        Verify envelope integrity and signature.
        
        Args:
            secret: Shared secret for HMAC verification (if signed)
            
        Raises:
            SignatureError: If verification fails
            
        Example:
            >>> env.verify(secret=b"shared_secret")
        """
        # Verify payload hash
        canonical_payload = _safe_json_dumps(self.payload).encode("utf-8")
        sha = _sha256_bytes(canonical_payload)
        
        if sha != self.payload_sha256:
            raise SignatureError(
                "Payload SHA mismatch (envelope tampered or not finalized)"
            )
        
        # Verify signature if present
        if self.signature_alg == "none":
            return
        
        if self.signature_alg != "hmac-sha256":
            raise SignatureError(f"Unsupported signature_alg: {self.signature_alg}")
        
        if not secret:
            raise SignatureError("Signature requires secret but none provided")
        
        expected = hmac.new(secret, canonical_payload, hashlib.sha256).hexdigest()
        
        if not hmac.compare_digest(expected, self.signature):
            raise SignatureError("Bad signature")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert envelope to dictionary."""
        return asdict(self)
    
    @staticmethod
    def from_dict(d: Dict[str, Any]) -> SAVE3Envelope:
        """
        Create envelope from dictionary.
        
        Args:
            d: Dictionary with envelope fields
            
        Returns:
            SAVE3Envelope instance
            
        Raises:
            SpecError: If dictionary format is invalid
        """
        try:
            return SAVE3Envelope(**d)
        except TypeError as e:
            raise SpecError(f"Bad envelope dict: {e}") from e


# =============================================================================
# Module Specification
# =============================================================================

@dataclass
class SAVE3ModuleSpec:
    """
    Module specification for dependency resolution.
    
    Defines what a module provides and requires, enabling automatic
    dependency resolution and initialization ordering.
    
    Attributes:
        schema: Schema identifier
        schema_version: Schema version
        module_id: Unique module identifier (e.g., "victor.tensor")
        name: Human-readable name
        version: Semantic version
        entrypoint: File path to module (set by discovery)
        provides: List of capabilities this module provides
        requires: List of capabilities this module requires
        requires_versions: Version constraints for required capabilities
        description: Module description
        tags: Classification tags
        
    Example:
        >>> spec = SAVE3ModuleSpec(
        ...     module_id="example.module",
        ...     name="Example Module",
        ...     version="v1.0.0",
        ...     provides=["example.service"],
        ...     requires=["logging.service"],
        ...     requires_versions={
        ...         "logging.service": {"min": "v1.0.0", "max_exclusive": "v2.0.0"}
        ...     }
        ... )
        >>> spec.validate()
    """
    schema: str = "SAVE3-MODULE-SPEC"
    schema_version: str = "v2.0.0"
    
    module_id: str = ""
    name: str = ""
    version: str = ""
    entrypoint: str = ""
    provides: List[str] = field(default_factory=list)
    requires: List[str] = field(default_factory=list)
    requires_versions: Dict[str, Dict[str, str]] = field(default_factory=dict)
    
    description: str = ""
    tags: List[str] = field(default_factory=list)
    
    def validate(self) -> None:
        """
        Validate specification fields.
        
        Raises:
            SpecError: If specification is invalid
        """
        if not self.module_id or not isinstance(self.module_id, str):
            raise SpecError("module_id required")
        
        if not self.name:
            raise SpecError("name required")
        
        # Validate version format
        _coerce_semver(self.version)
        
        # Validate provides list
        if not isinstance(self.provides, list):
            raise SpecError("provides must be list[str]")
        if not all(isinstance(x, str) and x for x in self.provides):
            raise SpecError("provides must be non-empty strings")
        
        # Validate requires list
        if not isinstance(self.requires, list):
            raise SpecError("requires must be list[str]")
        if not all(isinstance(x, str) and x for x in self.requires):
            raise SpecError("requires must be non-empty strings")
        
        # Validate version constraints
        if not isinstance(self.requires_versions, dict):
            raise SpecError("requires_versions must be dict")
        
        for cap, constraints in self.requires_versions.items():
            if cap not in self.requires:
                raise SpecError(
                    f"requires_versions specified for {cap!r} but cap not in requires"
                )
            
            if not isinstance(constraints, dict):
                raise SpecError(f"constraint for {cap!r} must be dict")
            
            if "min" in constraints:
                _coerce_semver(constraints["min"])
            
            if "max_exclusive" in constraints:
                _coerce_semver(constraints["max_exclusive"])


# =============================================================================
# Lego Context (Service Registry)
# =============================================================================

class LegoContext:
    """
    Service registry and dependency injection container.
    
    Modules register capabilities they provide and request capabilities
    they need. The context tracks provenance and enforces uniqueness.
    
    Example:
        >>> ctx = LegoContext()
        >>> spec = SAVE3ModuleSpec(
        ...     module_id="provider",
        ...     name="Provider",
        ...     version="v1.0.0",
        ...     provides=["service.a"]
        ... )
        >>> ctx.provide("service.a", my_service, spec)
        >>> service = ctx.require("service.a")
    """
    
    def __init__(self) -> None:
        self._services: Dict[str, Any] = {}
        self._specs_by_cap: Dict[str, SAVE3ModuleSpec] = {}
    
    def provide(
        self,
        capability: str,
        obj: Any,
        provider_spec: SAVE3ModuleSpec
    ) -> None:
        """
        Register a capability with the context.
        
        Args:
            capability: Capability name (e.g., "logging.service")
            obj: Object providing the capability
            provider_spec: Specification of providing module
            
        Raises:
            DependencyError: If capability already registered
        """
        if capability in self._services:
            existing = self._specs_by_cap[capability]
            raise DependencyError(
                f"Capability {capability!r} already provided by {existing.module_id}"
            )
        
        self._services[capability] = obj
        self._specs_by_cap[capability] = provider_spec
    
    def require(self, capability: str) -> Any:
        """
        Request a capability from the context.
        
        Args:
            capability: Capability name to request
            
        Returns:
            Object providing the capability
            
        Raises:
            DependencyError: If capability not available
        """
        if capability not in self._services:
            raise DependencyError(f"Missing required capability: {capability}")
        
        return self._services[capability]
    
    def has_capability(self, capability: str) -> bool:
        """Check if capability is available."""
        return capability in self._services
    
    def provider_spec(self, capability: str) -> Optional[SAVE3ModuleSpec]:
        """Get specification of module providing a capability."""
        return self._specs_by_cap.get(capability)
    
    def list_capabilities(self) -> List[str]:
        """List all registered capabilities."""
        return sorted(self._services.keys())


# =============================================================================
# Module Discovery
# =============================================================================

def _load_module_from_path(py_path: str):
    """
    Dynamically load Python module from file path.
    
    Args:
        py_path: Path to .py file
        
    Returns:
        Loaded module object
        
    Raises:
        Save3Error: If module cannot be loaded
    """
    name = f"lego_{_sha256_bytes(py_path.encode('utf-8'))[:12]}"
    spec = importlib.util.spec_from_file_location(name, py_path)
    
    if spec is None or spec.loader is None:
        raise Save3Error(f"Cannot import module at {py_path}")
    
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)  # type: ignore
    
    return mod


def discover_specs(
    folder: str
) -> List[Tuple[str, SAVE3ModuleSpec, Optional[Callable]]]:
    """
    Discover modules with SAVE3 specifications in a folder.
    
    Scans for .py files containing module_spec() function and optional
    module_init(ctx) function.
    
    Args:
        folder: Directory to scan
        
    Returns:
        List of (filepath, spec, init_function) tuples
        
    Raises:
        SpecError: If module specifications are invalid
        
    Example:
        >>> specs = discover_specs("/path/to/modules")
        >>> for path, spec, init_fn in specs:
        ...     print(spec.module_id)
    """
    out: List[Tuple[str, SAVE3ModuleSpec, Optional[Callable]]] = []
    
    for root, _, files in os.walk(folder):
        for fn in files:
            if not fn.endswith(".py"):
                continue
            
            path = os.path.join(root, fn)
            
            # Skip this file itself
            if os.path.abspath(path) == os.path.abspath(__file__):
                continue
            
            try:
                mod = _load_module_from_path(path)
            except Exception as e:
                warnings.warn(f"Failed to load {path}: {e}")
                continue
            
            # Check for module_spec function
            if not hasattr(mod, "module_spec"):
                continue
            
            spec_dict = mod.module_spec()
            if not isinstance(spec_dict, dict):
                raise SpecError(f"{path}: module_spec() must return dict")
            
            # Create and validate spec
            ms = SAVE3ModuleSpec(**spec_dict)
            ms.entrypoint = path
            ms.validate()
            
            # Check for optional init function
            init_fn = getattr(mod, "module_init", None)
            if init_fn is not None and not callable(init_fn):
                raise SpecError(f"{path}: module_init must be callable if present")
            
            out.append((path, ms, init_fn))
    
    return out


# =============================================================================
# Dependency Resolution
# =============================================================================

def _build_provider_map(specs: List[SAVE3ModuleSpec]) -> Dict[str, SAVE3ModuleSpec]:
    """
    Build map from capabilities to providing modules.
    
    Args:
        specs: List of module specifications
        
    Returns:
        Dictionary mapping capability names to specs
        
    Raises:
        DependencyError: If multiple modules provide same capability
    """
    providers: Dict[str, SAVE3ModuleSpec] = {}
    
    for s in specs:
        for cap in s.provides:
            if cap in providers:
                raise DependencyError(
                    f"Duplicate provider for capability {cap!r}: "
                    f"{providers[cap].module_id} vs {s.module_id}"
                )
            providers[cap] = s
    
    return providers


def _check_version_constraints(
    consumer: SAVE3ModuleSpec,
    cap: str,
    provider: SAVE3ModuleSpec
) -> None:
    """
    Verify version constraints are satisfied.
    
    Args:
        consumer: Module requiring the capability
        cap: Capability name
        provider: Module providing the capability
        
    Raises:
        DependencyError: If constraints not satisfied
    """
    c = consumer.requires_versions.get(cap)
    if not c:
        return
    
    if "min" in c and not _semver_ge(provider.version, c["min"]):
        raise DependencyError(
            f"{consumer.module_id} requires {cap} >= {c['min']} "
            f"but provider {provider.module_id} is {provider.version}"
        )
    
    if "max_exclusive" in c and not _semver_lt(provider.version, c["max_exclusive"]):
        raise DependencyError(
            f"{consumer.module_id} requires {cap} < {c['max_exclusive']} "
            f"but provider {provider.module_id} is {provider.version}"
        )


def resolve_init_order(specs: List[SAVE3ModuleSpec]) -> List[SAVE3ModuleSpec]:
    """
    Compute topological initialization order for modules.
    
    Uses Kahn's algorithm to sort modules such that dependencies are
    initialized before dependents.
    
    Args:
        specs: List of module specifications
        
    Returns:
        List of specs in initialization order
        
    Raises:
        DependencyError: If dependencies missing or circular
        
    Example:
        >>> specs = [spec_a, spec_b, spec_c]  # b depends on a, c depends on b
        >>> ordered = resolve_init_order(specs)
        >>> # Returns [spec_a, spec_b, spec_c]
    """
    providers = _build_provider_map(specs)
    
    # Build dependency graph
    deps: Dict[str, List[str]] = {s.module_id: [] for s in specs}
    rev: Dict[str, List[str]] = {s.module_id: [] for s in specs}
    by_id = {s.module_id: s for s in specs}
    
    for s in specs:
        for cap in s.requires:
            # Check capability exists
            if cap not in providers:
                raise DependencyError(
                    f"{s.module_id} requires missing capability {cap!r}"
                )
            
            p = providers[cap]
            
            # Check version constraints
            _check_version_constraints(s, cap, p)
            
            # Don't add self-dependency
            if p.module_id == s.module_id:
                continue
            
            deps[s.module_id].append(p.module_id)
            rev[p.module_id].append(s.module_id)
    
    # Kahn's algorithm for topological sort
    indeg = {mid: len(set(deps[mid])) for mid in deps}
    queue = [mid for mid, d in indeg.items() if d == 0]
    order: List[str] = []
    
    while queue:
        mid = queue.pop(0)
        order.append(mid)
        
        for consumer_mid in rev[mid]:
            indeg[consumer_mid] -= 1
            if indeg[consumer_mid] == 0:
                queue.append(consumer_mid)
    
    # Check for cycles
    if len(order) != len(specs):
        remaining = [mid for mid in indeg if indeg[mid] > 0]
        raise DependencyError(f"Dependency cycle detected among: {remaining}")
    
    return [by_id[mid] for mid in order]


# =============================================================================
# Envelope Wrapping
# =============================================================================

def wrap_spec(
    spec: SAVE3ModuleSpec,
    secret: Optional[bytes] = None
) -> SAVE3Envelope:
    """
    Wrap module specification in SAVE3 envelope.
    
    Args:
        spec: Module specification to wrap
        secret: Optional shared secret for signing
        
    Returns:
        Finalized SAVE3Envelope
        
    Example:
        >>> spec = SAVE3ModuleSpec(module_id="test", version="v1.0.0")
        >>> env = wrap_spec(spec)
    """
    env = SAVE3Envelope(
        module_id=spec.module_id,
        module_name=spec.name,
        module_version=spec.version,
        payload_type="module_spec",
        payload=asdict(spec),
    )
    env.finalize(secret=secret)
    return env


# =============================================================================
# Orchestration (Lego Build)
# =============================================================================

def lego_build(
    folder: str,
    secret: Optional[bytes] = None,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Discover, validate, and initialize modules in a folder.
    
    The "Lego build" process:
    1. Discover all modules with module_spec()
    2. Validate specifications and envelope signatures
    3. Resolve dependencies and compute init order
    4. Call module_init(ctx) for each module in order
    5. Return report with initialization statistics
    
    Args:
        folder: Directory containing modules
        secret: Shared secret for signature verification
        verbose: Print progress messages
        
    Returns:
        Dictionary with build report
        
    Raises:
        Save3Error: If no modules found
        DependencyError: If dependency resolution fails
        SignatureError: If signature verification fails
        
    Example:
        >>> result = lego_build("/path/to/modules")
        >>> print(result["capabilities_published"])
    """
    # Discover modules
    discovered = discover_specs(folder)
    specs = [s for _, s, _ in discovered]
    
    if not specs:
        raise Save3Error(f"No modules with module_spec() found under: {folder}")
    
    # Resolve initialization order
    order = resolve_init_order(specs)
    
    # Map specs to init functions
    init_by_id: Dict[str, Optional[Callable]] = {s.module_id: None for s in specs}
    for _, s, init_fn in discovered:
        init_by_id[s.module_id] = init_fn
    
    # Build provider map
    providers = _build_provider_map(specs)
    
    # Wrap specs in envelopes and verify
    envelopes: Dict[str, SAVE3Envelope] = {}
    for s in specs:
        env = wrap_spec(s, secret=secret)
        env.verify(secret=secret)
        envelopes[s.module_id] = env
    
    # Create context with core registry
    ctx = LegoContext()
    
    core_spec = SAVE3ModuleSpec(
        module_id="save3.core",
        name="SAVE3 Core",
        version="v2.0.0",
        provides=["save3.spec_registry"],
        requires=[],
        requires_versions={},
        description="Provides the envelope registry",
        tags=["save3"]
    )
    
    registry_data = {
        "envelopes": {k: v.to_dict() for k, v in envelopes.items()}
    }
    ctx.provide("save3.spec_registry", registry_data, provider_spec=core_spec)
    
    # Initialize modules in dependency order
    report: List[Dict[str, Any]] = []
    
    for s in order:
        init_fn = init_by_id.get(s.module_id)
        
        if verbose:
            print(
                f"[LEGO] init {s.module_id} ({s.version}) "
                f"requires={s.requires} provides={s.provides}"
            )
        
        # Verify all required capabilities are available
        for cap in s.requires:
            if cap not in ctx._services:
                p = providers[cap]
                raise DependencyError(
                    f"Capability {cap!r} required by {s.module_id} but "
                    f"provider {p.module_id} did not publish it via ctx.provide()"
                )
        
        # Call module init
        t0 = time.time()
        if init_fn:
            sig = inspect.signature(init_fn)
            if len(sig.parameters) != 1:
                raise SpecError(
                    f"{s.module_id}: module_init(ctx) must take exactly 1 parameter"
                )
            init_fn(ctx)
        
        dt = time.time() - t0
        report.append({
            "module_id": s.module_id,
            "version": s.version,
            "init_seconds": round(dt, 6)
        })
    
    return {
        "folder": os.path.abspath(folder),
        "modules_in_init_order": [asdict(s) for s in order],
        "report": report,
        "capabilities_published": ctx.list_capabilities(),
    }
