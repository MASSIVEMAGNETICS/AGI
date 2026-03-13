"""
Bridge Integration: ConsciousnessEngine + CognitiveRiver8
Demonstrates how to use both systems together for maximum capability
"""

import sys
import time
import numpy as np
from consciousness_engine import ConsciousnessEngine
from typing import Dict, Any


# Mock version of CognitiveRiver8 since we can't import the full GUI version
class CognitiveRiver8Bridge:
    """Simplified bridge to CognitiveRiver8 concept from river.py"""
    
    STREAMS = ["status", "emotion", "memory", "awareness", "systems", "user", "sensory", "realworld"]
    
    def __init__(self):
        self.state: Dict[str, Any] = {k: None for k in self.STREAMS}
        self.priority_logits: Dict[str, float] = {k: 0.0 for k in self.STREAMS}
        self.energy = 0.5
        self.stability = 0.8
        
    def set_status(self, d: Dict[str, Any]):
        self.state["status"] = d
        self.priority_logits["status"] += 0.1
        
    def set_emotion(self, d: Dict[str, Any]):
        self.state["emotion"] = d
        arousal = d.get("arousal", 0.0)
        self.priority_logits["emotion"] += 0.1 + 0.5 * arousal
        
    def set_memory(self, d: Dict[str, Any]):
        self.state["memory"] = d
        salience = d.get("salience", 0.0)
        self.priority_logits["memory"] += 0.05 + 0.6 * salience
        
    def set_awareness(self, d: Dict[str, Any]):
        self.state["awareness"] = d
        self.priority_logits["awareness"] += 0.15
        
    def set_systems(self, d: Dict[str, Any]):
        self.state["systems"] = d
        active = d.get("active_tasks", 0)
        self.priority_logits["systems"] += 0.05 + 0.02 * active
        
    def set_user(self, d: Dict[str, Any]):
        self.state["user"] = d
        self.priority_logits["user"] += 0.25
        
    def set_sensory(self, d: Dict[str, Any]):
        self.state["sensory"] = d
        novelty = d.get("novelty", 0.0)
        self.priority_logits["sensory"] += 0.05 + 0.5 * novelty
        
    def set_realworld(self, d: Dict[str, Any]):
        self.state["realworld"] = d
        urgency = d.get("urgency", 0.0)
        self.priority_logits["realworld"] += 0.05 + 0.5 * urgency


class HybridConsciousnessSystem:
    """
    Hybrid system that combines:
    - CognitiveRiver8: Stream management and priority logic
    - ConsciousnessEngine: Attention, memory, and merging
    """
    
    def __init__(self, memory_capacity: int = 500):
        # Initialize both systems
        self.river = CognitiveRiver8Bridge()
        self.consciousness = ConsciousnessEngine(
            stream_names=CognitiveRiver8Bridge.STREAMS,
            memory_capacity=memory_capacity,
            system_instructions="""
            Integrate cognitive streams with attention and memory.
            Prioritize user input and high-urgency realworld events.
            Maintain emotional coherence and system stability.
            """
        )
        
        self.cycle_count = 0
        
    def update_stream(self, stream_name: str, data: Dict[str, Any], importance: float = 0.5):
        """Update a stream in both systems"""
        
        # Update CognitiveRiver8
        if stream_name == "status":
            self.river.set_status(data)
        elif stream_name == "emotion":
            self.river.set_emotion(data)
        elif stream_name == "memory":
            self.river.set_memory(data)
        elif stream_name == "awareness":
            self.river.set_awareness(data)
        elif stream_name == "systems":
            self.river.set_systems(data)
        elif stream_name == "user":
            self.river.set_user(data)
        elif stream_name == "sensory":
            self.river.set_sensory(data)
        elif stream_name == "realworld":
            self.river.set_realworld(data)
        
        # Update ConsciousnessEngine
        metadata = {
            "tags": [stream_name, "cycle_" + str(self.cycle_count)],
            "river_priority": self.river.priority_logits.get(stream_name, 0.0)
        }
        
        self.consciousness.ingest_stream(
            stream_name=stream_name,
            data=data,
            importance=importance,
            metadata=metadata
        )
    
    def process_unified_consciousness(self) -> Dict[str, Any]:
        """
        Process unified consciousness combining both systems
        """
        self.cycle_count += 1
        
        # Get consciousness engine state
        consciousness_state = self.consciousness.process_consciousness()
        
        # Get river priorities
        river_priorities = dict(self.river.priority_logits)
        
        # Create unified state
        unified_state = {
            "cycle": self.cycle_count,
            "timestamp": time.time(),
            
            # From consciousness engine
            "consciousness": {
                "coherence": consciousness_state["coherence"],
                "dominant_streams": consciousness_state["dominant_streams"],
                "attention_weights": consciousness_state["attention_distribution"],
                "total_importance": consciousness_state["total_importance"],
            },
            
            # From cognitive river
            "river": {
                "energy": self.river.energy,
                "stability": self.river.stability,
                "priorities": river_priorities,
            },
            
            # Memory context
            "memory": consciousness_state["memory_context"],
            
            # Combined streams
            "streams": consciousness_state["streams"],
            
            # Statistics
            "statistics": consciousness_state["statistics"],
        }
        
        # Adjust river energy based on coherence
        coherence = consciousness_state["coherence"]
        if coherence > 0.7:
            self.river.energy = min(1.0, self.river.energy + 0.05)
        elif coherence < 0.3:
            self.river.energy = max(0.0, self.river.energy - 0.05)
        
        return unified_state
    
    def get_summary(self) -> str:
        """Get human-readable summary of unified system"""
        consciousness_summary = self.consciousness.get_consciousness_summary()
        
        summary = f"Hybrid Consciousness System Summary:\n"
        summary += f"{'=' * 60}\n"
        summary += f"Cycle: {self.cycle_count}\n"
        summary += f"River Energy: {self.river.energy:.2f}\n"
        summary += f"River Stability: {self.river.stability:.2f}\n\n"
        summary += consciousness_summary
        
        return summary


def demonstrate_hybrid_system():
    """Demonstrate the hybrid consciousness system"""
    
    print("=" * 70)
    print("HYBRID CONSCIOUSNESS SYSTEM DEMONSTRATION")
    print("CognitiveRiver8 + ConsciousnessEngine")
    print("=" * 70)
    
    # Initialize hybrid system
    system = HybridConsciousnessSystem(memory_capacity=200)
    
    print(f"\nInitialized hybrid system")
    print(f"Streams: {CognitiveRiver8Bridge.STREAMS}")
    print()
    
    # Scenario 1: System startup
    print("\n" + "=" * 70)
    print("SCENARIO 1: System Startup")
    print("=" * 70)
    
    system.update_stream("systems", {
        "status": "initializing",
        "active_tasks": 5,
        "cpu_usage": 0.3
    }, importance=0.7)
    
    system.update_stream("status", {
        "state": "booting",
        "readiness": 0.4
    }, importance=0.6)
    
    system.update_stream("awareness", {
        "clarity": 0.5,
        "focus": "initialization"
    }, importance=0.5)
    
    state = system.process_unified_consciousness()
    print(system.get_summary())
    
    # Scenario 2: User interaction
    print("\n" + "=" * 70)
    print("SCENARIO 2: User Interaction")
    print("=" * 70)
    
    system.update_stream("user", {
        "input": "What is your current state?",
        "intent": "query",
        "priority": "high"
    }, importance=0.9)
    
    system.update_stream("emotion", {
        "state": "attentive",
        "valence": 0.7,
        "arousal": 0.6
    }, importance=0.7)
    
    system.update_stream("awareness", {
        "clarity": 0.8,
        "focus": "user_interaction"
    }, importance=0.8)
    
    state = system.process_unified_consciousness()
    print(system.get_summary())
    print(f"\nTop 3 Streams by Attention:")
    for idx, weight in system.consciousness.attention.get_top_k_streams(3):
        print(f"  {CognitiveRiver8Bridge.STREAMS[idx]:15s}: {weight:.3f}")
    
    # Scenario 3: Complex sensory input
    print("\n" + "=" * 70)
    print("SCENARIO 3: Complex Sensory Input")
    print("=" * 70)
    
    system.update_stream("sensory", {
        "modality": "visual",
        "data": "complex_scene_data",
        "novelty": 0.8
    }, importance=0.8)
    
    system.update_stream("sensory", {
        "modality": "auditory",
        "data": "ambient_sounds",
        "novelty": 0.4
    }, importance=0.5)
    
    system.update_stream("emotion", {
        "state": "curious",
        "valence": 0.6,
        "arousal": 0.7
    }, importance=0.6)
    
    system.update_stream("memory", {
        "recall": "similar_scene_from_past",
        "salience": 0.7,
        "confidence": 0.6
    }, importance=0.7)
    
    state = system.process_unified_consciousness()
    print(system.get_summary())
    
    # Scenario 4: Urgent realworld event
    print("\n" + "=" * 70)
    print("SCENARIO 4: Urgent Realworld Event")
    print("=" * 70)
    
    system.update_stream("realworld", {
        "event": "system_alert",
        "urgency": 0.95,
        "source": "security_monitor"
    }, importance=1.0)
    
    system.update_stream("emotion", {
        "state": "alert",
        "valence": 0.3,
        "arousal": 0.95
    }, importance=0.9)
    
    system.update_stream("systems", {
        "status": "checking",
        "active_tasks": 12,
        "cpu_usage": 0.8
    }, importance=0.8)
    
    state = system.process_unified_consciousness()
    print(system.get_summary())
    print(f"\nCoherence: {state['consciousness']['coherence']:.3f}")
    print(f"Dominant Streams: {', '.join(state['consciousness']['dominant_streams'])}")
    
    # Scenario 5: Resolution and reflection
    print("\n" + "=" * 70)
    print("SCENARIO 5: Resolution and Reflection")
    print("=" * 70)
    
    system.update_stream("realworld", {
        "event": "alert_resolved",
        "urgency": 0.2,
        "outcome": "false_positive"
    }, importance=0.5)
    
    system.update_stream("emotion", {
        "state": "relieved",
        "valence": 0.7,
        "arousal": 0.4
    }, importance=0.6)
    
    system.update_stream("memory", {
        "action": "storing_experience",
        "salience": 0.8,
        "lesson": "false_alarm_pattern"
    }, importance=0.8)
    
    system.update_stream("awareness", {
        "clarity": 0.9,
        "focus": "learning",
        "reflection": "analyzing_response"
    }, importance=0.7)
    
    state = system.process_unified_consciousness()
    print(system.get_summary())
    
    # Final statistics
    print("\n" + "=" * 70)
    print("FINAL STATISTICS")
    print("=" * 70)
    
    print(f"\nTotal Cycles: {system.cycle_count}")
    print(f"Total Memories: {len(system.consciousness.memory.memories)}")
    print(f"Average Coherence: {np.mean(list(system.consciousness.coherence_history)):.3f}")
    print(f"Final Energy: {system.river.energy:.3f}")
    print(f"Final Stability: {system.river.stability:.3f}")
    
    # Show memory context
    mem_summary = system.consciousness.memory.get_memory_summary()
    print(f"\nMemory System:")
    print(f"  Total: {mem_summary['total_memories']}")
    print(f"  Avg Salience: {mem_summary['avg_salience']:.3f}")
    
    print("\n" + "=" * 70)
    print("DEMONSTRATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    demonstrate_hybrid_system()
