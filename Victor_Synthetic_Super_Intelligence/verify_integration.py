#!/usr/bin/env python3
"""
Integration Verification Script
Runs comprehensive tests on the Victor Hub to verify all systems are operational
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from victor_hub.victor_boot import VictorHub, Task

def main():
    print("=" * 70)
    print("VICTOR HUB INTEGRATION VERIFICATION")
    print("=" * 70)
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Initialization
    print("\n[Test 1] System Initialization")
    try:
        hub = VictorHub()
        print("✅ PASS: System initialized successfully")
        tests_passed += 1
    except Exception as e:
        print(f"❌ FAIL: System initialization failed: {e}")
        tests_failed += 1
        return
    
    # Test 2: Skill Discovery
    print("\n[Test 2] Skill Discovery")
    try:
        assert len(hub.registry.skills) >= 2, "Expected at least 2 skills"
        print(f"✅ PASS: Discovered {len(hub.registry.skills)} skills")
        tests_passed += 1
    except Exception as e:
        print(f"❌ FAIL: Skill discovery failed: {e}")
        tests_failed += 1
    
    # Test 3: Echo Task Execution
    print("\n[Test 3] Echo Task Execution")
    try:
        task = Task(
            id="verify_001",
            type="echo",
            description="Integration verification test"
        )
        result = hub.execute_task(task)
        assert result.status == "success", f"Expected success, got {result.status}"
        assert result.output is not None, "Expected output"
        print(f"✅ PASS: Echo task executed successfully")
        print(f"   Output: {result.output}")
        tests_passed += 1
    except Exception as e:
        print(f"❌ FAIL: Echo task failed: {e}")
        tests_failed += 1
    
    # Test 4: Content Generation Task
    print("\n[Test 4] Content Generation Task")
    try:
        task = Task(
            id="verify_002",
            type="content_generation",
            description="Test content generation",
            inputs={"topic": "AGI", "style": "technical"}
        )
        result = hub.execute_task(task)
        assert result.status == "success", f"Expected success, got {result.status}"
        assert result.output is not None, "Expected output"
        print(f"✅ PASS: Content generation executed successfully")
        print(f"   Generated {len(str(result.output))} characters")
        tests_passed += 1
    except Exception as e:
        print(f"❌ FAIL: Content generation failed: {e}")
        tests_failed += 1
    
    # Test 5: Task Routing
    print("\n[Test 5] Task Routing")
    try:
        task = Task(id="verify_003", type="echo", description="Routing test")
        skill = hub.registry.route(task)
        assert skill is not None, "Expected skill to be found"
        assert skill.name == "echo", f"Expected echo skill, got {skill.name}"
        print(f"✅ PASS: Task routed correctly to {skill.name}")
        tests_passed += 1
    except Exception as e:
        print(f"❌ FAIL: Task routing failed: {e}")
        tests_failed += 1
    
    # Test 6: Configuration Loading
    print("\n[Test 6] Configuration Loading")
    try:
        assert hub.config is not None, "Expected config"
        assert "mode" in hub.config, "Expected mode in config"
        print(f"✅ PASS: Configuration loaded (mode: {hub.config['mode']})")
        tests_passed += 1
    except Exception as e:
        print(f"❌ FAIL: Configuration loading failed: {e}")
        tests_failed += 1
    
    # Test 7: Logging System
    print("\n[Test 7] Logging System")
    try:
        log_dir = Path("logs")
        assert log_dir.exists(), "Expected logs directory"
        log_files = list(log_dir.glob("*.log"))
        assert len(log_files) > 0, "Expected log files"
        print(f"✅ PASS: Logging system operational ({len(log_files)} log files)")
        tests_passed += 1
    except Exception as e:
        print(f"❌ FAIL: Logging system check failed: {e}")
        tests_failed += 1
    
    # Test 8: Documentation Completeness
    print("\n[Test 8] Documentation Completeness")
    try:
        required_docs = [
            "README.md",
            "00_REPO_MANIFEST.md",
            "01_INTERACTION_MAP.md",
            "02_VICTOR_INTEGRATED_ARCHITECTURE.md",
            "03_AUTONOMY_AND_EVOLUTION.md",
            "DEPLOYMENT_SUMMARY.md"
        ]
        missing_docs = []
        for doc in required_docs:
            if not Path(doc).exists():
                missing_docs.append(doc)
        
        assert len(missing_docs) == 0, f"Missing docs: {missing_docs}"
        print(f"✅ PASS: All {len(required_docs)} required documents present")
        tests_passed += 1
    except Exception as e:
        print(f"❌ FAIL: Documentation check failed: {e}")
        tests_failed += 1
    
    # Final Summary
    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)
    print(f"Tests Passed: {tests_passed}")
    print(f"Tests Failed: {tests_failed}")
    print(f"Success Rate: {tests_passed}/{tests_passed + tests_failed} ({100 * tests_passed / (tests_passed + tests_failed):.1f}%)")
    
    if tests_failed == 0:
        print("\n🎉 ALL TESTS PASSED - Victor Hub is fully operational!")
        print("\nQuick Start:")
        print("  python victor_hub/victor_boot.py")
        return 0
    else:
        print(f"\n⚠️  {tests_failed} test(s) failed - Please review errors above")
        return 1

if __name__ == "__main__":
    sys.exit(main())
