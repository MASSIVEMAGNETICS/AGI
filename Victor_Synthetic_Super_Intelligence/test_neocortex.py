#!/usr/bin/env python3
"""
Test script for Octonion Engine and Victor Holon Neocortex
Tests the octonion mathematics and the neocortex components
"""

import sys
from pathlib import Path
import numpy as np

# Add project root and advanced_ai directly to path to avoid __init__.py imports
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "advanced_ai"))

# Import directly from module files to avoid holon_omega torch dependency
from octonion_engine import Octonion
from victor_holon_neocortex import SDRLayer, TemporalMemory, FractalCompressor, OmegaTensorField, VictorHolonNeocortex


def test_octonion_creation():
    """Test Octonion creation and basic properties"""
    
    print("=" * 80)
    print("TEST 1: Octonion Creation")
    print("=" * 80)
    print()
    
    # Create zero octonion
    o0 = Octonion()
    print(f"✓ Zero octonion: norm={o0.norm():.6f}")
    assert o0.norm() < 1e-10, "Zero octonion should have zero norm"
    
    # Create unit octonion
    o1 = Octonion(np.array([1, 0, 0, 0, 0, 0, 0, 0]))
    print(f"✓ Unit real octonion: norm={o1.norm():.6f}")
    assert abs(o1.norm() - 1.0) < 1e-10, "Unit octonion should have norm 1"
    
    # Create normalized octonion
    o2 = Octonion(np.ones(8) / np.sqrt(8))
    print(f"✓ Normalized octonion: norm={o2.norm():.6f}")
    assert abs(o2.norm() - 1.0) < 1e-6, "Normalized octonion should have norm 1"
    
    print()
    return True


def test_octonion_multiplication():
    """Test Octonion multiplication"""
    
    print("=" * 80)
    print("TEST 2: Octonion Multiplication")
    print("=" * 80)
    print()
    
    # Multiply by identity (real 1)
    o1 = Octonion(np.array([1, 0, 0, 0, 0, 0, 0, 0]))
    o2 = Octonion(np.array([0.5, 0.3, 0.2, 0.1, 0.4, 0.5, 0.6, 0.7]))
    o3 = o1 * o2
    print(f"✓ Multiply by identity: {o3.data}")
    assert np.allclose(o3.data, o2.data), "Multiplying by identity should preserve value"
    
    # Multiply two octonions
    o4 = Octonion(np.ones(8) / np.sqrt(8))
    o5 = Octonion(np.array([1, -1, 1, -1, 1, -1, 1, -1]) / np.sqrt(8))
    o6 = o4 * o5
    print(f"✓ General multiplication: norm={o6.norm():.6f}")
    
    # Scalar multiplication
    o7 = o4 * 2.0
    print(f"✓ Scalar multiplication: norm ratio={o7.norm() / o4.norm():.6f}")
    assert abs(o7.norm() / o4.norm() - 2.0) < 1e-6, "Scalar multiplication should scale norm"
    
    print()
    return True


def test_octonion_operations():
    """Test other Octonion operations"""
    
    print("=" * 80)
    print("TEST 3: Octonion Operations")
    print("=" * 80)
    print()
    
    o = Octonion(np.array([1, 2, 3, 4, 5, 6, 7, 8]))
    
    # Conjugate
    o_conj = o.conjugate()
    print(f"✓ Conjugate: real unchanged={o.real() == o_conj.real()}, imag negated={np.allclose(o.imag(), -o_conj.imag())}")
    
    # Normalize
    o_norm = o.normalize()
    print(f"✓ Normalize: norm={o_norm.norm():.6f}")
    assert abs(o_norm.norm() - 1.0) < 1e-6, "Normalized octonion should have norm 1"
    
    # Inverse
    o_inv = o.inverse()
    o_identity = o * o_inv
    print(f"✓ Inverse: (o * o_inv).real={o_identity.real():.6f}")
    assert abs(o_identity.real() - 1.0) < 1e-6, "o * o_inv should be close to identity"
    
    # Addition
    o_sum = o + o
    print(f"✓ Addition: sum norm={o_sum.norm():.6f}")
    assert abs(o_sum.norm() - 2 * o.norm()) < 1e-6, "Sum should have double norm"
    
    print()
    return True


def test_sdr_layer():
    """Test SDRLayer"""
    
    print("=" * 80)
    print("TEST 4: SDRLayer")
    print("=" * 80)
    print()
    
    # Create layer
    layer = SDRLayer(size=1024, sparsity=0.02)
    print(f"✓ Created SDRLayer: size={layer.size}, k={layer.k}")
    
    # Encode
    x = np.random.randn(1024)
    sdr = layer.encode(x)
    sparsity = sdr.sum() / len(sdr)
    print(f"✓ Encoded input: output shape={sdr.shape}, sparsity={sparsity:.4f}")
    assert sdr.shape == (1024,), "SDR should have correct shape"
    assert abs(sparsity - 0.02) < 0.01, "SDR should have approximately correct sparsity"
    
    # Encode with different size input
    x2 = np.random.randn(2048)
    sdr2 = layer.encode(x2)
    print(f"✓ Encoded larger input: output shape={sdr2.shape}")
    assert sdr2.shape == (1024,), "SDR should resize input correctly"
    
    print()
    return True


def test_temporal_memory():
    """Test TemporalMemory"""
    
    print("=" * 80)
    print("TEST 5: TemporalMemory")
    print("=" * 80)
    print()
    
    tm = TemporalMemory(size=256, hist=16)
    print(f"✓ Created TemporalMemory: size={tm.size}")
    
    # Step through some SDRs
    for i in range(5):
        sdr = np.zeros(256)
        sdr[np.random.choice(256, 10, replace=False)] = 1.0
        pred = tm.step(sdr)
        print(f"  Step {i+1}: pred norm={np.linalg.norm(pred):.4f}")
    
    print(f"✓ History length: {len(tm.history)}")
    assert len(tm.history) == 5, "History should have 5 entries"
    
    print()
    return True


def test_fractal_compressor():
    """Test FractalCompressor"""
    
    print("=" * 80)
    print("TEST 6: FractalCompressor")
    print("=" * 80)
    print()
    
    fc = FractalCompressor(dim=8)
    print(f"✓ Created FractalCompressor: dim={fc.dim}")
    
    # Compress SDR
    sdr = np.zeros(512)
    sdr[np.random.choice(512, 10, replace=False)] = 1.0
    octo = fc.compress(sdr)
    print(f"✓ Compressed SDR to octonion: {octo}")
    assert isinstance(octo, Octonion), "Output should be Octonion"
    
    # Refine
    octo2 = fc.compress(sdr)
    refined = fc.refine(octo, octo2)
    print(f"✓ Refined octonions: norm={refined.norm():.6f}")
    assert isinstance(refined, Octonion), "Refined should be Octonion"
    
    print()
    return True


def test_omega_tensor_field():
    """Test OmegaTensorField"""
    
    print("=" * 80)
    print("TEST 7: OmegaTensorField")
    print("=" * 80)
    print()
    
    omega = OmegaTensorField()
    initial_norm = omega.state.norm()
    print(f"✓ Created OmegaTensorField: initial norm={initial_norm:.6f}")
    
    # Update with signal
    signal = Octonion(np.random.randn(8))
    new_state = omega.update(signal)
    print(f"✓ Updated state: norm={new_state.norm():.6f}")
    
    print()
    return True


def test_victor_holon_neocortex():
    """Test VictorHolonNeocortex"""
    
    print("=" * 80)
    print("TEST 8: VictorHolonNeocortex")
    print("=" * 80)
    print()
    
    neo = VictorHolonNeocortex(input_size=2048, layers=3)
    print(f"✓ Created VictorHolonNeocortex: {len(neo.layers)} layers")
    for i, layer in enumerate(neo.layers):
        print(f"  Layer {i}: size={layer.size}")
    
    # Forward pass
    x = np.random.randn(2048)
    out = neo.forward(x)
    print(f"✓ Forward pass:")
    print(f"  SDRs: {len(out['sdrs'])} (shapes: {[s.shape for s in out['sdrs']]})")
    print(f"  Octonions: {len(out['octonions'])}")
    print(f"  Omega state: {out['omega_state'][:3]}...")
    
    # Sleep cycle
    sleep_state = neo.sleep(cycles=3)
    print(f"✓ Sleep cycle completed: {sleep_state[:3]}...")
    
    print()
    return True


def main():
    """Run all tests"""
    print("\n")
    print("=" * 80)
    print("OCTONION ENGINE & VICTOR HOLON NEOCORTEX TEST SUITE")
    print("=" * 80)
    print("\n")
    
    tests = [
        ("Octonion Creation", test_octonion_creation),
        ("Octonion Multiplication", test_octonion_multiplication),
        ("Octonion Operations", test_octonion_operations),
        ("SDRLayer", test_sdr_layer),
        ("TemporalMemory", test_temporal_memory),
        ("FractalCompressor", test_fractal_compressor),
        ("OmegaTensorField", test_omega_tensor_field),
        ("VictorHolonNeocortex", test_victor_holon_neocortex),
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
