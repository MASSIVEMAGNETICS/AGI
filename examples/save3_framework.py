"""
Example: SAVE3 Trust Framework
===============================

Demonstrates the SAVE3 trust framework with module discovery,
dependency resolution, and lego build orchestration.
"""

import tempfile
import os
from victor_core.trust import (
    SAVE3Envelope, SAVE3ModuleSpec, LegoContext, TrustModelBeta,
    lego_build, wrap_spec
)

print("=" * 60)
print("Victor Core - SAVE3 Trust Framework Example")
print("=" * 60)

# 1. Trust Model Example
print("\n1. Trust Model Beta - Time-decay & Latency Weighting")
print("-" * 40)

trust = TrustModelBeta(
    decay_halflife=3600.0,  # 1 hour
    latency_penalty_threshold=1000.0,  # 1 second
    latency_penalty_rate=0.001
)

# Record some interactions
print("Recording interactions...")

# Service A: Good performance
trust.record_success("service_a", score_gain=10, latency_ms=50)
trust.record_success("service_a", score_gain=10, latency_ms=75)
trust.record_success("service_a", score_gain=10, latency_ms=60)

# Service B: Mixed performance
trust.record_success("service_b", score_gain=10, latency_ms=200)
trust.record_failure("service_b", score_penalty=15)
trust.record_success("service_b", score_gain=10, latency_ms=150)

# Service C: Poor performance
trust.record_failure("service_c", score_penalty=20)
trust.record_success("service_c", score_gain=5, latency_ms=2000)  # High latency
trust.record_failure("service_c", score_penalty=20)

print("\nTrust Scores:")
print(f"  Service A: {trust.get_trust('service_a'):.2f}")
print(f"  Service B: {trust.get_trust('service_b'):.2f}")
print(f"  Service C: {trust.get_trust('service_c'):.2f}")

# Check threshold
try:
    trust.check_threshold("service_a", min_score=60.0)
    print("\n✓ Service A passes trust threshold")
except Exception as e:
    print(f"\n✗ Service A fails trust threshold: {e}")

# 2. SAVE3 Envelope Example
print("\n2. SAVE3 Envelope - Secure Message Wrapping")
print("-" * 40)

# Create envelope
envelope = SAVE3Envelope(
    module_id="example.service",
    module_name="Example Service",
    module_version="v1.0.0",
    payload={
        "config": {"timeout": 30, "retries": 3},
        "data": [1, 2, 3, 4, 5]
    }
)

# Finalize with signature
secret = b"shared_secret_key"
envelope.finalize(secret=secret)

print(f"Envelope created:")
print(f"  Module: {envelope.module_name} ({envelope.module_version})")
print(f"  Payload SHA256: {envelope.payload_sha256[:16]}...")
print(f"  Signature: {envelope.signature[:16]}...")

# Verify
try:
    envelope.verify(secret=secret)
    print("\n✓ Envelope signature verified successfully")
except Exception as e:
    print(f"\n✗ Verification failed: {e}")

# 3. Module Specification Example
print("\n3. Module Specification - Dependency Declaration")
print("-" * 40)

# Define some module specs
logger_spec = SAVE3ModuleSpec(
    module_id="core.logger",
    name="Logging Service",
    version="v1.0.0",
    provides=["logging.service"],
    requires=[],
    description="Provides centralized logging"
)

database_spec = SAVE3ModuleSpec(
    module_id="core.database",
    name="Database Service",
    version="v2.1.0",
    provides=["database.service"],
    requires=["logging.service"],
    requires_versions={
        "logging.service": {"min": "v1.0.0", "max_exclusive": "v2.0.0"}
    },
    description="Provides database access"
)

api_spec = SAVE3ModuleSpec(
    module_id="core.api",
    name="API Service",
    version="v1.5.0",
    provides=["api.service"],
    requires=["logging.service", "database.service"],
    description="Provides REST API"
)

print("Module Specifications:")
print(f"  {logger_spec.name}: provides {logger_spec.provides}")
print(f"  {database_spec.name}: requires {database_spec.requires}, provides {database_spec.provides}")
print(f"  {api_spec.name}: requires {api_spec.requires}, provides {api_spec.provides}")

# Resolve initialization order
from victor_core.trust import resolve_init_order

order = resolve_init_order([api_spec, database_spec, logger_spec])

print("\nInitialization Order (dependency resolution):")
for i, spec in enumerate(order, 1):
    print(f"  {i}. {spec.name}")

# 4. Lego Context Example
print("\n4. Lego Context - Service Registry")
print("-" * 40)

ctx = LegoContext()

# Provide some services
class MockLogger:
    def log(self, msg):
        print(f"[LOG] {msg}")

class MockDatabase:
    def query(self, sql):
        return f"Executing: {sql}"

ctx.provide("logging.service", MockLogger(), logger_spec)
ctx.provide("database.service", MockDatabase(), database_spec)

print("Services registered:")
for cap in ctx.list_capabilities():
    provider = ctx.provider_spec(cap)
    print(f"  {cap} <- {provider.name}")

# Require services
logger = ctx.require("logging.service")
db = ctx.require("database.service")

print("\nUsing services:")
logger.log("Database query started")
result = db.query("SELECT * FROM users")
logger.log(f"Result: {result}")

# 5. Lego Build Example
print("\n5. Lego Build - Full Orchestration")
print("-" * 40)

with tempfile.TemporaryDirectory() as tmpdir:
    # Create module files
    
    # Module 1: Data Provider
    module1_code = '''
def module_spec():
    return {
        "module_id": "data.provider",
        "name": "Data Provider",
        "version": "v1.0.0",
        "provides": ["data.numbers"],
        "requires": [],
        "description": "Provides number data"
    }

def module_init(ctx):
    from victor_core.trust import SAVE3ModuleSpec
    spec = SAVE3ModuleSpec(
        module_id="data.provider",
        name="Data Provider",
        version="v1.0.0",
        provides=["data.numbers"]
    )
    ctx.provide("data.numbers", [1, 2, 3, 4, 5], provider_spec=spec)
'''
    
    # Module 2: Data Processor
    module2_code = '''
def module_spec():
    return {
        "module_id": "data.processor",
        "name": "Data Processor",
        "version": "v1.0.0",
        "provides": ["data.processed"],
        "requires": ["data.numbers"],
        "description": "Processes number data"
    }

def module_init(ctx):
    from victor_core.trust import SAVE3ModuleSpec
    numbers = ctx.require("data.numbers")
    processed = [x * 2 for x in numbers]
    
    spec = SAVE3ModuleSpec(
        module_id="data.processor",
        name="Data Processor",
        version="v1.0.0",
        provides=["data.processed"]
    )
    ctx.provide("data.processed", processed, provider_spec=spec)
'''
    
    # Write modules to disk
    with open(os.path.join(tmpdir, "provider.py"), 'w') as f:
        f.write(module1_code)
    
    with open(os.path.join(tmpdir, "processor.py"), 'w') as f:
        f.write(module2_code)
    
    # Build!
    print(f"Building modules from: {tmpdir}")
    result = lego_build(tmpdir, verbose=False)
    
    print("\nBuild Results:")
    print(f"  Modules discovered: {len(result['modules_in_init_order'])}")
    print(f"  Capabilities published: {len(result['capabilities_published'])}")
    
    print("\nInitialization Order:")
    for module in result['modules_in_init_order']:
        print(f"  - {module['name']} (v{module['version']})")
    
    print("\nAvailable Capabilities:")
    for cap in sorted(result['capabilities_published']):
        print(f"  - {cap}")

print("\n" + "=" * 60)
print("All SAVE3 examples completed successfully!")
print("=" * 60)
