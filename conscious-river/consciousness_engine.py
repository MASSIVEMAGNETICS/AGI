"""
Consciousness Engine - Complete Implementation
Integrates multiple sensory streams with attention, memory, pruning, and merging
"""

import numpy as np
import time
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from collections import deque
import hashlib


@dataclass
class StreamData:
    """Data from a single sensory/cognitive stream"""
    stream_name: str
    data: Any
    timestamp: float
    importance: float = 0.5
    novelty: float = 0.5
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_hash(self) -> str:
        """
        Generate content hash for deduplication
        Using SHA-256 for better collision resistance
        """
        content_str = json.dumps(self.data, sort_keys=True)
        return hashlib.sha256(content_str.encode()).hexdigest()


@dataclass
class MemoryEntry:
    """Memory entry with importance and decay"""
    content: Any
    importance: float
    timestamp: float
    access_count: int = 0
    last_access: float = 0.0
    tags: List[str] = field(default_factory=list)
    
    # Salience calculation parameters
    DECAY_WEIGHT = 1.0
    ACCESS_WEIGHT = 0.3
    RECENCY_WEIGHT = 0.2
    ACCESS_BOOST_FACTOR = 0.1
    
    def get_salience(self, current_time: float, decay_rate: float = 0.1) -> float:
        """Calculate current salience based on importance, recency, and access"""
        time_decay = np.exp(-decay_rate * (current_time - self.timestamp))
        access_boost = min(1.0, self.access_count * self.ACCESS_BOOST_FACTOR)
        
        # Only apply recency boost if memory has been accessed
        if self.last_access > 0:
            recency_boost = np.exp(-decay_rate * (current_time - self.last_access))
        else:
            recency_boost = 0.0
        
        return (self.importance * time_decay * self.DECAY_WEIGHT + 
                access_boost * self.ACCESS_WEIGHT + 
                recency_boost * self.RECENCY_WEIGHT)


class AttentionMechanism:
    """Attention mechanism for prioritizing streams"""
    
    # Configuration parameters
    DEFAULT_TEMPERATURE = 1.0
    CONTEXT_BOOST_WEIGHT = 0.3
    EMA_ALPHA = 0.3  # Smoothing factor for attention transitions
    
    def __init__(self, num_streams: int, attention_window: int = 10):
        self.num_streams = num_streams
        self.attention_weights = np.ones(num_streams) / num_streams
        self.history = deque(maxlen=attention_window)
        self.stream_names = []
        
    def update_attention(self, stream_importances: np.ndarray, 
                        context: Optional[Dict[str, float]] = None) -> np.ndarray:
        """
        Update attention weights based on stream importances and context
        Uses softmax with temperature for smooth transitions
        """
        # Temperature parameter for attention sharpness
        temperature = self.DEFAULT_TEMPERATURE
        
        # Add context modulation if provided
        if context:
            context_boost = np.array([context.get(name, 0.0) for name in self.stream_names])
            stream_importances = stream_importances + context_boost * self.CONTEXT_BOOST_WEIGHT
        
        # Apply softmax with temperature
        exp_importances = np.exp(stream_importances / temperature)
        attention_weights = exp_importances / np.sum(exp_importances)
        
        # Smooth transition using exponential moving average
        alpha = self.EMA_ALPHA
        self.attention_weights = (1 - alpha) * self.attention_weights + alpha * attention_weights
        
        # Store in history
        self.history.append(self.attention_weights.copy())
        
        return self.attention_weights
    
    def get_top_k_streams(self, k: int = 3) -> List[Tuple[int, float]]:
        """Get indices and weights of top-k attended streams"""
        indices = np.argsort(self.attention_weights)[-k:][::-1]
        return [(int(idx), float(self.attention_weights[idx])) for idx in indices]


class MemorySystem:
    """Memory system with importance weighting and pruning"""
    
    # Scoring weights for retrieval
    TAG_OVERLAP_WEIGHT = 0.6
    SALIENCE_WEIGHT = 0.4
    MIN_QUERY_TAGS = 1  # Minimum to prevent division by zero
    
    def __init__(self, capacity: int = 1000, prune_threshold: float = 0.1):
        self.capacity = capacity
        self.prune_threshold = prune_threshold
        self.memories: List[MemoryEntry] = []
        self.content_hashes = {}  # Maps hash -> memory for O(1) duplicate detection
        self.decay_rate = 0.1
    
    def _compute_content_hash(self, content: Any) -> str:
        """Helper method to compute SHA-256 hash of content"""
        content_str = json.dumps(content, sort_keys=True)
        return hashlib.sha256(content_str.encode()).hexdigest()
        
    def add_memory(self, content: Any, importance: float, tags: List[str] = None):
        """Add new memory with importance score"""
        # Check for duplicates using SHA-256 content hash with O(1) lookup
        content_hash = self._compute_content_hash(content)
        if content_hash in self.content_hashes:
            # Update existing memory directly via hash map
            mem = self.content_hashes[content_hash]
            mem.importance = max(mem.importance, importance)
            mem.access_count += 1
            mem.last_access = time.time()
            return
        
        # Add new memory
        memory = MemoryEntry(
            content=content,
            importance=importance,
            timestamp=time.time(),
            tags=tags or []
        )
        self.memories.append(memory)
        self.content_hashes[content_hash] = memory  # Store reference for O(1) lookup
        
        # Prune if over capacity
        if len(self.memories) > self.capacity:
            self.prune_memories()
    
    def prune_memories(self):
        """Remove low-salience memories to free space"""
        current_time = time.time()
        
        # Calculate salience for all memories
        saliences = [mem.get_salience(current_time, self.decay_rate) 
                    for mem in self.memories]
        
        # Keep memories above threshold
        kept_memories = []
        
        for mem, salience in zip(self.memories, saliences):
            if salience >= self.prune_threshold or len(kept_memories) < self.capacity // 2:
                kept_memories.append(mem)
        
        # Sort by salience and keep top entries
        kept_memories.sort(key=lambda m: m.get_salience(current_time, self.decay_rate), reverse=True)
        self.memories = kept_memories[:self.capacity]
        
        # Rebuild hash map to stay consistent with kept memories
        self.content_hashes = {}
        for mem in self.memories:
            mem_hash = self._compute_content_hash(mem.content)
            self.content_hashes[mem_hash] = mem
    
    def retrieve_relevant(self, query_tags: List[str], k: int = 5) -> List[MemoryEntry]:
        """Retrieve k most relevant memories based on tags and salience"""
        current_time = time.time()
        query_tags_set = set(query_tags)  # Convert once for efficiency
        
        # Score memories by tag overlap and salience
        scores = []
        for mem in self.memories:
            tag_overlap = len(set(mem.tags) & query_tags_set) / max(len(query_tags), self.MIN_QUERY_TAGS)
            salience = mem.get_salience(current_time, self.decay_rate)
            score = tag_overlap * self.TAG_OVERLAP_WEIGHT + salience * self.SALIENCE_WEIGHT
            scores.append((mem, score))
            
            # Update access stats
            if tag_overlap > 0:
                mem.access_count += 1
                mem.last_access = current_time
        
        # Return top k
        scores.sort(key=lambda x: x[1], reverse=True)
        return [mem for mem, _ in scores[:k]]
    
    def get_memory_summary(self) -> Dict[str, Any]:
        """Get summary statistics of memory system"""
        current_time = time.time()
        saliences = [mem.get_salience(current_time, self.decay_rate) for mem in self.memories]
        
        return {
            "total_memories": len(self.memories),
            "capacity": self.capacity,
            "avg_salience": np.mean(saliences) if saliences else 0.0,
            "max_salience": np.max(saliences) if saliences else 0.0,
            "min_salience": np.min(saliences) if saliences else 0.0
        }


class StreamMerger:
    """Merges multiple streams into unified consciousness state"""
    
    def __init__(self):
        self.merge_history = deque(maxlen=100)
        
    def merge_streams(self, stream_data: List[StreamData], 
                     attention_weights: np.ndarray,
                     memory_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Merge multiple streams using attention weights
        Returns unified consciousness state
        """
        # Weight streams by attention
        weighted_streams = {}
        total_importance = 0.0
        
        for i, stream in enumerate(stream_data):
            weight = attention_weights[i] if i < len(attention_weights) else 0.0
            weighted_importance = stream.importance * weight
            
            weighted_streams[stream.stream_name] = {
                "data": stream.data,
                "weight": float(weight),
                "importance": float(weighted_importance),
                "timestamp": stream.timestamp,
                "metadata": stream.metadata
            }
            total_importance += weighted_importance
        
        # Create merged state
        merged_state = {
            "timestamp": time.time(),
            "streams": weighted_streams,
            "total_importance": float(total_importance),
            "attention_distribution": attention_weights.tolist(),
            "dominant_streams": self._get_dominant_streams(weighted_streams),
            "memory_context": memory_context or {},
            "coherence": self._calculate_coherence(stream_data, attention_weights)
        }
        
        self.merge_history.append(merged_state)
        return merged_state
    
    def _get_dominant_streams(self, weighted_streams: Dict[str, Any], top_k: int = 3) -> List[str]:
        """Get names of dominant streams"""
        sorted_streams = sorted(weighted_streams.items(), 
                              key=lambda x: x[1]["importance"], 
                              reverse=True)
        return [name for name, _ in sorted_streams[:top_k]]
    
    def _calculate_coherence(self, streams: List[StreamData], weights: np.ndarray) -> float:
        """Calculate coherence of merged consciousness state"""
        if len(streams) < 2:
            return 1.0
        
        # Coherence based on attention focus (higher when attention is concentrated)
        # Use Gini coefficient: higher values = more concentrated = higher coherence
        weights_sorted = np.sort(weights)[::-1]
        n = len(weights_sorted)
        
        # Calculate concentration of attention
        cumsum = np.cumsum(weights_sorted)
        top_3_concentration = cumsum[min(2, n-1)] if n > 0 else 0.0
        
        # Normalize to 0-1 range (perfect focus = 1.0, uniform = low)
        coherence = top_3_concentration
        
        return float(np.clip(coherence, 0.0, 1.0))


class ConsciousnessEngine:
    """
    Complete Consciousness Engine
    Integrates multiple sensory inputs, attention, memory, pruning, and merging
    """
    
    # Configuration parameters
    IMPORTANT_MEMORY_THRESHOLD = 0.6  # Threshold for storing in memory
    PRUNING_INTERVAL = 10  # Process cycles between pruning operations
    
    def __init__(self, stream_names: List[str], 
                 memory_capacity: int = 1000,
                 system_instructions: str = ""):
        self.stream_names = stream_names
        self.num_streams = len(stream_names)
        self.system_instructions = system_instructions
        
        # Core components
        self.attention = AttentionMechanism(self.num_streams)
        self.attention.stream_names = stream_names
        self.memory = MemorySystem(capacity=memory_capacity)
        self.merger = StreamMerger()
        
        # Current state
        self.current_streams: Dict[str, StreamData] = {}
        self.consciousness_state: Optional[Dict[str, Any]] = None
        self.energy_level = 1.0
        self.coherence_history = deque(maxlen=100)
        
        # Statistics
        self.process_count = 0
        self.prune_count = 0
        
    def ingest_stream(self, stream_name: str, data: Any, 
                     importance: float = 0.5, 
                     metadata: Dict[str, Any] = None):
        """Ingest data from a sensory/cognitive stream"""
        if stream_name not in self.stream_names:
            raise ValueError(f"Unknown stream: {stream_name}")
        
        stream_data = StreamData(
            stream_name=stream_name,
            data=data,
            timestamp=time.time(),
            importance=importance,
            metadata=metadata or {}
        )
        
        self.current_streams[stream_name] = stream_data
        
        # Add to memory if important enough
        if importance > self.IMPORTANT_MEMORY_THRESHOLD:
            tags = [stream_name] + metadata.get("tags", []) if metadata else [stream_name]
            self.memory.add_memory(data, importance, tags)
    
    def process_consciousness(self) -> Dict[str, Any]:
        """
        Main consciousness processing loop:
        1. Calculate stream importances
        2. Update attention weights
        3. Retrieve relevant memories
        4. Merge streams with attention
        5. Prune insignificant data
        6. Return unified consciousness state
        """
        self.process_count += 1
        
        # Step 1: Get all active streams as list
        stream_list = []
        stream_importances = np.zeros(self.num_streams)
        
        for i, stream_name in enumerate(self.stream_names):
            if stream_name in self.current_streams:
                stream = self.current_streams[stream_name]
                stream_list.append(stream)
                stream_importances[i] = stream.importance
        
        # Step 2: Update attention based on importances
        attention_weights = self.attention.update_attention(stream_importances)
        
        # Step 3: Retrieve relevant memories
        # Use dominant streams for memory retrieval
        top_streams = self.attention.get_top_k_streams(k=3)
        query_tags = [self.stream_names[idx] for idx, _ in top_streams]
        relevant_memories = self.memory.retrieve_relevant(query_tags, k=5)
        
        memory_context = {
            "relevant_memories": [mem.content for mem in relevant_memories],
            "memory_summary": self.memory.get_memory_summary()
        }
        
        # Step 4: Merge streams
        merged_state = self.merger.merge_streams(stream_list, attention_weights, memory_context)
        
        # Step 5: Prune old/irrelevant data from memory periodically
        if self.process_count % self.PRUNING_INTERVAL == 0:
            old_count = len(self.memory.memories)
            self.memory.prune_memories()
            new_count = len(self.memory.memories)
            if old_count > new_count:
                self.prune_count += 1
        
        # Step 6: Update consciousness state
        self.consciousness_state = {
            **merged_state,
            "system_instructions": self.system_instructions,
            "energy_level": self.energy_level,
            "statistics": {
                "process_count": self.process_count,
                "prune_count": self.prune_count,
                "active_streams": len(stream_list),
                "total_memories": len(self.memory.memories)
            }
        }
        
        # Track coherence
        self.coherence_history.append(merged_state["coherence"])
        
        return self.consciousness_state
    
    def get_consciousness_summary(self) -> str:
        """Get human-readable summary of consciousness state"""
        if not self.consciousness_state:
            return "No consciousness state available"
        
        state = self.consciousness_state
        dominant = state.get("dominant_streams", [])
        coherence = state.get("coherence", 0.0)
        
        summary = f"Consciousness State Summary:\n"
        summary += f"  Coherence: {coherence:.2f}\n"
        summary += f"  Energy: {self.energy_level:.2f}\n"
        summary += f"  Dominant Streams: {', '.join(dominant)}\n"
        summary += f"  Active Memories: {state['statistics']['total_memories']}\n"
        summary += f"  Processing Cycles: {state['statistics']['process_count']}\n"
        
        return summary
    
    def set_system_instructions(self, instructions: str):
        """Update system instructions"""
        self.system_instructions = instructions
    
    def adjust_energy(self, delta: float):
        """Adjust consciousness energy level"""
        self.energy_level = max(0.0, min(1.0, self.energy_level + delta))


# Example usage and demonstration
def demo_consciousness_engine():
    """Demonstrate the consciousness engine"""
    
    # Define streams
    streams = ["visual", "auditory", "emotional", "cognitive", "memory_recall", 
               "body_state", "environment", "intent"]
    
    # Create engine with system instructions
    engine = ConsciousnessEngine(
        stream_names=streams,
        memory_capacity=500,
        system_instructions="Integrate sensory data to form coherent understanding"
    )
    
    print("=" * 60)
    print("Consciousness Engine Demo")
    print("=" * 60)
    
    # Simulate sensory inputs over time
    scenarios = [
        {
            "visual": {"objects": ["tree", "bird"], "brightness": 0.8},
            "auditory": {"sounds": ["chirping", "wind"], "volume": 0.5},
            "emotional": {"mood": "calm", "valence": 0.7},
            "cognitive": {"thought": "observing nature"},
            "body_state": {"energy": 0.8, "comfort": 0.9},
        },
        {
            "visual": {"objects": ["person approaching"], "brightness": 0.7},
            "auditory": {"sounds": ["footsteps"], "volume": 0.6},
            "emotional": {"mood": "curious", "valence": 0.5},
            "cognitive": {"thought": "who is this?"},
            "intent": {"action": "observe and greet"},
        },
        {
            "visual": {"objects": ["smiling face"], "brightness": 0.7},
            "auditory": {"sounds": ["friendly voice"], "volume": 0.7},
            "emotional": {"mood": "happy", "valence": 0.9},
            "cognitive": {"thought": "this is pleasant"},
            "memory_recall": {"memory": "similar pleasant encounter yesterday"},
        },
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n--- Scenario {i} ---")
        
        # Ingest streams
        for stream_name, data in scenario.items():
            importance = 0.5 + np.random.rand() * 0.4  # Random importance 0.5-0.9
            engine.ingest_stream(stream_name, data, importance=importance)
        
        # Process consciousness
        state = engine.process_consciousness()
        
        # Display summary
        print(engine.get_consciousness_summary())
        print(f"\nTop Attended Streams:")
        for idx, weight in engine.attention.get_top_k_streams(3):
            print(f"  {streams[idx]}: {weight:.3f}")
    
    print("\n" + "=" * 60)
    print("Final Statistics:")
    print(f"  Total processing cycles: {engine.process_count}")
    print(f"  Total prune operations: {engine.prune_count}")
    print(f"  Current memories: {len(engine.memory.memories)}")
    print(f"  Average coherence: {np.mean(list(engine.coherence_history)):.3f}")
    print("=" * 60)
    
    return engine


if __name__ == "__main__":
    demo_consciousness_engine()
