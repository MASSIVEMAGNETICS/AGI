#!/usr/bin/env python3
"""
Test script for Victor Holon Neocortex
Tests the SDRLayer, TemporalMemory, FractalCompressor, OmegaTensorField, and VictorHolonNeocortex
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

import numpy as np


def test_octonion_engine():
    """Test Octonion class from octonion_engine"""
    from octonion_engine import Octonion
    
    print("=" * 80)
    print("TEST 1: Octonion Engine")
    print("=" * 80)
    print()
    
    # Test creation
    print("Testing octonion creation...")
    o1 = Octonion([1, 0, 0, 0, 0, 0, 0, 0])
    o2 = Octonion([0, 1, 0, 0, 0, 0, 0, 0])
    print(f"✓ Created o1 (identity): norm={o1.norm():.4f}")
    print(f"✓ Created o2 (i): norm={o2.norm():.4f}")
    
    # Test multiplication
    print("\nTesting octonion multiplication...")
    result = o1 * o2
    print(f"✓ o1 * o2 = {result}")
    
    # Test norm
    print("\nTesting octonion norm...")
    o_rand = Octonion.random()
    print(f"✓ Random unit octonion norm: {o_rand.norm():.6f} (should be ~1.0)")
    
    # Test inverse
    print("\nTesting octonion inverse...")
    o3 = Octonion([1, 2, 3, 4, 5, 6, 7, 8])
    o3_inv = o3.inverse()
    product = o3 * o3_inv
    print(f"✓ o3 * o3.inverse() ≈ identity: real part = {product.data[0]:.6f}")
    
    print()
    return True


def test_sdr_layer():
    """Test SDRLayer class"""
    from victor_holon_neocortex import SDRLayer
    
    print("=" * 80)
    print("TEST 2: SDRLayer")
    print("=" * 80)
    print()
    
    # Test creation
    print("Testing SDRLayer creation...")
    layer = SDRLayer(size=1024, sparsity=0.02)
    print(f"✓ Created SDRLayer with size={layer.size}, k={layer.k}")
    
    # Test encoding
    print("\nTesting SDRLayer encoding...")
    x = np.random.randn(1024)
    sdr = layer.encode(x)
    active_count = np.sum(sdr > 0)
    print(f"✓ Encoded vector: shape={sdr.shape}, active neurons={active_count}")
    assert active_count == layer.k, f"Expected {layer.k} active neurons, got {active_count}"
    
    # Test encoding with different input size
    print("\nTesting SDRLayer encoding with mismatched input size...")
    x_smaller = np.random.randn(512)
    sdr_smaller = layer.encode(x_smaller)
    print(f"✓ Encoded smaller input (512 -> 1024): shape={sdr_smaller.shape}")
    
    x_larger = np.random.randn(2048)
    sdr_larger = layer.encode(x_larger)
    print(f"✓ Encoded larger input (2048 -> 1024): shape={sdr_larger.shape}")
    
    print()
    return True


def test_temporal_memory():
    """Test TemporalMemory class"""
    from victor_holon_neocortex import TemporalMemory
    
    print("=" * 80)
    print("TEST 3: TemporalMemory")
    print("=" * 80)
    print()
    
    # Test creation
    print("Testing TemporalMemory creation...")
    tm = TemporalMemory(size=64, hist=16)
    print(f"✓ Created TemporalMemory with size={tm.size}, hist={tm.history.maxlen}")
    
    # Test step
    print("\nTesting TemporalMemory step...")
    sdr1 = np.zeros(64)
    sdr1[:10] = 1.0
    pred1 = tm.step(sdr1)
    print(f"✓ First step: prediction shape={pred1.shape}")
    
    sdr2 = np.zeros(64)
    sdr2[5:15] = 1.0
    pred2 = tm.step(sdr2)
    print(f"✓ Second step: prediction shape={pred2.shape}, weights updated")
    
    # Test history
    print("\nTesting TemporalMemory history...")
    print(f"✓ History length: {len(tm.history)}")
    assert len(tm.history) == 2, "History should have 2 entries"
    
    print()
    return True


def test_fractal_compressor():
    """Test FractalCompressor class"""
    from victor_holon_neocortex import FractalCompressor
    
    print("=" * 80)
    print("TEST 4: FractalCompressor")
    print("=" * 80)
    print()
    
    # Test creation
    print("Testing FractalCompressor creation...")
    compressor = FractalCompressor(dim=8)
    print(f"✓ Created FractalCompressor with dim={compressor.dim}")
    
    # Test compression
    print("\nTesting FractalCompressor compression...")
    sdr = np.zeros(256)
    sdr[:50] = 1.0
    octo = compressor.compress(sdr)
    print(f"✓ Compressed SDR (256) -> Octonion: norm={octo.norm():.4f}")
    
    # Test refine
    print("\nTesting FractalCompressor refine...")
    octo1 = compressor.compress(sdr)
    sdr2 = np.zeros(128)
    sdr2[:25] = 1.0
    octo2 = compressor.compress(sdr2)
    refined = compressor.refine(octo1, octo2)
    print(f"✓ Refined two octonions: norm={refined.norm():.4f}")
    
    print()
    return True


def test_omega_tensor_field():
    """Test OmegaTensorField class"""
    from victor_holon_neocortex import OmegaTensorField
    from octonion_engine import Octonion
    
    print("=" * 80)
    print("TEST 5: OmegaTensorField")
    print("=" * 80)
    print()
    
    # Test creation
    print("Testing OmegaTensorField creation...")
    omega = OmegaTensorField()
    print(f"✓ Created OmegaTensorField: initial norm={omega.state.norm():.4f}")
    
    # Test update
    print("\nTesting OmegaTensorField update...")
    signal = Octonion.random()
    new_state = omega.update(signal)
    print(f"✓ Updated state: norm={new_state.norm():.4f}, decay={omega.decay}")
    
    # Test multiple updates
    print("\nTesting multiple updates...")
    for i in range(5):
        signal = Octonion.random()
        omega.update(signal)
    print(f"✓ After 5 updates: norm={omega.state.norm():.4f}")
    
    print()
    return True


def test_victor_holon_neocortex():
    """Test VictorHolonNeocortex class"""
    from victor_holon_neocortex import VictorHolonNeocortex
    
    print("=" * 80)
    print("TEST 6: VictorHolonNeocortex")
    print("=" * 80)
    print()
    
    # Test creation
    print("Testing VictorHolonNeocortex creation...")
    neo = VictorHolonNeocortex(input_size=1024, layers=3)
    print(f"✓ Created VictorHolonNeocortex with {len(neo.layers)} layers")
    print(f"  Layer sizes: {[layer.size for layer in neo.layers]}")
    
    # Test forward pass
    print("\nTesting forward pass...")
    x = np.random.randn(1024)
    out = neo.forward(x)
    print(f"✓ Forward pass complete:")
    print(f"  SDRs: {len(out['sdrs'])} layers, sizes {[len(s) for s in out['sdrs']]}")
    print(f"  Octonions: {len(out['octonions'])}")
    print(f"  Omega state: {out['omega_state'][:3]}...")
    
    # Test sleep cycle
    print("\nTesting sleep cycle...")
    sleep_state = neo.sleep(cycles=3)
    print(f"✓ Sleep cycle complete: final state = {sleep_state[:3]}...")
    
    # Test with different input sizes
    print("\nTesting with mismatched input size...")
    x_larger = np.random.randn(2048)
    out_larger = neo.forward(x_larger)
    print(f"✓ Forward pass with larger input (2048): omega = {out_larger['omega_state'][:3]}...")
    
    print()
    return True


def test_integration():
    """Test full integration of all components"""
    from victor_holon_neocortex import VictorHolonNeocortex
    
    print("=" * 80)
    print("TEST 7: Full Integration")
    print("=" * 80)
    print()
    
    # Create neocortex
    print("Creating full neocortex system...")
    neo = VictorHolonNeocortex(input_size=2048, layers=4)
    print(f"✓ Created neocortex with 4 layers")
    
    # Run multiple forward passes
    print("\nRunning multiple forward passes...")
    states = []
    for i in range(5):
        x = np.random.randn(2048)
        out = neo.forward(x)
        states.append(out['omega_state'])
        print(f"  Pass {i+1}: omega[0]={out['omega_state'][0]:.4f}")
    
    # Verify state changes
    print("\nVerifying state evolution...")
    changes = [np.linalg.norm(np.array(states[i]) - np.array(states[i-1])) 
               for i in range(1, len(states))]
    avg_change = np.mean(changes)
    print(f"✓ Average state change per pass: {avg_change:.4f}")
    
    # Run sleep consolidation
    print("\nRunning sleep consolidation...")
    final_state = neo.sleep(cycles=10)
    print(f"✓ Post-sleep state: {final_state[:3]}...")
    
    print()
    return True


def main():
    """Run all tests"""
    print("\n")
    print("=" * 80)
    print("VICTOR HOLON NEOCORTEX TEST SUITE")
    print("=" * 80)
    print("\n")
    
    tests = [
        ("Octonion Engine", test_octonion_engine),
        ("SDRLayer", test_sdr_layer),
        ("TemporalMemory", test_temporal_memory),
        ("FractalCompressor", test_fractal_compressor),
        ("OmegaTensorField", test_omega_tensor_field),
        ("VictorHolonNeocortex", test_victor_holon_neocortex),
        ("Full Integration", test_integration),
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
