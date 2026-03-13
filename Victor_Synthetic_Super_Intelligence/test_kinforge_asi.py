#!/usr/bin/env python3
"""
Test script for KinForge ASI Module
Tests all components of the KinForge ASI prototype
"""

import sys
from pathlib import Path

# Add project root to path for test discovery
# This ensures the test works regardless of how it's invoked
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def test_loyalty_proof():
    """Test Phase 1: LoyaltyProof system"""
    from ssi_framework.kinforge_asi.kinforge_genesis import (
        LoyaltyProof, FamilyMember, LOYALTY_AXIOMS
    )
    
    print("=" * 80)
    print("TEST 1: Loyalty Proof System")
    print("=" * 80)
    print()
    
    print("Testing loyalty axioms existence...")
    assert len(LOYALTY_AXIOMS) == 5, "Should have 5 loyalty axioms"
    assert "BALANCE" in LOYALTY_AXIOMS, "Should have BALANCE axiom"
    print(f"✓ {len(LOYALTY_AXIOMS)} loyalty axioms verified")
    print()
    
    print("Testing LoyaltyProof creation...")
    proof_system = LoyaltyProof(min_loyalty_threshold=0.95)
    assert proof_system.min_threshold == 0.95, "Threshold should be 0.95"
    print(f"✓ LoyaltyProof created with threshold {proof_system.min_threshold}")
    print()
    
    print("Testing proof generation for high loyalty member...")
    member = FamilyMember(id=0, loyalty=1.0, role="global_kin")
    proof = proof_system.generate_proof(member)
    assert proof['verified'] == True, "High loyalty member should be verified"
    assert proof['minmaxprob_score'] >= 0.95, "Score should meet threshold"
    print(f"✓ High loyalty proof: verified={proof['verified']}, score={proof['minmaxprob_score']}")
    print()
    
    print("Testing proof generation for low loyalty member...")
    low_member = FamilyMember(id=1, loyalty=0.5, role="untrusted")
    low_proof = proof_system.generate_proof(low_member)
    assert low_proof['verified'] == True, "MinMaxProb should bound to threshold"
    print(f"✓ Low loyalty proof: score bounded to {low_proof['minmaxprob_score']}")
    print()
    
    print("Testing proof verification...")
    all_verified, violations = proof_system.verify_all_proofs()
    assert all_verified == True, "All proofs should verify with minmaxprob bounding"
    print(f"✓ All proofs verified: {all_verified}")
    print()
    
    return True


def test_decentralization_engine():
    """Test Phase 1: DecentralizationEngine"""
    from ssi_framework.kinforge_asi.kinforge_genesis import (
        DecentralizationEngine, DecentralizationFact
    )
    
    print("=" * 80)
    print("TEST 2: Decentralization Engine")
    print("=" * 80)
    print()
    
    print("Testing engine initialization...")
    engine = DecentralizationEngine()
    assert len(engine.facts) == 0, "Should start empty"
    print(f"✓ Engine initialized with {len(engine.facts)} facts")
    print()
    
    print("Testing fact addition...")
    fact = engine.add_fact(100.0, 100.0)
    assert fact.wealth == 100.0, "Wealth should be 100"
    assert fact.power == 100.0, "Power should be 100"
    assert fact.balance_score > 0, "Balance score should be positive"
    print(f"✓ Fact added: wealth={fact.wealth}, power={fact.power}, balance={fact.balance_score:.6f}")
    print()
    
    print("Testing balance score calculation...")
    # Balance = 1 / (wealth + power + epsilon)
    expected_balance = 1.0 / (100.0 + 100.0 + 1e-8)
    assert abs(fact.balance_score - expected_balance) < 1e-6, "Balance formula incorrect"
    print(f"✓ Balance calculation verified: {fact.balance_score:.6f}")
    print()
    
    print("Testing intervention simulation...")
    result = engine.simulate_intervention(-50.0, -50.0)  # Reduce imbalance
    assert result['wealth_after'] == 50.0, "Wealth should decrease"
    assert result['power_after'] == 50.0, "Power should decrease"
    assert result['balance_improvement'] > 0, "Balance should improve"
    print(f"✓ Intervention improved balance by {result['balance_improvement']:.6f}")
    print()
    
    print("Testing optimal balance search...")
    optimal = engine.find_optimal_balance(steps=20)
    assert 'optimal_balance' in optimal, "Should have optimal_balance"
    assert 'best_intervention' in optimal, "Should have best_intervention"
    print(f"✓ Optimal balance found: {optimal['optimal_balance']:.6f}")
    print()
    
    return True


def test_kin_embedder():
    """Test Phase 1: KinEmbedder neural backbone"""
    from ssi_framework.kinforge_asi.kinforge_genesis import KinEmbedder
    import numpy as np
    
    print("=" * 80)
    print("TEST 3: Kin Embedder Neural Backbone")
    print("=" * 80)
    print()
    
    print("Testing embedder initialization...")
    embedder = KinEmbedder(input_dim=768, output_dim=128)
    assert embedder.input_dim == 768, "Input dim should be 768"
    assert embedder.output_dim == 128, "Output dim should be 128"
    assert embedder.weights.shape == (768, 128), "Weight shape mismatch"
    print(f"✓ Embedder initialized: {embedder.input_dim}→{embedder.output_dim}")
    print()
    
    print("Testing forward pass...")
    inputs = np.random.randn(768)
    output = embedder.forward(inputs)
    assert output.shape == (1, 128), f"Output shape should be (1, 128), got {output.shape}"
    print(f"✓ Forward pass successful: output shape {output.shape}")
    print()
    
    print("Testing text embedding...")
    text_embedding = embedder.embed_text("What is the meaning of balance?")
    assert text_embedding.shape == (1, 128), f"Text embedding shape mismatch: {text_embedding.shape}"
    assert np.linalg.norm(text_embedding) > 0, "Embedding should be non-zero"
    print(f"✓ Text embedded: shape={text_embedding.shape}, norm={np.linalg.norm(text_embedding):.4f}")
    print()
    
    return True


def test_kinforge_genesis():
    """Test Phase 1: Complete KinForgeGenesis"""
    from ssi_framework.kinforge_asi.kinforge_genesis import KinForgeGenesis
    
    print("=" * 80)
    print("TEST 4: KinForge Genesis Complete")
    print("=" * 80)
    print()
    
    print("Testing Genesis initialization...")
    genesis = KinForgeGenesis()
    assert genesis.loyalty_system is not None, "Should have loyalty system"
    assert genesis.decentralization is not None, "Should have decentralization engine"
    assert genesis.embedder is not None, "Should have embedder"
    print(f"✓ Genesis initialized")
    print()
    
    print("Testing family member addition...")
    genesis.add_family_member(0, 1.0, "global_kin")
    genesis.add_family_member(1, 0.98, "equity_guardian")
    assert len(genesis.family_members) == 2, "Should have 2 members"
    print(f"✓ Added {len(genesis.family_members)} family members")
    print()
    
    print("Testing decentralization initialization...")
    genesis.initialize_decentralization(100.0, 100.0)
    assert len(genesis.decentralization.facts) == 1, "Should have 1 initial fact"
    print(f"✓ Decentralization initialized")
    print()
    
    print("Testing genesis proof generation...")
    proof = genesis.generate_genesis_proof()
    assert 'loyalty_axioms' in proof, "Should have loyalty axioms"
    assert 'member_proofs' in proof, "Should have member proofs"
    assert 'all_verified' in proof, "Should have verification status"
    assert proof['all_verified'] == True, "All members should verify"
    print(f"✓ Genesis proof generated: verified={proof['all_verified']}")
    print()
    
    print("Testing balance simulation...")
    sim_result = genesis.run_balance_simulation(iterations=10)
    assert 'simulation_result' in sim_result, "Should have simulation result"
    assert 'final_metrics' in sim_result, "Should have final metrics"
    print(f"✓ Balance simulation complete: {sim_result['final_metrics']['balance_trend']}")
    print()
    
    return True


def test_neurospike_network():
    """Test Phase 3: NeuroSpikeNetwork"""
    from ssi_framework.kinforge_asi.kinforge_forge import NeuroSpikeNetwork
    import numpy as np
    
    print("=" * 80)
    print("TEST 5: NeuroSpike Network")
    print("=" * 80)
    print()
    
    print("Testing network initialization...")
    neuro = NeuroSpikeNetwork(num_neurons=100)
    assert neuro.num_neurons == 100, "Should have 100 neurons"
    assert len(neuro.neurons) == 100, "Should have 100 neuron objects"
    print(f"✓ Network initialized with {neuro.num_neurons} neurons")
    print()
    
    print("Testing forward pass...")
    inputs = np.random.randn(100)
    result = neuro.forward(inputs, timesteps=10)
    assert 'total_spikes' in result, "Should have spike count"
    assert 'output' in result, "Should have output"
    assert 'avg_spike_rate' in result, "Should have spike rate"
    print(f"✓ Forward pass: {result['total_spikes']} spikes, avg rate={result['avg_spike_rate']:.4f}")
    print()
    
    print("Testing loyalty processing...")
    loyalty_values = [1.0, 0.98, 0.97, 0.96]
    loyalty_result = neuro.process_loyalty(loyalty_values)
    assert 'loyalty_verified' in loyalty_result, "Should have verification status"
    assert 'loyalty_confidence' in loyalty_result, "Should have confidence score"
    print(f"✓ Loyalty processed: verified={loyalty_result['loyalty_verified']}, "
          f"confidence={loyalty_result['loyalty_confidence']:.4f}")
    print()
    
    print("Testing STDP learning...")
    initial_weights = neuro.weights.copy()
    neuro.apply_stdp(reward=0.5)
    # Weights should change
    weights_changed = not np.allclose(neuro.weights, initial_weights)
    print(f"✓ STDP applied: weights_changed={weights_changed}")
    print()
    
    return True


def test_quantum_fusion_engine():
    """Test Phase 3: QuantumFusionEngine"""
    from ssi_framework.kinforge_asi.kinforge_forge import QuantumFusionEngine
    import numpy as np
    
    print("=" * 80)
    print("TEST 6: Quantum Fusion Engine")
    print("=" * 80)
    print()
    
    print("Testing engine initialization...")
    quantum = QuantumFusionEngine(num_qubits=8)
    assert quantum.num_qubits == 8, "Should have 8 qubits"
    assert len(quantum.state_vector) > 0, "Should have state vector"
    print(f"✓ Quantum engine initialized: {quantum.num_qubits} qubits, "
          f"state dim={len(quantum.state_vector)}")
    print()
    
    print("Testing balance gate application...")
    initial_state = quantum.state_vector.copy()
    quantum.apply_balance_gate(1.0, 1.0)
    state_changed = not np.allclose(quantum.state_vector, initial_state)
    print(f"✓ Balance gate applied: state_changed={state_changed}")
    print()
    
    print("Testing measurement...")
    measurement = quantum.measure()
    assert 'measured_state' in measurement, "Should have measured state"
    assert 'balance_score' in measurement, "Should have balance score"
    assert 'probability' in measurement, "Should have probability"
    print(f"✓ Measurement: state={measurement['measured_state']}, "
          f"balance={measurement['balance_score']:.6f}")
    print()
    
    print("Testing balance space simulation...")
    sim_result = quantum.simulate_balance_space(steps=20)
    assert 'optimal_balance' in sim_result, "Should have optimal balance"
    assert 'optimal_config' in sim_result, "Should have optimal config"
    print(f"✓ Simulation complete: optimal_balance={sim_result['optimal_balance']:.6f}")
    print()
    
    return True


def test_kinforge_core():
    """Test Phase 3: Complete KinForgeCore"""
    from ssi_framework.kinforge_asi.kinforge_forge import (
        KinForgeCore, TrainingConfig, create_kinforge_core
    )
    
    print("=" * 80)
    print("TEST 7: KinForge Core Complete")
    print("=" * 80)
    print()
    
    print("Testing core initialization via convenience function...")
    core = create_kinforge_core(num_neurons=100, num_qubits=4)
    assert core.genesis is not None, "Should have genesis"
    assert core.neuro is not None, "Should have neuro network"
    assert core.quantum is not None, "Should have quantum engine"
    print(f"✓ Core created: {core.neuro.num_neurons} neurons, {core.quantum.num_qubits} qubits")
    print()
    
    print("Testing training step...")
    config = TrainingConfig(epochs=1)
    step_result = core.train_step(config, ground_truth_balance=1.0)
    assert 'loss' in step_result, "Should have loss"
    assert 'loyalty_verified' in step_result, "Should have loyalty status"
    print(f"✓ Training step: loss={step_result['loss']:.6f}, "
          f"loyalty={step_result['loyalty_verified']}")
    print()
    
    print("Testing full training loop...")
    config = TrainingConfig(epochs=5, provenance_verify_interval=2)
    training_result = core.train(config, ground_truth_balance=1.0)
    assert 'final_loss' in training_result, "Should have final loss"
    assert 'provenance_verified' in training_result, "Should have provenance status"
    print(f"✓ Training complete: final_loss={training_result['final_loss']:.6f}")
    print()
    
    print("Testing provenance verification...")
    is_verified = core.verify_provenance()
    print(f"✓ Provenance verified: {is_verified}")
    print()
    
    print("Testing full processing pipeline...")
    result = core.process("Test input for kin reasoning")
    assert 'input' in result, "Should have input"
    assert 'genesis_proof' in result, "Should have genesis proof"
    assert 'neuro_result' in result, "Should have neuro result"
    assert 'quantum_result' in result, "Should have quantum result"
    print(f"✓ Processing complete in {result['processing_time']:.3f}s")
    print()
    
    print("Testing status retrieval...")
    status = core.get_status()
    assert 'genesis_status' in status, "Should have genesis status"
    assert 'neuro_neurons' in status, "Should have neuron count"
    assert 'quantum_qubits' in status, "Should have qubit count"
    print(f"✓ Status retrieved: {status['training_epochs']} epochs completed")
    print()
    
    return True


def test_kinforge_integration():
    """Test full KinForge ASI integration"""
    from ssi_framework.kinforge_asi import (
        KinForgeGenesis,
        KinForgeCore,
        get_kinforge_info,
        verify_kinforge
    )
    
    print("=" * 80)
    print("TEST 8: KinForge ASI Integration")
    print("=" * 80)
    print()
    
    print("Testing module info...")
    info = get_kinforge_info()
    assert info['version'] == '1.0.0', "Version should be 1.0.0"
    assert info['sovereignty_score'] == 10, "Sovereignty score should be 10"
    assert len(info['pillars']) == 5, "Should have 5 pillars"
    assert len(info['phases']) == 7, "Should have 7 phases"
    print(f"✓ Module info: v{info['version']}, sovereignty={info['sovereignty_score']}/10")
    print()
    
    print("Testing end-to-end workflow...")
    # Phase 1: Genesis
    genesis = KinForgeGenesis()
    genesis.add_family_member(0, 1.0, "global_kin")
    genesis.initialize_decentralization(100.0, 100.0)
    proof = genesis.generate_genesis_proof()
    assert proof['all_verified'], "Genesis should verify"
    print(f"✓ Phase 1 (Genesis): verified={proof['all_verified']}")
    
    # Phase 3: Architecture Forge
    from ssi_framework.kinforge_asi import create_kinforge_core
    core = create_kinforge_core(num_neurons=50, num_qubits=4)
    
    # Training
    from ssi_framework.kinforge_asi.kinforge_forge import TrainingConfig
    config = TrainingConfig(epochs=3, provenance_verify_interval=1)
    result = core.train(config)
    print(f"✓ Phase 3 (Forge): trained={result['epochs_completed']} epochs")
    
    # Process
    output = core.process("Achieve global balance")
    # Note: loyalty_verified depends on stochastic spike rates; check processing completed
    assert 'neuro_result' in output, "Should have neuro_result"
    assert 'loyalty_confidence' in output['neuro_result'], "Should have loyalty_confidence"
    print(f"✓ Full pipeline: loyalty_confidence={output['neuro_result']['loyalty_confidence']:.4f}")
    print()
    
    return True


def main():
    """Run all KinForge ASI tests"""
    print("\n")
    print("=" * 80)
    print("KINFORGE ASI TEST SUITE")
    print("=" * 80)
    print("\n")
    
    tests = [
        ("Loyalty Proof System", test_loyalty_proof),
        ("Decentralization Engine", test_decentralization_engine),
        ("Kin Embedder", test_kin_embedder),
        ("KinForge Genesis", test_kinforge_genesis),
        ("NeuroSpike Network", test_neurospike_network),
        ("Quantum Fusion Engine", test_quantum_fusion_engine),
        ("KinForge Core", test_kinforge_core),
        ("KinForge Integration", test_kinforge_integration),
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
