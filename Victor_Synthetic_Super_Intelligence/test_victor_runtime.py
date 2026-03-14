#!/usr/bin/env python3
"""
Test Victor Personal Runtime
============================

Basic tests for the Victor Personal Runtime components.
"""

import asyncio
import sys
import os
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_runtime_creation():
    """Test runtime can be created"""
    from victor_runtime.core.runtime import VictorPersonalRuntime
    
    with tempfile.TemporaryDirectory() as tmpdir:
        runtime = VictorPersonalRuntime(data_dir=tmpdir)
        
        assert runtime is not None
        assert runtime.user_id is not None
        assert runtime.data_dir.exists()
        
        status = runtime.get_status()
        assert status['version'] == '1.0.0'
        assert status['state'] == 'stopped'
        
        print("✓ Runtime creation test passed")


def test_consent_manager():
    """Test consent manager"""
    from victor_runtime.core.consent import ConsentManager, ConsentType
    
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = ConsentManager(
            data_dir=Path(tmpdir),
            user_id='test_user_123'
        )
        
        # Initially no consents
        assert not manager.has_consent(ConsentType.LEARNING)
        
        # Grant consent programmatically
        manager.grant_consent(ConsentType.LEARNING)
        assert manager.has_consent(ConsentType.LEARNING)
        
        # Revoke consent
        manager.revoke_consent(ConsentType.LEARNING)
        assert not manager.has_consent(ConsentType.LEARNING)
        
        # Check audit log
        log = manager.get_audit_log(ConsentType.LEARNING)
        assert len(log) == 2  # grant + revoke
        
        print("✓ Consent manager test passed")


def test_user_control_panel():
    """Test user control panel"""
    from victor_runtime.core.user_control import UserControlPanel
    
    with tempfile.TemporaryDirectory() as tmpdir:
        panel = UserControlPanel(config_dir=Path(tmpdir))
        
        # Check features
        features = panel.get_features()
        assert 'learning' in features
        assert 'overlay' in features
        assert 'automation' in features
        
        # Toggle feature
        assert panel.is_feature_enabled('learning')  # Default enabled
        
        # Get status
        status = panel.get_status()
        assert status['version'] is not None
        
        print("✓ User control panel test passed")


def test_device_registry():
    """Test device registry"""
    from victor_runtime.core.device_registry import DeviceRegistry
    
    with tempfile.TemporaryDirectory() as tmpdir:
        registry = DeviceRegistry(
            data_dir=Path(tmpdir),
            user_id='test_user_123'
        )
        
        # Register a device
        device = registry.register_device(
            device_id='test_device_1',
            device_name='Test Phone',
            platform='android',
            os_version='14',
            runtime_version='1.0.0',
            is_current=True
        )
        
        assert device.device_id == 'test_device_1'
        assert registry.get_current_device() is not None
        
        # Get all devices
        devices = registry.get_all_devices()
        assert len(devices) == 1
        
        # Remove device
        registry.remove_device('test_device_1')
        assert len(registry.get_all_devices()) == 0
        
        print("✓ Device registry test passed")


def test_learning_engine():
    """Test personal learning engine"""
    from victor_runtime.core.learning import PersonalLearningEngine
    
    with tempfile.TemporaryDirectory() as tmpdir:
        engine = PersonalLearningEngine(
            data_dir=Path(tmpdir),
            config={'enabled': True, 'local_only': True}
        )
        
        # Record observations
        engine.observe('app_usage', {'app_name': 'Chrome'})
        engine.observe('app_usage', {'app_name': 'Chrome'})
        engine.observe('command', {'command': 'search weather'})
        
        # Process queue
        loop = asyncio.new_event_loop()
        loop.run_until_complete(engine._process_observations())
        loop.close()
        
        # Check patterns
        patterns = engine.get_patterns()
        assert len(patterns) > 0
        
        # Get summary
        summary = engine.get_summary()
        assert summary['total_patterns'] > 0
        
        print("✓ Learning engine test passed")


def test_mesh_client():
    """Test mesh client"""
    from victor_runtime.mesh.client import MeshClient, MeshPeer
    
    # Create mock device info
    class MockDeviceInfo:
        device_id = 'test_device'
        device_name = 'Test Device'
        platform = 'test'
    
    client = MeshClient(
        device_info=MockDeviceInfo(),
        config={'enabled': True}
    )
    
    # Check initial state
    assert len(client.get_peers()) == 0
    
    # Get mesh status
    status = client.get_mesh_status()
    assert status['device_id'] == 'test_device'
    assert status['total_peers'] == 0
    
    print("✓ Mesh client test passed")


def test_platform_base():
    """Test base platform adapter"""
    from victor_runtime.platforms.base import BasePlatformAdapter
    
    adapter = BasePlatformAdapter(runtime=None)
    
    # Check it's properly initialized
    assert adapter.platform_name == "generic"
    assert not adapter._initialized
    
    # Get platform info
    info = adapter.get_platform_info()
    assert info['platform'] == 'generic'
    
    print("✓ Base platform adapter test passed")


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("Victor Personal Runtime - Test Suite")
    print("=" * 60)
    print()
    
    tests = [
        test_runtime_creation,
        test_consent_manager,
        test_user_control_panel,
        test_device_registry,
        test_learning_engine,
        test_mesh_client,
        test_platform_base,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed += 1
    
    print()
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
