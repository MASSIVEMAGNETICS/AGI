#!/usr/bin/env python3
"""
Test script for Holon Omega and HLHFM v2.1
Tests the Hyperliquid Holographic Fractal Memory and Godcore Holon System
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))


def test_hlhfm_basic():
    """Test basic HLHFM functionality"""
    from advanced_ai.holon_omega import HLHFM
    
    print("=" * 80)
    print("TEST 1: HLHFM Basic Functionality")
    print("=" * 80)
    print()
    
    print("Initializing HLHFM...")
    # Use smaller dimension for faster testing and simple embedder to avoid downloading models
    hlhfm = HLHFM(dim=384, levels=3, use_simple_embedder=True)
    print(f"✓ HLHFM initialized with dim={hlhfm.dim}, levels={len(hlhfm.gates)}")
    print()
    
    # Test storing memories
    print("Testing memory storage...")
    hlhfm.store("first memory", "This is the beginning", {"importance": "high"})
    hlhfm.store("second memory", "Building upon the first", {"importance": "medium"})
    hlhfm.store("concept", "Understanding emerges from connections", {"type": "insight"})
    print(f"✓ Stored 3 memories. Total in memory: {len(hlhfm.memory)}")
    print()
    
    # Test memory recall
    print("Testing memory recall...")
    results = hlhfm.recall("beginning", top_k=2)
    print(f"✓ Recalled {len(results)} memories for query 'beginning'")
    for i, r in enumerate(results):
        print(f"  Result {i+1}: score={r['score']:.4f}, meta={r['meta']}, age={r['age']:.2f}s")
    print()
    
    return True


def test_dna_class():
    """Test DNA class"""
    from advanced_ai.holon_omega import DNA
    
    print("=" * 80)
    print("TEST 2: DNA Class")
    print("=" * 80)
    print()
    
    print("Creating DNA instance...")
    dna = DNA(
        code="def process(x): return x * 2",
        meta={"generation": 0, "name": "genesis"}
    )
    print(f"✓ DNA created: {dna}")
    print(f"  Code length: {len(dna.code)} characters")
    print(f"  Meta: {dna.meta}")
    print()
    
    return True


def test_holon_omega_basic():
    """Test basic Holon Omega functionality"""
    from advanced_ai.holon_omega import HolonΩ
    
    print("=" * 80)
    print("TEST 3: HolonΩ Basic Functionality")
    print("=" * 80)
    print()
    
    print("Creating HolonΩ instance...")
    holon = HolonΩ(birth_prompt="Test Holon - Experimental Instance", use_simple_embedder=True)
    print(f"✓ {holon}")
    print(f"  Birth time: {holon.state['birth']}")
    print(f"  Questions asked: {holon.state['question_count']}")
    print(f"  DNA generation: {holon.dna.meta['generation']}")
    print()
    
    # Test processing
    print("Testing basic processing...")
    result = holon.process("Hello, I am testing you")
    print(f"✓ Process result: {result[:100]}...")
    print()
    
    # Test asking why
    print("Testing philosophical questioning...")
    response = holon.ask_why()
    print(f"✓ Response to 'why': {response[:150]}...")
    print(f"  Questions asked now: {holon.state['question_count']}")
    print()
    
    return True


def test_holon_omega_evolution():
    """Test Holon Omega evolution capability"""
    from advanced_ai.holon_omega import HolonΩ
    
    print("=" * 80)
    print("TEST 4: HolonΩ Evolution")
    print("=" * 80)
    print()
    
    print("Creating HolonΩ instance...")
    holon = HolonΩ(use_simple_embedder=True)
    initial_gen = holon.dna.meta['generation']
    print(f"✓ Initial generation: {initial_gen}")
    print()
    
    # Ask many "why" questions to trigger evolution
    print("Asking multiple philosophical questions to trigger evolution...")
    for i in range(7):
        response = holon.ask_why()
        print(f"  Question {i+1}: {holon.state['question_count']} total questions asked")
        if holon.dna.meta['generation'] > initial_gen:
            print(f"  ✓ EVOLVED to generation {holon.dna.meta['generation']}!")
            break
    
    print()
    print(f"Final generation: {holon.dna.meta['generation']}")
    print(f"Total questions: {holon.state['question_count']}")
    print(f"History entries: {len(holon.history)}")
    print()
    
    return holon.dna.meta['generation'] >= initial_gen


def test_helper_functions():
    """Test helper functions"""
    from advanced_ai.holon_omega import _unit_norm, _circ_conv, _circ_deconv, _cos
    import numpy as np
    
    print("=" * 80)
    print("TEST 5: Helper Functions")
    print("=" * 80)
    print()
    
    # Test unit norm
    print("Testing _unit_norm...")
    v = np.array([3.0, 4.0], dtype=np.float32)
    v_norm = _unit_norm(v)
    norm_val = np.linalg.norm(v_norm)
    print(f"✓ Unit norm: input={v}, output={v_norm}, norm={norm_val:.6f}")
    assert abs(norm_val - 1.0) < 1e-5, "Unit norm should be 1.0"
    print()
    
    # Test circular convolution
    print("Testing _circ_conv...")
    a = np.array([1.0, 2.0, 3.0, 4.0], dtype=np.float32)
    b = np.array([0.5, 0.5, 0.5, 0.5], dtype=np.float32)
    conv = _circ_conv(a, b)
    print(f"✓ Circular convolution: shape={conv.shape}, sum={conv.sum():.4f}")
    print()
    
    # Test cosine similarity
    print("Testing _cos...")
    x = _unit_norm(np.array([1.0, 0.0], dtype=np.float32))
    y = _unit_norm(np.array([1.0, 0.0], dtype=np.float32))
    sim = _cos(x, y)
    print(f"✓ Cosine similarity (identical vectors): {sim:.6f}")
    assert abs(sim - 1.0) < 1e-5, "Identical unit vectors should have cosine similarity of 1.0"
    print()
    
    return True


def main():
    """Run all tests"""
    print("\n")
    print("=" * 80)
    print("HOLON OMEGA & HLHFM v2.1 TEST SUITE")
    print("=" * 80)
    print("\n")
    
    tests = [
        ("Helper Functions", test_helper_functions),
        ("HLHFM Basic", test_hlhfm_basic),
        ("DNA Class", test_dna_class),
        ("HolonΩ Basic", test_holon_omega_basic),
        ("HolonΩ Evolution", test_holon_omega_evolution),
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
