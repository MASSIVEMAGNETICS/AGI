"""
Comprehensive tests for Victor Core SAVE3 Trust Framework.

Tests cover:
- TrustModelBeta (time-decay, latency weighting)
- SAVE3Envelope (signatures, verification)
- LegoContext (service registry)
- Module discovery and dependency resolution
- Lego build orchestration
"""

import pytest
import time
import tempfile
import os
from victor_core.trust import (
    SAVE3Envelope, SAVE3ModuleSpec, LegoContext, TrustModelBeta,
    discover_specs, resolve_init_order, lego_build, wrap_spec,
    Save3Error, SpecError, SignatureError, DependencyError, TrustError
)


class TestTrustModelBeta:
    """Test TrustModelBeta with time-decay and latency weighting."""
    
    def test_initialization(self):
        """Test trust model initialization."""
        trust = TrustModelBeta()
        assert trust.decay_halflife == 3600.0
        assert trust.min_trust == 0.0
        assert trust.max_trust == 100.0
    
    def test_record_success(self):
        """Test recording successful interactions."""
        trust = TrustModelBeta()
        
        # Record success
        score = trust.record_success("service_a", score_gain=10.0)
        
        # Score should increase from neutral (50)
        assert score > 50.0
    
    def test_latency_penalty(self):
        """Test latency penalties reduce trust."""
        trust = TrustModelBeta(latency_penalty_threshold=100.0, latency_penalty_rate=0.01)
        
        # Success with low latency
        score1 = trust.record_success("service_a", score_gain=10.0, latency_ms=50.0)
        
        # Success with high latency (should be penalized)
        score2 = trust.record_success("service_b", score_gain=10.0, latency_ms=500.0)
        
        # Service with high latency should have lower score gain
        # Both start at 50, service_a gains ~10, service_b gains ~10 - 4 (latency penalty) = ~6
        assert score1 > score2
    
    def test_record_failure(self):
        """Test recording failures."""
        trust = TrustModelBeta()
        
        # Record failure
        score = trust.record_failure("service_a", score_penalty=15.0)
        
        # Score should decrease from neutral (50)
        assert score < 50.0
    
    def test_get_trust(self):
        """Test getting trust scores."""
        trust = TrustModelBeta()
        
        # New entity should have neutral score
        score = trust.get_trust("service_a")
        assert score == 50.0
        
        # After success, score should increase
        trust.record_success("service_a")
        score = trust.get_trust("service_a")
        assert score > 50.0
    
    def test_time_decay(self):
        """Test trust scores decay over time."""
        trust = TrustModelBeta(decay_halflife=1.0)  # 1 second halflife
        
        # Record success
        trust.record_success("service_a", score_gain=50.0)
        initial_score = trust.get_trust("service_a")
        
        # Wait for decay
        time.sleep(1.1)
        
        # Score should have decayed
        decayed_score = trust.get_trust("service_a")
        assert decayed_score < initial_score
    
    def test_min_max_bounds(self):
        """Test trust scores stay within bounds."""
        trust = TrustModelBeta(min_trust=0.0, max_trust=100.0)
        
        # Try to exceed max
        for _ in range(20):
            trust.record_success("service_a", score_gain=20.0)
        
        score = trust.get_trust("service_a")
        assert score <= 100.0
        
        # Try to go below min
        for _ in range(20):
            trust.record_failure("service_b", score_penalty=20.0)
        
        score = trust.get_trust("service_b")
        assert score >= 0.0
    
    def test_get_events(self):
        """Test retrieving event history."""
        trust = TrustModelBeta()
        
        # Record events
        trust.record_success("service_a")
        trust.record_failure("service_a")
        trust.record_success("service_a")
        
        # Get all events
        events = trust.get_events("service_a")
        assert len(events) == 3
        
        # Check event types
        assert events[0].event_type == "success"
        assert events[1].event_type == "failure"
        assert events[2].event_type == "success"
    
    def test_check_threshold(self):
        """Test trust threshold checking."""
        trust = TrustModelBeta()
        
        # Build up trust
        for _ in range(5):
            trust.record_success("service_a", score_gain=10.0)
        
        # Should pass threshold
        assert trust.check_threshold("service_a", min_score=50.0)
        
        # Should fail low threshold
        with pytest.raises(TrustError):
            trust.check_threshold("service_a", min_score=200.0)


class TestSAVE3Envelope:
    """Test SAVE3 envelope with signatures."""
    
    def test_create_envelope(self):
        """Test envelope creation."""
        env = SAVE3Envelope(
            module_id="test.module",
            module_name="Test Module",
            module_version="v1.0.0",
            payload={"key": "value"}
        )
        
        assert env.module_id == "test.module"
        assert env.payload["key"] == "value"
    
    def test_finalize_no_signature(self):
        """Test finalizing envelope without signature."""
        env = SAVE3Envelope(
            module_id="test.module",
            payload={"data": 123}
        )
        
        env.finalize()
        
        assert env.payload_sha256 != ""
        assert env.signature_alg == "none"
        assert env.signature == ""
    
    def test_finalize_with_signature(self):
        """Test finalizing envelope with HMAC signature."""
        env = SAVE3Envelope(
            module_id="test.module",
            payload={"data": 123}
        )
        
        secret = b"shared_secret"
        env.finalize(secret=secret)
        
        assert env.payload_sha256 != ""
        assert env.signature_alg == "hmac-sha256"
        assert env.signature != ""
    
    def test_verify_unsigned(self):
        """Test verifying unsigned envelope."""
        env = SAVE3Envelope(
            module_id="test.module",
            payload={"data": 123}
        )
        
        env.finalize()
        env.verify()  # Should not raise
    
    def test_verify_signed(self):
        """Test verifying signed envelope."""
        secret = b"shared_secret"
        env = SAVE3Envelope(
            module_id="test.module",
            payload={"data": 123}
        )
        
        env.finalize(secret=secret)
        env.verify(secret=secret)  # Should not raise
    
    def test_verify_wrong_secret(self):
        """Test verification fails with wrong secret."""
        env = SAVE3Envelope(
            module_id="test.module",
            payload={"data": 123}
        )
        
        env.finalize(secret=b"secret1")
        
        with pytest.raises(SignatureError):
            env.verify(secret=b"secret2")
    
    def test_verify_tampered_payload(self):
        """Test verification fails with tampered payload."""
        env = SAVE3Envelope(
            module_id="test.module",
            payload={"data": 123}
        )
        
        env.finalize()
        
        # Tamper with payload
        env.payload["data"] = 456
        
        with pytest.raises(SignatureError):
            env.verify()
    
    def test_to_from_dict(self):
        """Test envelope serialization."""
        env = SAVE3Envelope(
            module_id="test.module",
            module_name="Test",
            module_version="v1.0.0",
            payload={"x": 1}
        )
        env.finalize()
        
        # Convert to dict
        d = env.to_dict()
        
        # Recreate from dict
        env2 = SAVE3Envelope.from_dict(d)
        
        assert env2.module_id == env.module_id
        assert env2.payload == env.payload
        assert env2.payload_sha256 == env.payload_sha256


class TestSAVE3ModuleSpec:
    """Test SAVE3 module specifications."""
    
    def test_create_spec(self):
        """Test creating module spec."""
        spec = SAVE3ModuleSpec(
            module_id="test.module",
            name="Test Module",
            version="v1.0.0",
            provides=["test.service"],
            requires=["logging.service"]
        )
        
        assert spec.module_id == "test.module"
        assert "test.service" in spec.provides
        assert "logging.service" in spec.requires
    
    def test_validate_success(self):
        """Test validation of valid spec."""
        spec = SAVE3ModuleSpec(
            module_id="test.module",
            name="Test",
            version="v1.0.0",
            provides=["svc"],
            requires=[]
        )
        
        spec.validate()  # Should not raise
    
    def test_validate_missing_id(self):
        """Test validation fails without module_id."""
        spec = SAVE3ModuleSpec(
            module_id="",
            name="Test",
            version="v1.0.0"
        )
        
        with pytest.raises(SpecError):
            spec.validate()
    
    def test_validate_invalid_version(self):
        """Test validation fails with bad version."""
        spec = SAVE3ModuleSpec(
            module_id="test",
            name="Test",
            version="1.0"  # Should be semver
        )
        
        with pytest.raises(SpecError):
            spec.validate()
    
    def test_version_constraints(self):
        """Test version constraint specification."""
        spec = SAVE3ModuleSpec(
            module_id="test",
            name="Test",
            version="v1.0.0",
            requires=["dep.service"],
            requires_versions={
                "dep.service": {
                    "min": "v1.0.0",
                    "max_exclusive": "v2.0.0"
                }
            }
        )
        
        spec.validate()  # Should not raise


class TestLegoContext:
    """Test service registry and dependency injection."""
    
    def test_create_context(self):
        """Test creating context."""
        ctx = LegoContext()
        assert ctx is not None
    
    def test_provide_capability(self):
        """Test providing capabilities."""
        ctx = LegoContext()
        spec = SAVE3ModuleSpec(
            module_id="provider",
            name="Provider",
            version="v1.0.0",
            provides=["test.service"]
        )
        
        service = {"data": "test"}
        ctx.provide("test.service", service, spec)
        
        assert ctx.has_capability("test.service")
    
    def test_require_capability(self):
        """Test requiring capabilities."""
        ctx = LegoContext()
        spec = SAVE3ModuleSpec(
            module_id="provider",
            name="Provider",
            version="v1.0.0",
            provides=["test.service"]
        )
        
        service = {"data": "test"}
        ctx.provide("test.service", service, spec)
        
        retrieved = ctx.require("test.service")
        assert retrieved == service
    
    def test_require_missing(self):
        """Test requiring missing capability fails."""
        ctx = LegoContext()
        
        with pytest.raises(DependencyError):
            ctx.require("missing.service")
    
    def test_duplicate_provide(self):
        """Test duplicate capability provision fails."""
        ctx = LegoContext()
        spec = SAVE3ModuleSpec(
            module_id="provider",
            name="Provider",
            version="v1.0.0",
            provides=["test.service"]
        )
        
        ctx.provide("test.service", {}, spec)
        
        with pytest.raises(DependencyError):
            ctx.provide("test.service", {}, spec)
    
    def test_list_capabilities(self):
        """Test listing capabilities."""
        ctx = LegoContext()
        spec = SAVE3ModuleSpec(
            module_id="provider",
            name="Provider",
            version="v1.0.0",
            provides=["svc1", "svc2"]
        )
        
        ctx.provide("svc1", {}, spec)
        ctx.provide("svc2", {}, spec)
        
        caps = ctx.list_capabilities()
        assert "svc1" in caps
        assert "svc2" in caps


class TestDependencyResolution:
    """Test dependency resolution and topological sorting."""
    
    def test_simple_resolution(self):
        """Test simple dependency resolution."""
        spec_a = SAVE3ModuleSpec(
            module_id="module.a",
            name="Module A",
            version="v1.0.0",
            provides=["service.a"],
            requires=[]
        )
        
        spec_b = SAVE3ModuleSpec(
            module_id="module.b",
            name="Module B",
            version="v1.0.0",
            provides=["service.b"],
            requires=["service.a"]
        )
        
        # B depends on A, so A should come first
        order = resolve_init_order([spec_b, spec_a])
        
        assert order[0].module_id == "module.a"
        assert order[1].module_id == "module.b"
    
    def test_chain_dependencies(self):
        """Test chain of dependencies."""
        spec_a = SAVE3ModuleSpec(
            module_id="a",
            name="A",
            version="v1.0.0",
            provides=["svc.a"],
            requires=[]
        )
        
        spec_b = SAVE3ModuleSpec(
            module_id="b",
            name="B",
            version="v1.0.0",
            provides=["svc.b"],
            requires=["svc.a"]
        )
        
        spec_c = SAVE3ModuleSpec(
            module_id="c",
            name="C",
            version="v1.0.0",
            provides=["svc.c"],
            requires=["svc.b"]
        )
        
        # C -> B -> A
        order = resolve_init_order([spec_c, spec_b, spec_a])
        
        assert order[0].module_id == "a"
        assert order[1].module_id == "b"
        assert order[2].module_id == "c"
    
    def test_missing_dependency(self):
        """Test missing dependency detection."""
        spec = SAVE3ModuleSpec(
            module_id="module",
            name="Module",
            version="v1.0.0",
            provides=[],
            requires=["missing.service"]
        )
        
        with pytest.raises(DependencyError):
            resolve_init_order([spec])
    
    def test_circular_dependency(self):
        """Test circular dependency detection."""
        spec_a = SAVE3ModuleSpec(
            module_id="a",
            name="A",
            version="v1.0.0",
            provides=["svc.a"],
            requires=["svc.b"]
        )
        
        spec_b = SAVE3ModuleSpec(
            module_id="b",
            name="B",
            version="v1.0.0",
            provides=["svc.b"],
            requires=["svc.a"]
        )
        
        with pytest.raises(DependencyError):
            resolve_init_order([spec_a, spec_b])
    
    def test_version_constraint_satisfied(self):
        """Test version constraints are checked."""
        spec_a = SAVE3ModuleSpec(
            module_id="a",
            name="A",
            version="v1.5.0",
            provides=["svc.a"],
            requires=[]
        )
        
        spec_b = SAVE3ModuleSpec(
            module_id="b",
            name="B",
            version="v1.0.0",
            provides=["svc.b"],
            requires=["svc.a"],
            requires_versions={
                "svc.a": {"min": "v1.0.0", "max_exclusive": "v2.0.0"}
            }
        )
        
        # Should succeed - v1.5.0 is in range [1.0.0, 2.0.0)
        order = resolve_init_order([spec_a, spec_b])
        assert len(order) == 2
    
    def test_version_constraint_violated(self):
        """Test version constraint violation detected."""
        spec_a = SAVE3ModuleSpec(
            module_id="a",
            name="A",
            version="v0.9.0",  # Too old
            provides=["svc.a"],
            requires=[]
        )
        
        spec_b = SAVE3ModuleSpec(
            module_id="b",
            name="B",
            version="v1.0.0",
            provides=["svc.b"],
            requires=["svc.a"],
            requires_versions={
                "svc.a": {"min": "v1.0.0"}
            }
        )
        
        with pytest.raises(DependencyError):
            resolve_init_order([spec_a, spec_b])


class TestEnvelopeWrapping:
    """Test wrapping specs in envelopes."""
    
    def test_wrap_spec(self):
        """Test wrapping module spec in envelope."""
        spec = SAVE3ModuleSpec(
            module_id="test",
            name="Test",
            version="v1.0.0",
            provides=["svc"]
        )
        
        env = wrap_spec(spec)
        
        assert env.module_id == spec.module_id
        assert env.payload_type == "module_spec"
        assert env.payload_sha256 != ""
    
    def test_wrap_spec_signed(self):
        """Test wrapping with signature."""
        spec = SAVE3ModuleSpec(
            module_id="test",
            name="Test",
            version="v1.0.0"
        )
        
        secret = b"secret"
        env = wrap_spec(spec, secret=secret)
        
        assert env.signature_alg == "hmac-sha256"
        env.verify(secret=secret)  # Should not raise


class TestModuleDiscovery:
    """Test module discovery from filesystem."""
    
    def test_discover_empty_folder(self):
        """Test discovery in empty folder."""
        with tempfile.TemporaryDirectory() as tmpdir:
            specs = discover_specs(tmpdir)
            assert len(specs) == 0
    
    def test_discover_single_module(self):
        """Test discovering single module."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a module file
            module_code = '''
def module_spec():
    return {
        "module_id": "test.module",
        "name": "Test Module",
        "version": "v1.0.0",
        "provides": ["test.service"],
        "requires": [],
    }

def module_init(ctx):
    ctx.provide("test.service", lambda: "test", provider_spec=type("Spec", (), {
        "module_id": "test.module",
        "name": "Test Module",
        "version": "v1.0.0",
        "provides": ["test.service"],
        "requires": []
    })())
'''
            
            module_path = os.path.join(tmpdir, "test_module.py")
            with open(module_path, 'w') as f:
                f.write(module_code)
            
            specs = discover_specs(tmpdir)
            
            assert len(specs) == 1
            path, spec, init_fn = specs[0]
            assert spec.module_id == "test.module"
            assert init_fn is not None


class TestLegoBuild:
    """Test complete lego build orchestration."""
    
    def test_lego_build_simple(self):
        """Test lego build with simple modules."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create provider module
            provider_code = '''
def module_spec():
    return {
        "module_id": "provider",
        "name": "Provider",
        "version": "v1.0.0",
        "provides": ["data.service"],
        "requires": [],
    }

def module_init(ctx):
    from victor_core.trust import SAVE3ModuleSpec
    spec = SAVE3ModuleSpec(
        module_id="provider",
        name="Provider",
        version="v1.0.0",
        provides=["data.service"]
    )
    ctx.provide("data.service", {"value": 42}, provider_spec=spec)
'''
            
            # Create consumer module
            consumer_code = '''
def module_spec():
    return {
        "module_id": "consumer",
        "name": "Consumer",
        "version": "v1.0.0",
        "provides": ["result.service"],
        "requires": ["data.service"],
    }

def module_init(ctx):
    from victor_core.trust import SAVE3ModuleSpec
    data = ctx.require("data.service")
    spec = SAVE3ModuleSpec(
        module_id="consumer",
        name="Consumer",
        version="v1.0.0",
        provides=["result.service"]
    )
    ctx.provide("result.service", {"result": data["value"] * 2}, provider_spec=spec)
'''
            
            # Write modules
            with open(os.path.join(tmpdir, "provider.py"), 'w') as f:
                f.write(provider_code)
            
            with open(os.path.join(tmpdir, "consumer.py"), 'w') as f:
                f.write(consumer_code)
            
            # Build
            result = lego_build(tmpdir, verbose=False)
            
            assert "provider" in result["capabilities_published"][0] or "data.service" in result["capabilities_published"]
            assert len(result["report"]) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
