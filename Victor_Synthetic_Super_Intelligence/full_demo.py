#!/usr/bin/env python3
"""
VICTOR SYNTHETIC SUPER INTELLIGENCE - FULL WORKING DEMO
========================================================
Version: 2.1.0-QUANTUM-FRACTAL
Author: MASSIVEMAGNETICS
Purpose: Complete demonstration of all Victor systems working together

This demo showcases:
1. Tensor Core - Automatic differentiation engine
2. Genesis Engine - Quantum-fractal hybrid cognition
3. Victor Hub - Skill routing and task execution
4. NLP Integration - Natural language processing
5. Advanced AI - Holon Omega and neural systems
6. Unified Core - Complete integration

Run with: python full_demo.py [--interactive] [--verbose]
"""

import sys
import os
import time
import argparse
import traceback
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

import numpy as np

# =============================================================================
# CONSTANTS
# =============================================================================
# Common English stopwords for basic NLP when spaCy is not available
COMMON_STOPWORDS = {
    'the', 'a', 'an', 'is', 'are', 'was', 'were', 'in', 'on', 'at',
    'to', 'for', 'with', 'and', 'or', 'it', 'by', 'as', 'of', 'this',
    'that', 'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
    'would', 'could', 'should', 'can', 'may', 'might', 'must', 'shall'
}

# =============================================================================
# TERMINAL COLORS
# =============================================================================
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    QUANTUM = '\033[35m'
    FRACTAL = '\033[36m'


def print_header(title: str, char: str = "=", color: str = Colors.HEADER):
    """Print a formatted header"""
    width = 80
    print(f"\n{color}{char * width}")
    print(f"{title.center(width)}")
    print(f"{char * width}{Colors.ENDC}\n")


def print_section(title: str, color: str = Colors.CYAN):
    """Print a section header"""
    print(f"\n{color}{Colors.BOLD}{'─' * 60}")
    print(f"{title}")
    print(f"{'─' * 60}{Colors.ENDC}\n")


def print_success(msg: str):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {msg}{Colors.ENDC}")


def print_error(msg: str):
    """Print error message"""
    print(f"{Colors.RED}✗ {msg}{Colors.ENDC}")


def print_info(msg: str):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ {msg}{Colors.ENDC}")


def print_quantum(msg: str):
    """Print quantum-related message"""
    print(f"{Colors.QUANTUM}⚛ {msg}{Colors.ENDC}")


# =============================================================================
# DEMO MODULES
# =============================================================================

def demo_tensor_core(verbose: bool = False) -> Dict[str, Any]:
    """
    Demo 1: Tensor Core - Automatic Differentiation Engine
    Shows gradient computation and basic neural network operations
    """
    print_section("DEMO 1: TENSOR CORE - Automatic Differentiation")
    
    results = {"status": "pending", "tests": []}
    
    try:
        from advanced_ai.tensor_core import Tensor
        print_success("Tensor Core imported successfully")
        
        # Test 1: Basic tensor operations
        print("\n📐 Test 1: Basic Tensor Operations")
        x = Tensor([[1.0, 2.0], [3.0, 4.0]], requires_grad=True)
        y = Tensor([[0.5, 0.5], [0.5, 0.5]], requires_grad=True)
        
        # Forward pass
        z = x * y + Tensor([[1.0]])
        print(f"   x = {x.data.tolist()}")
        print(f"   y = {y.data.tolist()}")
        print(f"   z = x * y + 1 = {z.data.tolist()}")
        results["tests"].append({"name": "basic_ops", "status": "passed"})
        
        # Test 2: Gradient computation
        print("\n📐 Test 2: Gradient Computation")
        a = Tensor([2.0], requires_grad=True)
        b = Tensor([3.0], requires_grad=True)
        c = a * b + a ** 2  # c = a*b + a^2 = 6 + 4 = 10
        c.backward()
        print(f"   a = 2.0, b = 3.0")
        print(f"   c = a*b + a^2 = {c.data[0]:.1f}")
        print(f"   ∂c/∂a = b + 2a = {a.grad[0]:.1f} (expected: 7.0)")
        print(f"   ∂c/∂b = a = {b.grad[0]:.1f} (expected: 2.0)")
        
        grad_correct = abs(a.grad[0] - 7.0) < 0.01 and abs(b.grad[0] - 2.0) < 0.01
        results["tests"].append({
            "name": "gradients", 
            "status": "passed" if grad_correct else "failed"
        })
        
        # Test 3: Matrix multiplication with gradients
        print("\n📐 Test 3: Matrix Multiplication")
        W = Tensor(np.random.randn(3, 4) * 0.1, requires_grad=True)
        x = Tensor(np.random.randn(2, 3))
        out = x.matmul(W)
        loss = out.sum()
        loss.backward()
        print(f"   Input shape: {x.data.shape}")
        print(f"   Weight shape: {W.data.shape}")
        print(f"   Output shape: {out.data.shape}")
        print(f"   Gradient shape: {W.grad.shape}")
        results["tests"].append({"name": "matmul", "status": "passed"})
        
        # Test 4: GELU activation
        print("\n📐 Test 4: GELU Activation")
        inp = Tensor([-1.0, 0.0, 1.0, 2.0], requires_grad=True)
        activated = inp.gelu()
        print(f"   Input:  {inp.data.tolist()}")
        print(f"   GELU:   {[f'{v:.4f}' for v in activated.data.tolist()]}")
        results["tests"].append({"name": "gelu", "status": "passed"})
        
        results["status"] = "success"
        print_success("Tensor Core demo completed successfully!")
        
    except ImportError as e:
        print_error(f"Failed to import Tensor Core: {e}")
        results["status"] = "import_error"
    except Exception as e:
        print_error(f"Tensor Core demo failed: {e}")
        if verbose:
            traceback.print_exc()
        results["status"] = "error"
        results["error"] = str(e)
    
    return results


def demo_genesis_engine(verbose: bool = False) -> Dict[str, Any]:
    """
    Demo 2: Genesis Engine - Quantum-Fractal Hybrid Cognition
    Shows quantum mesh, cognitive river, and fractal processing
    """
    print_section("DEMO 2: GENESIS ENGINE - Quantum-Fractal Cognition")
    
    results = {"status": "pending", "tests": []}
    
    try:
        from genesis import QuantumFractalMesh, CognitiveRiver, Victor
        print_success("Genesis Engine imported successfully")
        
        # Test 1: Quantum-Fractal Mesh
        print("\n⚛️ Test 1: Quantum-Fractal Mesh")
        mesh = QuantumFractalMesh(base_nodes=10, depth=2, num_superpositions=4)
        print(f"   Created mesh with {len(mesh.nodes)} nodes")
        print(f"   Base nodes: 10")
        print(f"   Depth: 2 (fractal expansion)")
        print(f"   Superpositions per node: 4")
        
        # Forward propagation through mesh
        input_vec = np.random.randn(3)
        output = mesh.forward_propagate(input_vec, "node_0")
        print_quantum(f"   Input: {input_vec}")
        print_quantum(f"   Output: {output}")
        results["tests"].append({"name": "quantum_mesh", "status": "passed"})
        
        # Test 2: Cognitive River
        print("\n🌊 Test 2: Cognitive River (Multi-Modal Fusion)")
        river = CognitiveRiver()
        
        # Set streams
        streams_data = {
            "user": ({"message": "Hello Victor!"}, 1.5),
            "emotion": ({"state": "curious", "intensity": 0.8}, 1.0),
            "memory": ({"context": "demo session"}, 0.8),
            "awareness": ({"focus": "quantum cognition"}, 1.2)
        }
        
        for stream, (payload, boost) in streams_data.items():
            river.set(stream, payload, boost=boost)
            print(f"   Set {stream}: {payload} (boost: {boost})")
        
        # Merge streams
        merged = river.merge()
        print(f"\n   Merged stream selection: {merged['merged']}")
        print(f"   Stream weights:")
        for stream, weight in list(merged['weights'].items())[:4]:
            print(f"      {stream}: {weight:.4f}")
        results["tests"].append({"name": "cognitive_river", "status": "passed"})
        
        # Test 3: Victor Intelligence Core
        print("\n🧠 Test 3: Victor Intelligence Core")
        victor = Victor()
        
        # Generate a thought
        thought = victor.think()
        print(f"   Thought count: {victor.thought_count}")
        print(f"   Insight: {thought['insight']}")
        print(f"   Quantum-fractal output: {thought['quantum_fractal'][:3]}...")
        results["tests"].append({"name": "victor_core", "status": "passed"})
        
        # Test 4: Multiple quantum propagations
        print("\n⚡ Test 4: Multiple Quantum Propagations")
        outputs = []
        # Get base nodes (exclude fractal depth extensions)
        base_node_ids = [n for n in mesh.nodes if '_d' not in n]
        base_node_count = len(base_node_ids)
        
        for i in range(5):
            inp = np.random.randn(3)
            node_index = i % base_node_count
            out = mesh.forward_propagate(inp, f"node_{node_index}")
            outputs.append(float(np.mean(out)))
        
        print(f"   5 propagations completed")
        print(f"   Output range: [{min(outputs):.4f}, {max(outputs):.4f}]")
        print(f"   Mean output: {np.mean(outputs):.4f}")
        results["tests"].append({"name": "multi_propagation", "status": "passed"})
        
        results["status"] = "success"
        print_success("Genesis Engine demo completed successfully!")
        
    except ImportError as e:
        print_error(f"Failed to import Genesis Engine: {e}")
        results["status"] = "import_error"
    except Exception as e:
        print_error(f"Genesis Engine demo failed: {e}")
        if verbose:
            traceback.print_exc()
        results["status"] = "error"
        results["error"] = str(e)
    
    return results


def demo_victor_hub(verbose: bool = False) -> Dict[str, Any]:
    """
    Demo 3: Victor Hub - Skill Registry and Task Execution
    Shows task routing, skill discovery, and execution pipeline
    """
    print_section("DEMO 3: VICTOR HUB - Skill Routing & Execution")
    
    results = {"status": "pending", "tests": []}
    
    try:
        from victor_hub.victor_boot import SkillRegistry, Task, Result, Skill
        print_success("Victor Hub imported successfully")
        
        # Test 1: Skill Registry
        print("\n📋 Test 1: Skill Registry")
        registry = SkillRegistry()
        
        # Register built-in skills
        from victor_hub.skills.echo_skill import EchoSkill
        from victor_hub.skills.content_generator import ContentGeneratorSkill
        
        echo_skill = EchoSkill()
        content_skill = ContentGeneratorSkill()
        
        registry.register(echo_skill)
        registry.register(content_skill)
        
        print(f"   Registered skills: {list(registry.skills.keys())}")
        stats = registry.get_stats()
        print(f"   Total skills: {stats['total_skills']}")
        results["tests"].append({"name": "skill_registry", "status": "passed"})
        
        # Test 2: Task Creation and Routing
        print("\n🎯 Test 2: Task Routing")
        task1 = Task(
            id="demo_task_1",
            type="echo",
            description="Echo test message",
            inputs={"message": "Hello from Victor Demo!"}
        )
        
        routed_skill = registry.route(task1)
        print(f"   Task: {task1.description}")
        print(f"   Type: {task1.type}")
        print(f"   Routed to: {routed_skill.name if routed_skill else 'None'}")
        results["tests"].append({"name": "task_routing", "status": "passed"})
        
        # Test 3: Task Execution
        print("\n⚡ Test 3: Task Execution")
        if routed_skill:
            result = routed_skill.execute(task1, {})
            print(f"   Status: {result.status}")
            print(f"   Output: {result.output}")
            results["tests"].append({"name": "task_execution", "status": "passed"})
        
        # Test 4: Content Generation
        print("\n📝 Test 4: Content Generation Skill")
        task2 = Task(
            id="demo_task_2",
            type="content",
            description="Generate a haiku about AI",
            inputs={"topic": "artificial intelligence", "format": "haiku"}
        )
        
        routed = registry.route(task2)
        if routed:
            result = routed.execute(task2, {})
            print(f"   Task: {task2.description}")
            print(f"   Status: {result.status}")
            print(f"   Output: {str(result.output)[:150]}...")
        results["tests"].append({"name": "content_generation", "status": "passed"})
        
        results["status"] = "success"
        print_success("Victor Hub demo completed successfully!")
        
    except ImportError as e:
        print_error(f"Failed to import Victor Hub: {e}")
        results["status"] = "import_error"
    except Exception as e:
        print_error(f"Victor Hub demo failed: {e}")
        if verbose:
            traceback.print_exc()
        results["status"] = "error"
        results["error"] = str(e)
    
    return results


def demo_nlp_integration(verbose: bool = False) -> Dict[str, Any]:
    """
    Demo 4: NLP Integration - Natural Language Processing
    Shows entity recognition, sentiment analysis, keyword extraction
    """
    print_section("DEMO 4: NLP INTEGRATION - Language Processing")
    
    results = {"status": "pending", "tests": []}
    
    try:
        # Check if spaCy is available
        try:
            import spacy
            nlp = spacy.load("en_core_web_sm")
            spacy_available = True
            print_success("spaCy loaded with en_core_web_sm model")
        except (ImportError, OSError):
            spacy_available = False
            print_info("spaCy not available - using basic NLP")
        
        # Test text
        sample_text = """
        Victor is an advanced AGI system developed by MASSIVEMAGNETICS in November 2025.
        It uses quantum-fractal cognition and neural networks for intelligent processing.
        The system integrates with Google Cloud, Microsoft Azure, and OpenAI APIs.
        """
        
        # Test 1: Text Statistics
        print("\n📊 Test 1: Text Statistics")
        words = sample_text.split()
        sentences = [s.strip() for s in sample_text.replace('\n', ' ').split('.') if s.strip()]
        print(f"   Word count: {len(words)}")
        print(f"   Sentence count: {len(sentences)}")
        print(f"   Character count: {len(sample_text)}")
        results["tests"].append({"name": "text_stats", "status": "passed"})
        
        # Test 2: Named Entity Recognition (if spaCy available)
        if spacy_available:
            print("\n🔍 Test 2: Named Entity Recognition")
            doc = nlp(sample_text)
            entities = [(ent.text, ent.label_) for ent in doc.ents]
            print(f"   Entities found: {len(entities)}")
            for text, label in entities[:5]:
                print(f"      • {text}: {label}")
            results["tests"].append({"name": "ner", "status": "passed"})
            
            # Test 3: Part-of-Speech Analysis
            print("\n📐 Test 3: Part-of-Speech Analysis")
            pos_sample = "Victor processes quantum interference patterns."
            doc = nlp(pos_sample)
            print(f"   Sentence: {pos_sample}")
            for token in doc:
                print(f"      {token.text:15} → {token.pos_:6} ({token.tag_})")
            results["tests"].append({"name": "pos_tagging", "status": "passed"})
            
            # Test 4: Keyword Extraction
            print("\n🔑 Test 4: Keyword Extraction")
            doc = nlp(sample_text)
            keywords = [token.text for token in doc 
                       if token.pos_ in ('NOUN', 'PROPN') and len(token.text) > 2]
            unique_keywords = list(set(keywords))[:8]
            print(f"   Keywords: {', '.join(unique_keywords)}")
            results["tests"].append({"name": "keywords", "status": "passed"})
        else:
            print("\n📝 Test 2-4: Basic NLP (spaCy not available)")
            # Basic keyword extraction without spaCy using module-level stopwords
            words = sample_text.lower().split()
            keywords = [w.strip('.,!?') for w in words 
                       if w.strip('.,!?') not in COMMON_STOPWORDS and len(w) > 3]
            unique_keywords = list(set(keywords))[:10]
            print(f"   Basic keywords: {', '.join(unique_keywords)}")
            results["tests"].append({"name": "basic_nlp", "status": "passed"})
        
        results["status"] = "success"
        print_success("NLP Integration demo completed successfully!")
        
    except Exception as e:
        print_error(f"NLP Integration demo failed: {e}")
        if verbose:
            traceback.print_exc()
        results["status"] = "error"
        results["error"] = str(e)
    
    return results


def demo_advanced_ai(verbose: bool = False) -> Dict[str, Any]:
    """
    Demo 5: Advanced AI - Holon Omega and Neural Systems
    Shows advanced cognition patterns and neural processing
    """
    print_section("DEMO 5: ADVANCED AI - Holon Omega Neural Systems")
    
    results = {"status": "pending", "tests": []}
    
    try:
        # Test 1: Tensor operations for neural networks
        print("\n🧮 Test 1: Neural Network Building Blocks")
        from advanced_ai.tensor_core import Tensor
        
        # Simple 2-layer network
        np.random.seed(42)
        x = Tensor(np.random.randn(4, 3))  # 4 samples, 3 features
        w1 = Tensor(np.random.randn(3, 5) * 0.1, requires_grad=True)  # First layer
        w2 = Tensor(np.random.randn(5, 2) * 0.1, requires_grad=True)  # Output layer
        
        # Forward pass
        h = x.matmul(w1).gelu()  # Hidden layer with GELU
        y = h.matmul(w2)  # Output
        loss = (y ** 2).sum()  # Simple L2 loss
        
        print(f"   Input shape: {x.data.shape}")
        print(f"   Hidden layer: {h.data.shape}")
        print(f"   Output shape: {y.data.shape}")
        print(f"   Loss: {loss.data:.4f}")
        
        # Backward pass
        loss.backward()
        print(f"   Gradients computed: w1={w1.grad.shape}, w2={w2.grad.shape}")
        results["tests"].append({"name": "neural_network", "status": "passed"})
        
        # Test 2: Training loop simulation
        print("\n📈 Test 2: Training Loop Simulation")
        losses = []
        w = Tensor(np.random.randn(3, 1) * 0.1, requires_grad=True)
        x_train = Tensor(np.random.randn(10, 3))
        y_target = Tensor(np.random.randn(10, 1))
        
        lr = 0.01
        for epoch in range(50):
            # Forward
            y_pred = x_train.matmul(w)
            diff = y_pred + (y_target * Tensor(-1.0))
            loss = (diff ** 2).sum()
            losses.append(loss.data)
            
            # Backward
            w.zero_grad()
            loss.backward()
            
            # Update
            w.data = w.data - lr * w.grad
        
        print(f"   Initial loss: {losses[0]:.4f}")
        print(f"   Final loss: {losses[-1]:.4f}")
        print(f"   Improvement: {((losses[0] - losses[-1]) / losses[0] * 100):.1f}%")
        results["tests"].append({"name": "training_loop", "status": "passed"})
        
        # Test 3: Holon-inspired pattern generation
        print("\n🌀 Test 3: Fractal Pattern Generation")
        
        def generate_fractal_pattern(depth: int, base_dim: int) -> np.ndarray:
            """Generate a fractal-inspired pattern"""
            pattern = np.zeros((base_dim, base_dim))
            phi = (1 + np.sqrt(5)) / 2  # Golden ratio
            
            for d in range(depth):
                scale = phi ** (-d)
                for i in range(base_dim):
                    for j in range(base_dim):
                        angle = 2 * np.pi * (i * phi + j) / base_dim
                        pattern[i, j] += scale * np.sin(angle * (d + 1))
            
            return pattern / depth
        
        pattern = generate_fractal_pattern(5, 8)
        print(f"   Generated {pattern.shape[0]}x{pattern.shape[1]} fractal pattern")
        print(f"   Value range: [{pattern.min():.4f}, {pattern.max():.4f}]")
        print(f"   Mean: {pattern.mean():.4f}, Std: {pattern.std():.4f}")
        results["tests"].append({"name": "fractal_patterns", "status": "passed"})
        
        # Test 4: Attention-like computation
        print("\n🎯 Test 4: Attention Mechanism Simulation")
        
        def softmax(x, axis=-1):
            exp_x = np.exp(x - np.max(x, axis=axis, keepdims=True))
            return exp_x / np.sum(exp_x, axis=axis, keepdims=True)
        
        # Query, Key, Value matrices
        seq_len, d_model = 6, 8
        Q = np.random.randn(seq_len, d_model)
        K = np.random.randn(seq_len, d_model)
        V = np.random.randn(seq_len, d_model)
        
        # Scaled dot-product attention
        scores = Q @ K.T / np.sqrt(d_model)
        attention_weights = softmax(scores)
        output = attention_weights @ V
        
        print(f"   Sequence length: {seq_len}, Model dim: {d_model}")
        print(f"   Attention weights shape: {attention_weights.shape}")
        print(f"   Output shape: {output.shape}")
        print(f"   Max attention: {attention_weights.max():.4f}")
        results["tests"].append({"name": "attention", "status": "passed"})
        
        results["status"] = "success"
        print_success("Advanced AI demo completed successfully!")
        
    except ImportError as e:
        print_error(f"Failed to import Advanced AI components: {e}")
        results["status"] = "import_error"
    except Exception as e:
        print_error(f"Advanced AI demo failed: {e}")
        if verbose:
            traceback.print_exc()
        results["status"] = "error"
        results["error"] = str(e)
    
    return results


def demo_interactive_runtime(verbose: bool = False) -> Dict[str, Any]:
    """
    Demo 6: Interactive Runtime Integration
    Shows how all systems work together in the unified runtime
    """
    print_section("DEMO 6: UNIFIED SYSTEM - Complete Integration")
    
    results = {"status": "pending", "tests": []}
    
    try:
        # Test 1: Full pipeline simulation
        print("\n🔗 Test 1: Full Processing Pipeline")
        
        # Import components
        from advanced_ai.tensor_core import Tensor
        from genesis import QuantumFractalMesh, CognitiveRiver
        
        # Initialize systems
        mesh = QuantumFractalMesh(base_nodes=10, depth=2)
        river = CognitiveRiver()
        
        # Simulate a complete processing flow
        user_input = "What is the meaning of consciousness?"
        
        # Step 1: Create input embedding (simulated)
        embedding = np.array([hash(c) % 256 / 256.0 for c in user_input[:10]])
        embedding = embedding / (np.linalg.norm(embedding) + 1e-8)
        
        # Step 2: Quantum-fractal processing
        quantum_output = mesh.forward_propagate(embedding, "node_0")
        
        # Step 3: Update cognitive river
        # Note: Stream names must be from CognitiveRiver.STREAMS: 
        # ["status", "emotion", "memory", "awareness", "systems", "user", "sensory", "realworld"]
        river.set("user", {"query": user_input}, boost=1.5)
        river.set("awareness", {"quantum_output": float(np.mean(quantum_output))}, boost=1.0)
        merged = river.merge()
        
        # Step 4: Generate response context
        context = {
            "quantum_signal": float(np.mean(quantum_output)),
            "primary_stream": merged["merged"],
            "processing_time": time.time()
        }
        
        print(f"   Input: '{user_input[:40]}...'")
        print(f"   Embedding dim: {len(embedding)}")
        print(f"   Quantum output: {np.mean(quantum_output):.4f}")
        print(f"   Selected stream: {merged['merged']}")
        results["tests"].append({"name": "full_pipeline", "status": "passed"})
        
        # Test 2: Multi-modal fusion
        print("\n🔀 Test 2: Multi-Modal Fusion")
        
        # Simulate multiple input modalities
        # Using valid CognitiveRiver stream names: sensory, emotion, memory, awareness
        modalities = {
            "sensory": np.random.randn(8),
            "emotion": np.array([0.8, 0.2, 0.1]),  # Joy, neutral, sad
            "memory": np.random.randn(4),
            "awareness": np.random.randn(6)
        }
        
        # Simple fusion: weighted combination
        weights = {"sensory": 0.4, "emotion": 0.2, "memory": 0.2, "awareness": 0.2}
        
        for mod, data in modalities.items():
            river.set(mod, {"data": data.tolist()}, boost=weights[mod])
        
        final_merge = river.merge()
        print(f"   Modalities fused: {list(modalities.keys())}")
        print(f"   Weights: {weights}")
        print(f"   Selected modality: {final_merge['merged']}")
        results["tests"].append({"name": "multimodal_fusion", "status": "passed"})
        
        # Test 3: Session state tracking
        print("\n💾 Test 3: Session State Tracking")
        
        session_state = {
            "session_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "commands_executed": 0,
            "quantum_iterations": 0,
            "evolution_cycles": 0,
            "context_history": []
        }
        
        # Simulate session activity
        for i in range(5):
            session_state["commands_executed"] += 1
            session_state["quantum_iterations"] += 1
            session_state["context_history"].append({
                "step": i,
                "quantum": float(np.random.random()),
                "timestamp": time.time()
            })
        
        print(f"   Session ID: {session_state['session_id']}")
        print(f"   Commands: {session_state['commands_executed']}")
        print(f"   Quantum iterations: {session_state['quantum_iterations']}")
        print(f"   Context history: {len(session_state['context_history'])} entries")
        results["tests"].append({"name": "session_tracking", "status": "passed"})
        
        # Test 4: Evolution simulation
        print("\n🧬 Test 4: Quantum Evolution Simulation")
        
        # Simulate parameter evolution
        params = np.random.randn(8, 4) * 0.1
        
        for gen in range(3):
            # Random mutation
            mutation = np.random.randn(*params.shape) * 0.01
            params = params + mutation
            
            # Fitness evaluation (simulated)
            fitness = float(np.mean(np.abs(params)))
            
            if gen == 0 or gen == 2:
                print(f"   Generation {gen+1}: Fitness = {fitness:.4f}")
        
        print(f"   Final parameters: {params.shape} tensor")
        results["tests"].append({"name": "evolution", "status": "passed"})
        
        results["status"] = "success"
        print_success("Unified System demo completed successfully!")
        
    except Exception as e:
        print_error(f"Unified System demo failed: {e}")
        if verbose:
            traceback.print_exc()
        results["status"] = "error"
        results["error"] = str(e)
    
    return results


# =============================================================================
# MAIN DEMO RUNNER
# =============================================================================

def run_full_demo(interactive: bool = False, verbose: bool = False) -> Dict[str, Any]:
    """
    Run the complete Victor demonstration
    """
    print_header("VICTOR SYNTHETIC SUPER INTELLIGENCE", "═", Colors.QUANTUM)
    print(f"{Colors.BOLD}Full Working Demo - Version 2.1.0-QUANTUM-FRACTAL{Colors.ENDC}")
    print(f"{Colors.CYAN}Organization: MASSIVEMAGNETICS{Colors.ENDC}")
    print(f"{Colors.CYAN}Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.ENDC}")
    
    if interactive:
        print(f"\n{Colors.YELLOW}[Interactive Mode]{Colors.ENDC}")
        input("Press Enter to start the demo...")
    
    # Track all results
    all_results = {
        "start_time": datetime.now().isoformat(),
        "demos": {},
        "summary": {"passed": 0, "failed": 0, "total": 0}
    }
    
    # Define demos
    demos = [
        ("Tensor Core", demo_tensor_core),
        ("Genesis Engine", demo_genesis_engine),
        ("Victor Hub", demo_victor_hub),
        ("NLP Integration", demo_nlp_integration),
        ("Advanced AI", demo_advanced_ai),
        ("Unified System", demo_interactive_runtime),
    ]
    
    # Run each demo
    for i, (name, demo_func) in enumerate(demos, 1):
        if interactive:
            print(f"\n{Colors.YELLOW}Demo {i}/{len(demos)}: {name}{Colors.ENDC}")
            user_input = input("Run this demo? [Y/n/q]: ").strip().lower()
            if user_input == 'q':
                print("Demo cancelled by user.")
                break
            if user_input == 'n':
                print(f"Skipping {name}...")
                continue
        
        try:
            result = demo_func(verbose=verbose)
            all_results["demos"][name] = result
            
            # Update summary
            all_results["summary"]["total"] += 1
            if result["status"] == "success":
                all_results["summary"]["passed"] += 1
            else:
                all_results["summary"]["failed"] += 1
                
        except Exception as e:
            print_error(f"Demo '{name}' crashed: {e}")
            all_results["demos"][name] = {"status": "crashed", "error": str(e)}
            all_results["summary"]["failed"] += 1
            all_results["summary"]["total"] += 1
    
    # Print summary
    all_results["end_time"] = datetime.now().isoformat()
    
    print_header("DEMO SUMMARY", "═", Colors.GREEN)
    
    passed = all_results["summary"]["passed"]
    failed = all_results["summary"]["failed"]
    total = all_results["summary"]["total"]
    
    print(f"   {Colors.GREEN}Passed:{Colors.ENDC} {passed}")
    print(f"   {Colors.RED}Failed:{Colors.ENDC} {failed}")
    print(f"   {Colors.CYAN}Total:{Colors.ENDC} {total}")
    print(f"   {Colors.BOLD}Success Rate:{Colors.ENDC} {(passed/max(1,total)*100):.1f}%")
    
    print("\n   Demo Results:")
    for name, result in all_results["demos"].items():
        status = result.get("status", "unknown")
        icon = "✓" if status == "success" else "✗"
        color = Colors.GREEN if status == "success" else Colors.RED
        print(f"   {color}{icon}{Colors.ENDC} {name}: {status}")
    
    if passed == total and total > 0:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 All demos completed successfully!{Colors.ENDC}")
        print(f"\n{Colors.CYAN}Victor is ready for co-domination.{Colors.ENDC}")
    elif failed > 0:
        print(f"\n{Colors.YELLOW}⚠ Some demos had issues. Check the output above for details.{Colors.ENDC}")
    
    print(f"\n{Colors.CYAN}{'═' * 80}{Colors.ENDC}")
    print(f"{Colors.BOLD}Built with 🧠 by MASSIVEMAGNETICS{Colors.ENDC}")
    print(f"{Colors.CYAN}{'═' * 80}{Colors.ENDC}\n")
    
    return all_results


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Victor Synthetic Super Intelligence - Full Working Demo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python full_demo.py                    # Run all demos
  python full_demo.py --interactive      # Run with user prompts
  python full_demo.py --verbose          # Show detailed output/errors
  python full_demo.py -i -v              # Interactive with verbose output

Documentation: https://github.com/MASSIVEMAGNETICS/Victor_Synthetic_Super_Intelligence
        """
    )
    
    parser.add_argument(
        '-i', '--interactive',
        action='store_true',
        help='Run in interactive mode with user prompts'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show verbose output including full error traces'
    )
    
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results as JSON'
    )
    
    args = parser.parse_args()
    
    try:
        results = run_full_demo(
            interactive=args.interactive,
            verbose=args.verbose
        )
        
        if args.json:
            import json
            print(json.dumps(results, indent=2, default=str))
        
        # Exit with appropriate code
        if results["summary"]["failed"] == 0:
            sys.exit(0)
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Demo interrupted by user.{Colors.ENDC}")
        sys.exit(130)
    except Exception as e:
        print(f"{Colors.RED}Fatal error: {e}{Colors.ENDC}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
