"""
Integration Example: Consciousness Engine + Cognitive River
Demonstrates how to use the consciousness engine with the existing river.py components
"""

import sys
import time
import numpy as np
from consciousness_engine import ConsciousnessEngine, StreamData
import json


def simulate_cognitive_agent():
    """
    Simulate a cognitive agent with multiple sensory inputs
    Demonstrates the full consciousness pipeline
    """
    
    # Display configuration
    MEMORY_DISPLAY_LENGTH = 100  # Characters to show from memory content
    
    print("=" * 70)
    print("CONSCIOUSNESS ENGINE - COGNITIVE AGENT SIMULATION")
    print("=" * 70)
    
    # Define sensory and cognitive streams
    stream_names = [
        "visual",           # Visual perception
        "auditory",         # Sound perception
        "tactile",          # Touch/physical sensation
        "emotional",        # Emotional state
        "cognitive",        # Thoughts and reasoning
        "memory_recall",    # Recalled memories
        "intent",           # Goals and intentions
        "system_status"     # Internal system state
    ]
    
    # Initialize consciousness engine
    system_instructions = """
    You are a conscious agent integrating multiple sensory streams.
    Prioritize based on:
    1. Importance of incoming data
    2. Relevance to current goals
    3. Emotional significance
    4. Novelty and learning opportunities
    """
    
    engine = ConsciousnessEngine(
        stream_names=stream_names,
        memory_capacity=100,
        system_instructions=system_instructions
    )
    
    print(f"\nInitialized with {len(stream_names)} streams")
    print(f"Memory capacity: {engine.memory.capacity}")
    print(f"System instructions: {system_instructions.strip()}\n")
    
    # Simulation scenarios
    scenarios = [
        {
            "name": "Morning Wake-up",
            "streams": {
                "visual": {"scene": "bedroom", "light_level": 0.3, "objects": ["bed", "window"]},
                "auditory": {"sounds": ["alarm_clock"], "volume": 0.8},
                "tactile": {"sensation": "comfortable", "temperature": 0.7},
                "emotional": {"state": "sleepy", "valence": 0.4, "arousal": 0.2},
                "cognitive": {"thought": "need to wake up"},
                "system_status": {"energy": 0.3, "alertness": 0.2},
            },
            "importances": {"auditory": 0.9, "emotional": 0.6, "system_status": 0.7}
        },
        {
            "name": "Getting Ready",
            "streams": {
                "visual": {"scene": "bathroom", "light_level": 0.9, "objects": ["mirror", "sink"]},
                "auditory": {"sounds": ["water_running"], "volume": 0.5},
                "tactile": {"sensation": "cold_water", "temperature": 0.3},
                "emotional": {"state": "alert", "valence": 0.6, "arousal": 0.6},
                "cognitive": {"thought": "planning the day"},
                "intent": {"goal": "get ready for work", "priority": 0.8},
                "memory_recall": {"memory": "yesterday's tasks"},
                "system_status": {"energy": 0.6, "alertness": 0.7},
            },
            "importances": {"intent": 0.9, "cognitive": 0.8, "memory_recall": 0.7}
        },
        {
            "name": "Unexpected Event",
            "streams": {
                "visual": {"scene": "living_room", "light_level": 0.8, "objects": ["broken_vase"]},
                "auditory": {"sounds": ["crash"], "volume": 0.9},
                "emotional": {"state": "surprised", "valence": 0.3, "arousal": 0.9},
                "cognitive": {"thought": "what happened?"},
                "intent": {"goal": "investigate", "priority": 1.0},
                "system_status": {"energy": 0.6, "alertness": 0.95},
            },
            "importances": {"visual": 0.95, "auditory": 0.9, "emotional": 0.85, "intent": 1.0}
        },
        {
            "name": "Problem Solving",
            "streams": {
                "visual": {"scene": "living_room", "light_level": 0.8, "objects": ["broken_vase", "broom"]},
                "cognitive": {"thought": "need to clean this up"},
                "emotional": {"state": "calm", "valence": 0.6, "arousal": 0.5},
                "intent": {"goal": "clean up", "priority": 0.8},
                "memory_recall": {"memory": "where cleaning supplies are kept"},
                "system_status": {"energy": 0.7, "alertness": 0.8},
            },
            "importances": {"cognitive": 0.9, "intent": 0.85, "memory_recall": 0.8}
        },
        {
            "name": "Reflection",
            "streams": {
                "visual": {"scene": "clean_living_room", "light_level": 0.7, "objects": ["sofa"]},
                "emotional": {"state": "satisfied", "valence": 0.8, "arousal": 0.4},
                "cognitive": {"thought": "handled that well"},
                "memory_recall": {"memory": "successful problem resolution"},
                "intent": {"goal": "relax briefly", "priority": 0.5},
                "system_status": {"energy": 0.65, "alertness": 0.6},
            },
            "importances": {"emotional": 0.7, "cognitive": 0.75, "memory_recall": 0.8}
        }
    ]
    
    # Run simulation
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{'=' * 70}")
        print(f"SCENARIO {i}: {scenario['name']}")
        print(f"{'=' * 70}")
        
        # Ingest all streams for this scenario
        for stream_name, data in scenario["streams"].items():
            importance = scenario["importances"].get(stream_name, 0.5)
            metadata = {"scenario": scenario["name"], "tags": [scenario["name"], stream_name]}
            
            engine.ingest_stream(
                stream_name=stream_name,
                data=data,
                importance=importance,
                metadata=metadata
            )
        
        # Process consciousness
        state = engine.process_consciousness()
        
        # Display results
        print(f"\n{engine.get_consciousness_summary()}")
        
        print(f"\nTop 3 Attended Streams:")
        for idx, weight in engine.attention.get_top_k_streams(3):
            stream_name = stream_names[idx]
            print(f"  {stream_name:15s}: {weight:.3f}")
        
        print(f"\nDominant Streams: {', '.join(state['dominant_streams'])}")
        print(f"Coherence: {state['coherence']:.3f}")
        
        # Show relevant memories
        if state.get('memory_context', {}).get('relevant_memories'):
            print(f"\nRelevant Memories Retrieved: {len(state['memory_context']['relevant_memories'])}")
            for j, mem in enumerate(state['memory_context']['relevant_memories'][:3], 1):
                mem_str = json.dumps(mem, indent=2)[:MEMORY_DISPLAY_LENGTH] + "..."
                print(f"  {j}. {mem_str}")
        
        # Simulate processing time
        time.sleep(0.2)
    
    # Final summary
    print(f"\n{'=' * 70}")
    print("FINAL SUMMARY")
    print(f"{'=' * 70}")
    print(f"\nTotal Processing Cycles: {engine.process_count}")
    print(f"Total Prune Operations: {engine.prune_count}")
    print(f"Total Memories Stored: {len(engine.memory.memories)}")
    print(f"Average Coherence: {np.mean(list(engine.coherence_history)):.3f}")
    
    # Memory summary
    mem_summary = engine.memory.get_memory_summary()
    print(f"\nMemory System:")
    print(f"  Total Memories: {mem_summary['total_memories']}")
    print(f"  Capacity: {mem_summary['capacity']}")
    print(f"  Average Salience: {mem_summary['avg_salience']:.3f}")
    print(f"  Max Salience: {mem_summary['max_salience']:.3f}")
    print(f"  Min Salience: {mem_summary['min_salience']:.3f}")
    
    # Demonstrate memory retrieval
    print(f"\n{'=' * 70}")
    print("MEMORY RETRIEVAL TEST")
    print(f"{'=' * 70}")
    
    # Retrieve memories related to problem-solving
    problem_memories = engine.memory.retrieve_relevant(
        query_tags=["Problem Solving", "cognitive", "intent"], 
        k=3
    )
    
    print(f"\nRetrieving memories tagged with 'Problem Solving':")
    for i, mem in enumerate(problem_memories, 1):
        print(f"\n{i}. Importance: {mem.importance:.3f}")
        print(f"   Timestamp: {time.ctime(mem.timestamp)}")
        print(f"   Access Count: {mem.access_count}")
        print(f"   Tags: {mem.tags}")
        print(f"   Content: {json.dumps(mem.content, indent=4)[:MEMORY_DISPLAY_LENGTH]}...")
    
    print(f"\n{'=' * 70}")
    print("SIMULATION COMPLETE")
    print(f"{'=' * 70}\n")
    
    return engine


def demonstrate_data_pruning():
    """Demonstrate the data pruning mechanism"""
    
    print("\n" + "=" * 70)
    print("DATA PRUNING DEMONSTRATION")
    print("=" * 70)
    
    # Create engine with small capacity to trigger pruning
    engine = ConsciousnessEngine(
        stream_names=["test_stream"],
        memory_capacity=20,  # Small capacity
        system_instructions="Test pruning"
    )
    
    print(f"\nMemory capacity: {engine.memory.capacity}")
    print(f"Prune threshold: {engine.memory.prune_threshold}")
    
    # Add many memories with varying importance
    print("\nAdding 50 memories with varying importance...")
    for i in range(50):
        importance = 0.3 + (i % 10) / 20.0  # Varying importance
        data = {"test_data": f"item_{i}", "value": i}
        
        engine.ingest_stream(
            stream_name="test_stream",
            data=data,
            importance=importance,
            metadata={"tags": [f"category_{i % 5}"]}
        )
        
        # Process every 10 items to trigger pruning
        if i % 10 == 0:
            engine.process_consciousness()
    
    # Final process to see pruning effect
    for _ in range(3):
        engine.process_consciousness()
    
    print(f"\nAfter processing:")
    print(f"  Memories retained: {len(engine.memory.memories)}/{50}")
    print(f"  Prune operations: {engine.prune_count}")
    
    # Show retained memories
    print(f"\nSample of retained memories (sorted by salience):")
    current_time = time.time()
    memories_with_salience = [
        (mem, mem.get_salience(current_time, engine.memory.decay_rate))
        for mem in engine.memory.memories
    ]
    memories_with_salience.sort(key=lambda x: x[1], reverse=True)
    
    for i, (mem, salience) in enumerate(memories_with_salience[:5], 1):
        print(f"\n{i}. Salience: {salience:.3f}, Importance: {mem.importance:.3f}")
        print(f"   Content: {mem.content}")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    # Run main simulation
    engine = simulate_cognitive_agent()
    
    # Demonstrate pruning
    demonstrate_data_pruning()
    
    print("\n✓ All demonstrations completed successfully!")
