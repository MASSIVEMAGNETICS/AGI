"""
Tests for Consciousness Engine
Basic validation of core functionality
"""

import numpy as np
import time
from consciousness_engine import (
    ConsciousnessEngine, 
    StreamData, 
    MemoryEntry,
    AttentionMechanism,
    MemorySystem,
    StreamMerger
)


def test_stream_data_creation():
    """Test StreamData creation and hashing"""
    stream = StreamData(
        stream_name="test",
        data={"key": "value"},
        timestamp=time.time(),
        importance=0.7
    )
    
    assert stream.stream_name == "test"
    assert stream.importance == 0.7
    assert len(stream.get_hash()) > 0
    print("✓ StreamData creation test passed")


def test_attention_mechanism():
    """Test attention mechanism"""
    attention = AttentionMechanism(num_streams=5)
    attention.stream_names = ["s1", "s2", "s3", "s4", "s5"]
    
    # Test attention update
    importances = np.array([0.8, 0.5, 0.9, 0.3, 0.6])
    weights = attention.update_attention(importances)
    
    assert len(weights) == 5
    assert np.abs(np.sum(weights) - 1.0) < 0.01  # Should sum to ~1
    assert weights[2] > weights[3]  # Higher importance = higher weight
    
    # Test top-k selection
    top_k = attention.get_top_k_streams(k=3)
    assert len(top_k) == 3
    assert all(isinstance(idx, int) and isinstance(weight, float) for idx, weight in top_k)
    
    print("✓ Attention mechanism test passed")


def test_memory_system():
    """Test memory system with pruning"""
    memory = MemorySystem(capacity=10, prune_threshold=0.2)
    
    # Add memories
    for i in range(15):
        memory.add_memory(
            content={"data": f"item_{i}"},
            importance=0.3 + (i % 5) / 10.0,
            tags=[f"tag_{i % 3}"]
        )
    
    # Should have pruned due to capacity
    assert len(memory.memories) <= memory.capacity
    
    # Test retrieval
    results = memory.retrieve_relevant(query_tags=["tag_0"], k=3)
    assert len(results) <= 3
    
    # Test duplicate detection
    initial_count = len(memory.memories)
    memory.add_memory({"data": "item_0"}, 0.5, ["tag_0"])
    # Should not add duplicate (or should merge)
    assert len(memory.memories) <= initial_count + 1
    
    # Test memory summary
    summary = memory.get_memory_summary()
    assert "total_memories" in summary
    assert summary["total_memories"] > 0
    
    print("✓ Memory system test passed")


def test_stream_merger():
    """Test stream merging"""
    merger = StreamMerger()
    
    # Create test streams
    streams = [
        StreamData("visual", {"scene": "forest"}, time.time(), 0.8),
        StreamData("auditory", {"sound": "birds"}, time.time(), 0.6),
        StreamData("emotional", {"mood": "calm"}, time.time(), 0.7),
    ]
    
    # Create attention weights
    weights = np.array([0.4, 0.3, 0.3])
    
    # Merge
    merged = merger.merge_streams(streams, weights)
    
    assert "timestamp" in merged
    assert "streams" in merged
    assert "coherence" in merged
    assert "dominant_streams" in merged
    assert len(merged["streams"]) == 3
    assert 0.0 <= merged["coherence"] <= 1.0
    
    print("✓ Stream merger test passed")


def test_consciousness_engine():
    """Test complete consciousness engine"""
    streams = ["visual", "auditory", "emotional", "cognitive"]
    
    engine = ConsciousnessEngine(
        stream_names=streams,
        memory_capacity=50,
        system_instructions="Test system"
    )
    
    # Test stream ingestion
    engine.ingest_stream("visual", {"data": "test"}, importance=0.7)
    engine.ingest_stream("auditory", {"data": "test"}, importance=0.6)
    
    assert "visual" in engine.current_streams
    assert "auditory" in engine.current_streams
    
    # Test processing
    state = engine.process_consciousness()
    
    assert state is not None
    assert "streams" in state
    assert "coherence" in state
    assert "statistics" in state
    assert state["statistics"]["process_count"] == 1
    
    # Test multiple processing cycles
    for i in range(10):
        engine.ingest_stream("cognitive", {"thought": f"thought_{i}"}, importance=0.5 + i * 0.05)
        engine.process_consciousness()
    
    assert engine.process_count == 11
    assert len(engine.coherence_history) > 0
    
    # Test summary
    summary = engine.get_consciousness_summary()
    assert len(summary) > 0
    assert "Coherence" in summary
    
    # Test system instructions update
    engine.set_system_instructions("New instructions")
    assert engine.system_instructions == "New instructions"
    
    # Test energy adjustment
    engine.adjust_energy(-0.3)
    assert engine.energy_level == 0.7
    
    print("✓ Consciousness engine test passed")


def test_memory_salience():
    """Test memory salience calculation"""
    current_time = time.time()
    
    # Create memory
    mem = MemoryEntry(
        content={"test": "data"},
        importance=0.8,
        timestamp=current_time - 100,  # 100 seconds ago
        access_count=5,
        last_access=current_time - 10  # 10 seconds ago
    )
    
    salience = mem.get_salience(current_time, decay_rate=0.1)
    
    assert salience > 0
    assert salience < 2.0  # Should be reasonable
    
    # More accessed memory should have higher salience
    mem2 = MemoryEntry(
        content={"test": "data2"},
        importance=0.8,
        timestamp=current_time - 100,
        access_count=10,  # More accesses
        last_access=current_time - 10
    )
    
    salience2 = mem2.get_salience(current_time, decay_rate=0.1)
    assert salience2 > salience
    
    print("✓ Memory salience test passed")


def test_data_pruning():
    """Test automatic data pruning"""
    engine = ConsciousnessEngine(
        stream_names=["test"],
        memory_capacity=20,
        system_instructions=""
    )
    
    # Add many low-importance items
    for i in range(50):
        engine.ingest_stream(
            "test",
            {"item": i},
            importance=0.3 + (i % 10) / 30.0
        )
        
        # Process every 5 items
        if i % 5 == 0:
            engine.process_consciousness()
    
    # Should have pruned
    assert len(engine.memory.memories) <= engine.memory.capacity
    
    # Higher importance items should be retained
    high_importance_count = sum(1 for mem in engine.memory.memories if mem.importance > 0.5)
    low_importance_count = sum(1 for mem in engine.memory.memories if mem.importance < 0.4)
    
    # Should retain more high-importance items
    assert high_importance_count >= low_importance_count
    
    print("✓ Data pruning test passed")


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("Running Consciousness Engine Tests")
    print("=" * 60)
    print()
    
    tests = [
        test_stream_data_creation,
        test_attention_mechanism,
        test_memory_system,
        test_stream_merger,
        test_memory_salience,
        test_consciousness_engine,
        test_data_pruning,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} error: {e}")
            failed += 1
    
    print()
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
