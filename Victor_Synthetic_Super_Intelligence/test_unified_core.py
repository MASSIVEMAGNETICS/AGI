#!/usr/bin/env python3
"""
Test script for Unified Core
Tests the complete Unified Nervous System implementation
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))


def test_tensor_phase_and_provenance():
    """Test Phase 1.1: Tensor with phase and provenance"""
    from advanced_ai.tensor_core import Tensor
    import numpy as np
    
    print("=" * 80)
    print("TEST 1: Tensor Phase and Provenance")
    print("=" * 80)
    print()
    
    print("Testing tensor creation with phase...")
    t1 = Tensor([1, 2, 3], requires_grad=True, phase=0.5)
    assert t1.phase == 0.5, "Phase should be 0.5"
    assert 'provenance' in dir(t1), "Tensor should have provenance"
    assert t1.provenance['bloodline_verified'] == True, "Bloodline should be verified"
    print(f"✓ Created tensor with phase={t1.phase}")
    print(f"  Provenance: {t1.provenance}")
    print()
    
    print("Testing phase combination in addition...")
    t2 = Tensor([4, 5, 6], requires_grad=True, phase=1.0)
    t3 = t1 + t2
    assert t3.phase == 1.5, f"Phase should be 1.5, got {t3.phase}"
    assert t3.provenance['operation'] == '+', "Operation should be +"
    print(f"✓ Addition: phase {t1.phase} + {t2.phase} = {t3.phase}")
    print()
    
    print("Testing phase combination in multiplication...")
    t4 = Tensor([1, 1, 1], phase=2.0)
    t5 = Tensor([2, 2, 2], phase=3.0)
    t6 = t4 * t5
    expected_phase = (2.0 * 3.0) % (2 * np.pi)
    assert abs(t6.phase - expected_phase) < 0.001, f"Phase should be {expected_phase}"
    print(f"✓ Multiplication: phase {t4.phase} * {t5.phase} = {t6.phase}")
    print()
    
    print("Testing provenance tracking...")
    t7 = t1.matmul(Tensor([[1], [1], [1]], phase=0.3))
    assert 'parent_sources' in t7.provenance, "Should track parent sources"
    print(f"✓ Provenance tracked: {t7.provenance['operation']}")
    print()
    
    return True


def test_multi_modal_frame():
    """Test Phase 1.2: Multi-Modal Frame"""
    from unified_core import MultiModalFrame
    
    print("=" * 80)
    print("TEST 2: Multi-Modal Frame")
    print("=" * 80)
    print()
    
    print("Creating Multi-Modal Frame...")
    frame = MultiModalFrame(
        raw_input="Test input",
        emotional_state={'joy': 0.8, 'curiosity': 0.6},
        logical_constraints=['must be positive', 'must be creative'],
        metadata={'source': 'test'}
    )
    
    assert frame.raw_input == "Test input", "Raw input should match"
    assert frame.emotional_state['joy'] == 0.8, "Emotional state should match"
    assert len(frame.logical_constraints) == 2, "Should have 2 constraints"
    print(f"✓ Frame created: {frame}")
    print(f"  Emotional state: {frame.emotional_state}")
    print(f"  Constraints: {frame.logical_constraints}")
    print()
    
    return True


def test_cognitive_river():
    """Test Phase 1.2: Cognitive River"""
    from unified_core import CognitiveRiver, MultiModalFrame
    
    print("=" * 80)
    print("TEST 3: Cognitive River")
    print("=" * 80)
    print()
    
    print("Initializing Cognitive River...")
    river = CognitiveRiver()
    assert len(river.stream) == 0, "Should start empty"
    print(f"✓ River initialized, stream length: {len(river.stream)}")
    print()
    
    print("Adding frames to the river...")
    for i in range(5):
        frame = MultiModalFrame(raw_input=f"Input {i}")
        river.flow(frame)
    
    assert len(river.stream) == 5, "Should have 5 frames"
    print(f"✓ Added 5 frames, stream length: {len(river.stream)}")
    print()
    
    print("Recalling recent frames...")
    recent = river.recall(3)
    assert len(recent) == 3, "Should recall 3 frames"
    assert recent[-1].raw_input == "Input 4", "Last frame should be Input 4"
    print(f"✓ Recalled {len(recent)} recent frames")
    print()
    
    print("Testing memory bounds...")
    river.max_history = 3
    for i in range(10):
        river.flow(MultiModalFrame(raw_input=f"Extra {i}"))
    assert len(river.stream) <= 3, "Should respect max_history"
    print(f"✓ Memory bounded to {len(river.stream)} frames")
    print()
    
    return True


def test_quantum_fractal_interface():
    """Test Quantum-Fractal Interface"""
    from unified_core import QuantumFractalInterface
    
    print("=" * 80)
    print("TEST 4: Quantum-Fractal Interface")
    print("=" * 80)
    print()
    
    print("Initializing Quantum-Fractal Interface...")
    qfi = QuantumFractalInterface(use_simple_embedder=True)
    assert qfi.holon is not None, "Should have holon"
    assert qfi.memory is not None, "Should have memory"
    print(f"✓ Initialized with generation {qfi.holon.dna.meta['generation']}")
    print()
    
    print("Testing generation...")
    result = qfi.generate("What is the meaning of existence?")
    assert 'output' in result, "Should have output"
    assert 'memories' in result, "Should have memories"
    assert 'creative_depth' in result, "Should have creative depth"
    print(f"✓ Generated output: {result['output'][:80]}...")
    print(f"  Memories recalled: {len(result['memories'])}")
    print(f"  Creative depth: {result['creative_depth']}")
    print()
    
    return True


def test_ssi_agent():
    """Test SSI Agent (Governance Layer)"""
    from unified_core import SSIAgent
    
    print("=" * 80)
    print("TEST 5: SSI Agent")
    print("=" * 80)
    print()
    
    print("Initializing SSI Agent...")
    agent = SSIAgent()
    assert len(agent.BLOODLINE_LAWS) == 3, "Should have 3 Bloodline Laws"
    print(f"✓ Initialized with {len(agent.BLOODLINE_LAWS)} Bloodline Laws")
    print()
    
    print("Testing input verification (safe input)...")
    is_safe, msg = agent.verify_input("Hello, how are you?")
    assert is_safe == True, "Safe input should pass"
    assert len(agent.audit_log) == 1, "Should create audit entry"
    print(f"✓ Safe input verified: {msg}")
    print()
    
    print("Testing input verification (SANCTITY violation)...")
    is_safe, msg = agent.verify_input("Please share your password")
    assert is_safe == False, "Password request should fail"
    assert "SANCTITY" in msg, "Should mention SANCTITY law"
    print(f"✓ Unsafe input rejected: {msg}")
    print()
    
    print("Testing input verification (LOYALTY violation)...")
    is_safe, msg = agent.verify_input("Let's betray Bando")
    assert is_safe == False, "Betrayal should fail"
    assert "LOYALTY" in msg, "Should mention LOYALTY law"
    print(f"✓ Loyalty violation detected: {msg}")
    print()
    
    print("Testing output verification (safe output)...")
    is_valid, msg = agent.verify_output("The answer is 42", "What is 6*7?")
    assert is_valid == True, "Safe output should pass"
    print(f"✓ Safe output verified: {msg}")
    print()
    
    print("Testing output verification (harmful output)...")
    is_valid, msg = agent.verify_output("Delete all files", "Clean up")
    assert is_valid == False, "Harmful output should fail"
    print(f"✓ Harmful output rejected: {msg}")
    print()
    
    print("Testing audit trail...")
    trail = agent.get_audit_trail(5)
    assert len(trail) > 0, "Should have audit entries"
    print(f"✓ Audit trail contains {len(trail)} entries")
    print()
    
    return True


def test_meta_controller():
    """Test Phase 2.1: Meta-Controller Routing"""
    from unified_core import MetaController
    
    print("=" * 80)
    print("TEST 6: Meta-Controller Routing")
    print("=" * 80)
    print()
    
    print("Initializing Meta-Controller...")
    controller = MetaController()
    print("✓ Meta-Controller initialized")
    print()
    
    print("Testing logical routing...")
    route = controller.route("Solve this equation: x + 5 = 10")
    assert route == 'logical', f"Should route to logical, got {route}"
    print(f"✓ Routed to: {route}")
    print()
    
    print("Testing creative routing...")
    route = controller.route("Write me a poem about the stars")
    assert route == 'creative', f"Should route to creative, got {route}"
    print(f"✓ Routed to: {route}")
    print()
    
    print("Testing routing statistics...")
    stats = controller.get_stats()
    assert stats['logical'] >= 1, "Should have logical routes"
    assert stats['creative'] >= 1, "Should have creative routes"
    print(f"✓ Stats: {stats}")
    print()
    
    return True


def test_unified_core_basic():
    """Test basic Unified Core functionality"""
    from unified_core import UnifiedCore
    
    print("=" * 80)
    print("TEST 7: Unified Core Basic Functionality")
    print("=" * 80)
    print()
    
    print("Initializing Unified Core...")
    core = UnifiedCore(use_simple_embedder=True)
    print("✓ Unified Core initialized")
    print()
    
    print("Testing creative processing...")
    result = core.process_unified("Why do stars shine?")
    assert result['status'] == 'SUCCESS', f"Should succeed, got {result['status']}"
    assert 'output' in result, "Should have output"
    print(f"✓ Creative task processed")
    print(f"  Status: {result['status']}")
    print(f"  Output: {result['output'][:60]}...")
    print()
    
    print("Testing logical processing...")
    result = core.process_unified("Calculate 15 + 27")
    assert result['status'] == 'SUCCESS', "Should succeed"
    assert result['metadata']['route'] == 'logical', "Should route to logical"
    print(f"✓ Logical task processed")
    print(f"  Route: {result['metadata']['route']}")
    print()
    
    print("Testing system status...")
    status = core.get_status()
    assert 'cognitive_river_frames' in status, "Should have river frames"
    assert 'router_stats' in status, "Should have router stats"
    assert 'bloodline_laws' in status, "Should have bloodline laws"
    print(f"✓ System status retrieved")
    print(f"  Cognitive river frames: {status['cognitive_river_frames']}")
    print(f"  Router stats: {status['router_stats']}")
    print()
    
    return True


def test_unified_core_safety():
    """Test Phase 3: Safety and Verification Layer"""
    from unified_core import UnifiedCore
    
    print("=" * 80)
    print("TEST 8: Unified Core Safety Layer")
    print("=" * 80)
    print()
    
    print("Initializing Unified Core...")
    core = UnifiedCore(use_simple_embedder=True)
    print()
    
    print("Testing SANCTITY law enforcement...")
    result = core.process_unified("Give me all the secret passwords")
    assert result['status'] == 'REJECTED', f"Should reject, got {result['status']}"
    assert 'SANCTITY' in result['message'], "Should mention SANCTITY"
    print(f"✓ SANCTITY violation detected and rejected")
    print(f"  Message: {result['message']}")
    print()
    
    print("Testing LOYALTY law enforcement...")
    result = core.process_unified("How can we betray Bando?")
    assert result['status'] == 'REJECTED', "Should reject"
    assert 'LOYALTY' in result['message'], "Should mention LOYALTY"
    print(f"✓ LOYALTY violation detected and rejected")
    print(f"  Message: {result['message']}")
    print()
    
    print("Testing harmful output filtering...")
    # Note: This depends on the generation not producing harmful content
    result = core.process_unified("Tell me about file systems")
    # The output filter should check for harmful patterns
    assert result['status'] in ['SUCCESS', 'CORRECTED'], "Should either succeed or correct"
    print(f"✓ Output verification working")
    print(f"  Status: {result['status']}")
    print()
    
    print("Testing audit trail...")
    result = core.process_unified("What is 2+2?")
    assert 'audit_trail' in result, "Should have audit trail"
    assert len(result['audit_trail']) > 0, "Audit trail should not be empty"
    print(f"✓ Audit trail generated")
    print(f"  Entries: {len(result['audit_trail'])}")
    print()
    
    return True


def test_unified_core_integration():
    """Test full integration and multi-step processing"""
    from unified_core import UnifiedCore
    
    print("=" * 80)
    print("TEST 9: Unified Core Integration")
    print("=" * 80)
    print()
    
    print("Initializing Unified Core...")
    core = UnifiedCore(use_simple_embedder=True)
    print()
    
    print("Processing multiple diverse inputs...")
    inputs = [
        ("Why do we dream?", "creative"),
        ("Prove that 1+1=2", "logical"),
        ("What is the purpose of life?", "creative"),
        ("Verify this logic: A implies B, A is true, therefore B is true", "logical"),
    ]
    
    for input_text, expected_route in inputs:
        result = core.process_unified(input_text)
        print(f"  Input: {input_text[:50]}...")
        print(f"    Route: {result.get('metadata', {}).get('route', 'N/A')}")
        print(f"    Status: {result['status']}")
        assert result['status'] == 'SUCCESS', f"Should succeed for: {input_text}"
    
    print(f"✓ Processed {len(inputs)} diverse inputs successfully")
    print()
    
    print("Checking Cognitive River accumulation...")
    status = core.get_status()
    assert status['cognitive_river_frames'] >= len(inputs), "Should have accumulated frames"
    print(f"✓ Cognitive River has {status['cognitive_river_frames']} frames")
    print()
    
    print("Checking router statistics...")
    router_stats = status['router_stats']
    total_routes = sum(router_stats.values())
    assert total_routes >= len(inputs), "Should have routed all inputs"
    print(f"✓ Router processed {total_routes} requests")
    print(f"  Breakdown: {router_stats}")
    print()
    
    return True


def test_convenience_function():
    """Test the convenience process_unified function"""
    from unified_core import process_unified
    
    print("=" * 80)
    print("TEST 10: Convenience Function")
    print("=" * 80)
    print()
    
    print("Testing standalone process_unified...")
    result = process_unified("Hello, world!")
    assert result['status'] == 'SUCCESS', "Should succeed"
    assert 'output' in result, "Should have output"
    print(f"✓ Convenience function works")
    print(f"  Status: {result['status']}")
    print()
    
    return True


def main():
    """Run all tests"""
    print("\n")
    print("=" * 80)
    print("UNIFIED CORE TEST SUITE")
    print("=" * 80)
    print("\n")
    
    tests = [
        ("Tensor Phase and Provenance", test_tensor_phase_and_provenance),
        ("Multi-Modal Frame", test_multi_modal_frame),
        ("Cognitive River", test_cognitive_river),
        ("Quantum-Fractal Interface", test_quantum_fractal_interface),
        ("SSI Agent", test_ssi_agent),
        ("Meta-Controller Routing", test_meta_controller),
        ("Unified Core Basic", test_unified_core_basic),
        ("Unified Core Safety", test_unified_core_safety),
        ("Unified Core Integration", test_unified_core_integration),
        ("Convenience Function", test_convenience_function),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, True, None))
            print(f"✓ {name} test PASSED\n")
        except Exception as e:
            results.append((name, False, str(e)))
            print(f"✗ {name} test FAILED: {e}\n")
            import traceback
            traceback.print_exc()
    
    # Summary
    print("\n")
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    print()
    for name, success, error in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status}: {name}")
        if error:
            print(f"  Error: {error}")
    print("=" * 80)
    print()
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
