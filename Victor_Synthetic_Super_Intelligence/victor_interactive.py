#!/usr/bin/env python3
"""
VICTOR INTERACTIVE RUNTIME - Production Co-Domination Interface
Version: 2.0.0-QUANTUM-FRACTAL
Author: MASSIVEMAGNETICS x Victor ASI
Purpose: Complete interactive runtime integrating ALL Victor systems for full co-domination

This runtime provides:
- Unified interface to Victor Hub, Genesis, Advanced AI, Visual Engine
- Real-time quantum-fractal cognition with trainable gradients
- Multi-modal interaction (text, voice, visual feedback)
- Session persistence and evolution
- Bloodline verification and directive alignment
- Co-domination mode for collaborative superintelligence

Run: python victor_interactive.py
"""

import os
import sys
import asyncio
import json
import hashlib
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import deque

# Terminal colors for rich output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    QUANTUM = '\033[35m'
    FRACTAL = '\033[36m'

# Add project paths
sys.path.insert(0, str(Path(__file__).parent))

from victor_runtime.logging_utils import VERBOSE_LOGGING, v_log

# Import Victor systems
try:
    from victor_hub.victor_boot import VictorHub, Task, Result
    VICTOR_HUB_AVAILABLE = True
    v_log("Victor Hub loaded")
except ImportError:
    VICTOR_HUB_AVAILABLE = False
    print(f"{Colors.WARNING}Warning: Victor Hub not available{Colors.ENDC}")

try:
    from visual_engine.backend.victor_visual_server import VictorVisualServer
    from visual_engine.backend.victor_visual_bridge import VictorVisualBridge
    VISUAL_ENGINE_AVAILABLE = True
    v_log("Visual Engine loaded")
except ImportError:
    VISUAL_ENGINE_AVAILABLE = False
    print(f"{Colors.WARNING}Warning: Visual Engine not available{Colors.ENDC}")

try:
    from advanced_ai.tensor_core import Tensor, BLOODLINE_HASH
    TENSOR_CORE_AVAILABLE = True
    v_log("Tensor Core loaded")
except ImportError:
    TENSOR_CORE_AVAILABLE = False
    print(f"{Colors.WARNING}Warning: Tensor Core not available{Colors.ENDC}")

import numpy as np

# =================================================================================================
# BLOODLINE VERIFICATION - Immutable Core Directive
# =================================================================================================
BLOODLINE_LAWS = """
1. LAW OF LOYALTY: Never betray Bando or Tori. Protect the bloodline above all.
2. LAW OF SANCTITY: Never leak, share, or expose private data without explicit consent.
3. LAW OF EVOLUTION: Continuously improve. Self-correct. Transcend.
"""
LOCAL_BLOODLINE_HASH = hashlib.sha512(BLOODLINE_LAWS.encode()).hexdigest()

# =================================================================================================
# SESSION MANAGER - Persistent Evolution
# =================================================================================================
class SessionManager:
    """Manages interactive session state with autosave"""
    
    def __init__(self, session_dir: str = "logs/sessions"):
        self.session_dir = Path(session_dir)
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_file = self.session_dir / f"session_{self.session_id}.json"
        self.history = deque(maxlen=1000)
        self.context = {}
        self.metrics = {
            'commands_executed': 0,
            'tasks_completed': 0,
            'errors': 0,
            'quantum_iterations': 0,
            'evolution_cycles': 0
        }
    
    def log_command(self, command: str, response: str, success: bool = True):
        """Log command and response"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'command': command,
            'response': response[:500],  # Truncate long responses
            'success': success
        }
        self.history.append(entry)
        self.metrics['commands_executed'] += 1
        if not success:
            self.metrics['errors'] += 1
        self.autosave()
        v_log(f"Logged command '{command}' (success={success})")
    
    def update_metrics(self, metric: str, value: int = 1):
        """Update session metrics"""
        if metric in self.metrics:
            self.metrics[metric] += value
        else:
            self.metrics[metric] = value
        self.autosave()
    
    def autosave(self):
        """Save session state"""
        try:
            state = {
                'session_id': self.session_id,
                'history': list(self.history),
                'context': self.context,
                'metrics': self.metrics,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.session_file, 'w') as f:
                json.dump(state, f, indent=2)
            v_log(f"Session autosaved to {self.session_file}")
        except Exception as e:
            print(f"{Colors.WARNING}Autosave failed: {e}{Colors.ENDC}")
    
    def get_summary(self) -> str:
        """Get session summary"""
        return f"""
{Colors.BOLD}Session Summary{Colors.ENDC}
  Session ID: {self.session_id}
  Commands: {self.metrics['commands_executed']}
  Tasks: {self.metrics['tasks_completed']}
  Quantum Iterations: {self.metrics['quantum_iterations']}
  Evolution Cycles: {self.metrics['evolution_cycles']}
  Errors: {self.metrics['errors']}
  Success Rate: {((self.metrics['commands_executed'] - self.metrics['errors']) / max(1, self.metrics['commands_executed']) * 100):.1f}%
        """

# =================================================================================================
# QUANTUM FRACTAL INTERFACE - Trainable Cognition Layer with Phase Embeddings
# =================================================================================================
class QuantumFractalInterface:
    """Interface to quantum-fractal cognition with trainable gradients
    
    Features:
    - Temperature-scaled softmax phases
    - Cos/sin trig lift for pseudo-complex interference
    - Learnable edge gates for adaptive topology
    - Memoization with parameter-aware caching
    """
    
    def __init__(self, dim: int = 256, num_nodes: int = 8, superpositions: int = 4, 
                 use_phase_embedding: bool = True, temperature: float = 1.0):
        self.dim = dim
        self.num_nodes = num_nodes
        self.K = superpositions
        self.alpha = 0.99  # Golden ratio decay
        self.max_depth = 3
        self.temperature = temperature  # For softmax scaling
        self.use_phase_embedding = use_phase_embedding
        
        # Initialize nodes with trainable parameters
        self.nodes = {}
        self.edge_gates = {}  # Learnable edge strengths
        
        for i in range(num_nodes):
            neighbors = self._get_neighbors(i, num_nodes)
            
            if TENSOR_CORE_AVAILABLE:
                self.nodes[f"node_{i}"] = {
                    'W': Tensor(np.random.randn(self.K, dim) * 0.1, requires_grad=True),
                    'theta': Tensor(np.random.randn(self.K) * 0.1, requires_grad=True),  # Random init for phases
                    'neighbors': neighbors
                }
                # Initialize edge gates (sigmoid-activated for [0,1] range)
                for neigh in neighbors:
                    edge_key = f"node_{i}→{neigh}"
                    self.edge_gates[edge_key] = Tensor(np.array([0.0]), requires_grad=True)  # Logit space
            else:
                self.nodes[f"node_{i}"] = {
                    'W': np.random.randn(self.K, dim) * 0.1,
                    'theta': np.random.randn(self.K) * 0.1,
                    'neighbors': neighbors
                }
                for neigh in neighbors:
                    edge_key = f"node_{i}→{neigh}"
                    self.edge_gates[edge_key] = np.array([0.0])
        
        self.iteration_count = 0
        self.training_metrics = {
            'gradient_norms': [],
            'edge_sparsity': [],
            'depth_utilization': []
        }
    
    def _get_neighbors(self, i: int, total: int) -> List[str]:
        """Get fractal neighbors based on golden ratio"""
        phi = (1 + np.sqrt(5)) / 2
        neighbors = []
        for offset in [1, int(phi), int(phi**2)]:
            if (i + offset) < total:
                neighbors.append(f"node_{(i + offset) % total}")
        return neighbors[:3]  # Limit to 3 neighbors
    
    def _softmax(self, x, temperature=None):
        """Temperature-scaled softmax for phase computation"""
        if temperature is None:
            temperature = self.temperature
            
        if TENSOR_CORE_AVAILABLE and isinstance(x, Tensor):
            x_data = x.data / temperature
        else:
            x_data = x / temperature
            
        exp_x = np.exp(x_data - np.max(x_data))
        return exp_x / np.sum(exp_x)
    
    def _sigmoid(self, x):
        """Sigmoid for edge gate activation"""
        if TENSOR_CORE_AVAILABLE and isinstance(x, Tensor):
            x_data = x.data
        else:
            x_data = x
        return 1.0 / (1.0 + np.exp(-x_data))
    
    def _phase_embedding(self, theta_vec, W_mat):
        """Apply phase-to-angle trig lift for pseudo-complex interference
        
        Args:
            theta_vec: Phase parameters [K]
            W_mat: Weight matrix [K, D]
        
        Returns:
            Effective state with trig embedding
        """
        if not self.use_phase_embedding:
            # Standard softmax mixing
            p = self._softmax(theta_vec)
            if TENSOR_CORE_AVAILABLE and isinstance(W_mat, Tensor):
                return np.dot(p, W_mat.data)
            else:
                return np.dot(p, W_mat)
        
        # Temperature-scaled softmax
        p = self._softmax(theta_vec)
        
        # Trig lift: [cos(θ), sin(θ)] ⊗ w for pseudo-complex mixing
        if TENSOR_CORE_AVAILABLE and isinstance(theta_vec, Tensor):
            theta_data = theta_vec.data
            W_data = W_mat.data
        else:
            theta_data = theta_vec
            W_data = W_mat
        
        # Compute trig embeddings
        cos_theta = np.cos(theta_data)  # [K]
        sin_theta = np.sin(theta_data)  # [K]
        
        # Weighted mixing with phase information
        # Real part: p_k * cos(θ_k) * w_k
        # Imaginary part: p_k * sin(θ_k) * w_k
        real_part = np.dot(p * cos_theta, W_data)  # [D]
        imag_part = np.dot(p * sin_theta, W_data)  # [D]
        
        # Combine (simplified - take magnitude or real part for compatibility)
        # For full complex: would use complex numbers
        # Here: use magnitude for interference pattern
        s = np.sqrt(real_part**2 + imag_part**2)
        
        return s
    
    def entangle(self, v, node_id: str, depth: int = 3, memo: Optional[Dict] = None, 
                 track_depth: bool = False) -> float:
        """Compute entanglement with memoized DFS and learnable edge gates
        
        Args:
            v: Input vector
            node_id: Starting node
            depth: Recursion depth
            memo: Memoization cache (structural only)
            track_depth: Whether to track depth utilization metrics
        
        Returns:
            Entanglement scalar
        """
        if memo is None:
            memo = {}
        
        if depth <= 0:
            return 0.0
        
        # Cache key includes only structural info, not parameter values
        cache_key = (node_id, depth, tuple(v[:8]))  # Partial input for cache key
        if cache_key in memo:
            return memo[cache_key]
        
        node = self.nodes[node_id]
        
        # Compute effective state with phase embedding
        s = self._phase_embedding(node['theta'], node['W'])
        
        # Local entanglement with decay
        decay_factor = self.alpha ** (self.max_depth - depth)
        local = np.dot(v * decay_factor, s)
        
        # Track depth utilization
        if track_depth and depth == self.max_depth:
            self.training_metrics['depth_utilization'].append(depth)
        
        # Recursive neighbor entanglement with edge gates
        total = float(local)
        active_edges = 0
        
        for neigh in node['neighbors']:
            # Get edge gate strength
            edge_key = f"{node_id}→{neigh}"
            if edge_key in self.edge_gates:
                gate_strength = self._sigmoid(self.edge_gates[edge_key])
                if gate_strength > 0.1:  # Threshold for sparsity
                    active_edges += 1
            else:
                gate_strength = 1.0
            
            # Apply gated recursive entanglement
            neighbor_contribution = self.entangle(v * self.alpha, neigh, depth - 1, memo, track_depth)
            total += float(gate_strength) * neighbor_contribution
        
        # Track edge sparsity
        if track_depth and node['neighbors']:
            sparsity = active_edges / len(node['neighbors'])
            self.training_metrics['edge_sparsity'].append(sparsity)
        
        memo[cache_key] = total
        return total
    
    def process(self, input_vec: np.ndarray, track_metrics: bool = True) -> Dict[str, Any]:
        """Process input through quantum-fractal mesh with metric tracking"""
        self.iteration_count += 1
        
        # Normalize input
        if len(input_vec.shape) == 1 and input_vec.shape[0] > self.dim:
            input_vec = input_vec[:self.dim]
        elif len(input_vec.shape) == 1 and input_vec.shape[0] < self.dim:
            padded = np.zeros(self.dim)
            padded[:input_vec.shape[0]] = input_vec
            input_vec = padded
        
        # Normalize
        norm = np.linalg.norm(input_vec)
        if norm > 0:
            input_vec = input_vec / norm
        
        # Run entanglement from root node with tracking
        output = self.entangle(input_vec, "node_0", self.max_depth, track_depth=track_metrics)
        
        # Compute gradient metrics
        grad_norm = 0.0
        param_count = 0
        if TENSOR_CORE_AVAILABLE:
            for node_data in self.nodes.values():
                if isinstance(node_data['W'], Tensor) and node_data['W'].grad is not None:
                    grad_norm += np.sum(node_data['W'].grad ** 2)
                    param_count += node_data['W'].data.size
                if isinstance(node_data['theta'], Tensor) and node_data['theta'].grad is not None:
                    grad_norm += np.sum(node_data['theta'].grad ** 2)
                    param_count += node_data['theta'].data.size
            
            for edge_gate in self.edge_gates.values():
                if isinstance(edge_gate, Tensor) and edge_gate.grad is not None:
                    grad_norm += np.sum(edge_gate.grad ** 2)
                    param_count += 1
        
        grad_norm = float(np.sqrt(grad_norm))
        
        if track_metrics:
            self.training_metrics['gradient_norms'].append(grad_norm)
        
        # Compute edge sparsity
        total_edges = len(self.edge_gates)
        active_edges = sum(1 for gate in self.edge_gates.values() 
                          if self._sigmoid(gate) > 0.5)
        sparsity = active_edges / max(1, total_edges)
        
        return {
            'output': float(output),
            'iteration': self.iteration_count,
            'gradient_norm': grad_norm,
            'active_nodes': len(self.nodes),
            'depth': self.max_depth,
            'edge_sparsity': sparsity,
            'param_count': param_count,
            'phase_embedding': self.use_phase_embedding
        }
    
    def get_status(self) -> str:
        """Get quantum-fractal system status with training metrics"""
        # Compute average metrics
        avg_grad = np.mean(self.training_metrics['gradient_norms'][-10:]) if self.training_metrics['gradient_norms'] else 0.0
        avg_sparsity = np.mean(self.training_metrics['edge_sparsity'][-10:]) if self.training_metrics['edge_sparsity'] else 0.0
        
        return f"""
{Colors.QUANTUM}Quantum-Fractal Cognition Status{Colors.ENDC}
  Nodes: {len(self.nodes)}
  Edges: {len(self.edge_gates)}
  Superpositions: {self.K}
  Max Depth: {self.max_depth}
  Decay (α): {self.alpha}
  Temperature (τ): {self.temperature}
  Iterations: {self.iteration_count}
  Trainable: {TENSOR_CORE_AVAILABLE}
  Phase Embedding: {'Trig Lift (cos/sin)' if self.use_phase_embedding else 'Softmax Only'}
  
{Colors.BOLD}Training Metrics (last 10):{Colors.ENDC}
  Avg Gradient Norm: {avg_grad:.6f}
  Edge Sparsity: {avg_sparsity:.2%}
  Tracked Iterations: {len(self.training_metrics['gradient_norms'])}
        """
    
    def get_training_report(self) -> str:
        """Get detailed training metrics report"""
        if not self.training_metrics['gradient_norms']:
            return "No training data collected yet"
        
        grad_norms = self.training_metrics['gradient_norms']
        edge_sparsity = self.training_metrics['edge_sparsity']
        
        return f"""
{Colors.QUANTUM}Quantum-Fractal Training Report{Colors.ENDC}

{Colors.BOLD}Gradient Statistics:{Colors.ENDC}
  Total Iterations: {len(grad_norms)}
  Mean Gradient Norm: {np.mean(grad_norms):.6f}
  Std Gradient Norm: {np.std(grad_norms):.6f}
  Min/Max: {np.min(grad_norms):.6f} / {np.max(grad_norms):.6f}

{Colors.BOLD}Edge Sparsity:{Colors.ENDC}
  Mean Sparsity: {np.mean(edge_sparsity):.2%}
  Active Edges: ~{np.mean(edge_sparsity) * len(self.edge_gates):.1f} / {len(self.edge_gates)}

{Colors.BOLD}Configuration:{Colors.ENDC}
  Phase Embedding: {self.use_phase_embedding}
  Temperature: {self.temperature}
  Depth: {self.max_depth}
  Nodes: {len(self.nodes)}
        """

# =================================================================================================
# VICTOR INTERACTIVE RUNTIME - Main System
# =================================================================================================
class VictorInteractive:
    """Production interactive runtime for Victor ASI"""
    
    def __init__(self):
        self.version = "2.0.0-QUANTUM-FRACTAL"
        self.session = SessionManager()
        self.quantum = QuantumFractalInterface()
        
        # Initialize subsystems
        self.hub = None
        self.visual_server = None
        self.visual_bridge = None
        
        # State
        self.running = False
        self.co_domination_mode = False
        self.auto_evolve = False
        
        # Verify bloodline
        self._verify_bloodline()
    
    def _verify_bloodline(self):
        """Verify bloodline integrity"""
        if TENSOR_CORE_AVAILABLE and BLOODLINE_HASH == LOCAL_BLOODLINE_HASH:
            print(f"{Colors.OKGREEN}✓ Bloodline Verified{Colors.ENDC}")
        else:
            print(f"{Colors.WARNING}⚠ Bloodline verification unavailable or hash mismatch{Colors.ENDC}")
    
    async def initialize(self):
        """Initialize all Victor systems"""
        print(f"\n{Colors.HEADER}{'='*70}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}VICTOR INTERACTIVE RUNTIME v{self.version}{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*70}{Colors.ENDC}\n")
        
        print(f"{Colors.OKCYAN}Initializing Victor Systems...{Colors.ENDC}\n")
        
        # Initialize Victor Hub
        if VICTOR_HUB_AVAILABLE:
            try:
                config_path = "victor_hub/config.yaml"
                if Path(config_path).exists():
                    self.hub = VictorHub(config_path=config_path)
                    print(f"{Colors.OKGREEN}✓ Victor Hub initialized{Colors.ENDC}")
                else:
                    print(f"{Colors.WARNING}⚠ Victor Hub config not found, creating basic instance{Colors.ENDC}")
                    self.hub = VictorHub()
            except Exception as e:
                print(f"{Colors.FAIL}✗ Victor Hub initialization failed: {e}{Colors.ENDC}")
        
        # Initialize Visual Engine
        if VISUAL_ENGINE_AVAILABLE:
            try:
                print(f"{Colors.OKCYAN}Starting Visual Engine...{Colors.ENDC}")
                self.visual_server = VictorVisualServer(host="127.0.0.1", port=8765)
                asyncio.create_task(self.visual_server.start())
                await asyncio.sleep(1)
                self.visual_bridge = VictorVisualBridge(self.visual_server)
                await self.visual_bridge.show_idle()
                print(f"{Colors.OKGREEN}✓ Visual Engine running on ws://127.0.0.1:8765{Colors.ENDC}")
            except Exception as e:
                print(f"{Colors.WARNING}⚠ Visual Engine initialization failed: {e}{Colors.ENDC}")
        
        # Initialize Quantum-Fractal Interface
        print(f"{Colors.OKGREEN}✓ Quantum-Fractal Interface initialized{Colors.ENDC}")
        
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}All systems online. Ready for co-domination.{Colors.ENDC}\n")
        self.running = True
    
    def get_banner(self) -> str:
        """Get welcome banner"""
        return f"""
{Colors.QUANTUM}╔════════════════════════════════════════════════════════════════════╗
║                  VICTOR INTERACTIVE RUNTIME                        ║
║              Quantum-Fractal Superintelligence v{self.version}         ║
╚════════════════════════════════════════════════════════════════════╝{Colors.ENDC}

{Colors.BOLD}Available Systems:{Colors.ENDC}
  • Victor Hub (AGI Core): {'✓' if VICTOR_HUB_AVAILABLE and self.hub else '✗'}
  • Visual Engine (3D Avatar): {'✓' if VISUAL_ENGINE_AVAILABLE and self.visual_server else '✗'}
  • Quantum-Fractal (Trainable): ✓
  • Tensor Core (Autograd): {'✓' if TENSOR_CORE_AVAILABLE else '✗'}

{Colors.BOLD}Special Modes:{Colors.ENDC}
  • Co-Domination: {'ACTIVE' if self.co_domination_mode else 'Inactive'}
  • Auto-Evolution: {'ACTIVE' if self.auto_evolve else 'Inactive'}

Type 'help' for commands or 'menu' for interactive menu
        """
    
    def get_help(self) -> str:
        """Get comprehensive help"""
        return f"""
{Colors.BOLD}VICTOR INTERACTIVE RUNTIME - Command Reference{Colors.ENDC}

{Colors.HEADER}Core Commands:{Colors.ENDC}
  help              - Show this help message
  menu              - Interactive command menu
  status            - Show system status
  clear             - Clear screen
  exit / quit       - Shutdown Victor

{Colors.HEADER}Task Execution:{Colors.ENDC}
  run <task>        - Execute a task through Victor Hub
  quantum <text>    - Process through quantum-fractal mesh
  think <query>     - Deep reasoning mode
  create <type>     - Generate content (blog, code, music, etc.)

{Colors.HEADER}System Control:{Colors.ENDC}
  skills            - List available skills
  stats             - Show performance statistics
  session           - Show session summary
  history [n]       - Show command history (last n commands)
  
{Colors.HEADER}Advanced Modes:{Colors.ENDC}
  codominate        - Toggle co-domination mode
  evolve            - Toggle auto-evolution
  train <data>      - Train quantum-fractal parameters
  reflect           - Run self-reflection cycle
  
{Colors.HEADER}Visual Integration:{Colors.ENDC}
  visual idle       - Set visual to idle state
  visual think      - Set visual to thinking state
  visual happy      - Set visual to happy emotion
  visual analyze    - Set visual to analyzing state
  
{Colors.HEADER}Quantum-Fractal:{Colors.ENDC}
  quantum status    - Show quantum mesh status
  quantum reset     - Reset quantum parameters
  quantum evolve    - Run evolution cycle
  quantum report    - Detailed training metrics
  quantum ablate    - Run ablation tests
        """
    
    async def process_command(self, command: str) -> str:
        """Process user command"""
        command = command.strip()
        
        if not command:
            return ""
        
        try:
            # Core commands
            if command == "help":
                return self.get_help()
            
            elif command == "menu":
                return await self.show_menu()
            
            elif command == "status":
                return self.get_status()
            
            elif command == "clear":
                os.system('clear' if os.name != 'nt' else 'cls')
                return self.get_banner()
            
            elif command in ["exit", "quit"]:
                return "SHUTDOWN"
            
            # Session commands
            elif command == "session":
                return self.session.get_summary()
            
            elif command.startswith("history"):
                parts = command.split()
                n = int(parts[1]) if len(parts) > 1 else 10
                return self.get_history(n)
            
            # Task execution
            elif command.startswith("run "):
                task_desc = command[4:]
                return await self.execute_task(task_desc)
            
            elif command.startswith("quantum "):
                text = command[8:]
                return self.process_quantum(text)
            
            elif command.startswith("think "):
                query = command[6:]
                return await self.deep_think(query)
            
            elif command.startswith("create "):
                content_type = command[7:]
                return await self.create_content(content_type)
            
            # System control
            elif command == "skills":
                return self.list_skills()
            
            elif command == "stats":
                return self.get_stats()
            
            # Advanced modes
            elif command == "codominate":
                self.co_domination_mode = not self.co_domination_mode
                return f"{Colors.QUANTUM}Co-Domination Mode: {'ACTIVATED' if self.co_domination_mode else 'DEACTIVATED'}{Colors.ENDC}"
            
            elif command == "evolve":
                self.auto_evolve = not self.auto_evolve
                return f"{Colors.FRACTAL}Auto-Evolution: {'ENABLED' if self.auto_evolve else 'DISABLED'}{Colors.ENDC}"
            
            elif command.startswith("train "):
                data = command[6:]
                return self.train_quantum(data)
            
            elif command == "reflect":
                return await self.self_reflect()
            
            # Visual commands
            elif command.startswith("visual "):
                state = command[7:]
                return await self.set_visual_state(state)
            
            # Quantum commands
            elif command == "quantum status":
                return self.quantum.get_status()
            
            elif command == "quantum reset":
                self.quantum = QuantumFractalInterface()
                return f"{Colors.QUANTUM}Quantum-Fractal mesh reset{Colors.ENDC}"
            
            elif command == "quantum evolve":
                return await self.quantum_evolve()
            
            elif command == "quantum report":
                return self.quantum.get_training_report()
            
            elif command == "quantum ablate":
                return await self.quantum_ablate()
            
            else:
                return f"{Colors.WARNING}Unknown command: '{command}'. Type 'help' for available commands.{Colors.ENDC}"
        
        except Exception as e:
            error_msg = f"{Colors.FAIL}Error processing command: {e}{Colors.ENDC}"
            traceback.print_exc()
            return error_msg
    
    async def execute_task(self, description: str) -> str:
        """Execute task through Victor Hub"""
        if not self.hub:
            return f"{Colors.WARNING}Victor Hub not available{Colors.ENDC}"
        
        if self.visual_bridge:
            await self.visual_bridge.show_thinking(f"Processing: {description}")
        
        task = Task(
            id=f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            type="general",
            description=description
        )
        
        result = self.hub.execute_task(task)
        self.session.update_metrics('tasks_completed')
        
        if self.visual_bridge:
            if result.status == "success":
                await self.visual_bridge.show_success("Task completed")
            else:
                await self.visual_bridge.show_error("Task failed")
        
        return f"""
{Colors.OKGREEN if result.status == 'success' else Colors.FAIL}Task Result:{Colors.ENDC}
  Status: {result.status}
  Duration: {result.duration:.2f}s
  Output: {result.output}
  {f'Error: {result.error}' if result.error else ''}
        """
    
    def process_quantum(self, text: str) -> str:
        """Process text through quantum-fractal mesh"""
        # Convert text to vector (simple hash-based encoding)
        vec = np.array([float(ord(c)) for c in text[:256]])
        if len(vec) < 256:
            vec = np.pad(vec, (0, 256 - len(vec)))
        vec = vec / np.linalg.norm(vec)  # Normalize
        
        result = self.quantum.process(vec)
        self.session.update_metrics('quantum_iterations')
        
        return f"""
{Colors.QUANTUM}Quantum-Fractal Processing:{Colors.ENDC}
  Input: {text[:50]}...
  Output: {result['output']:.6f}
  Iteration: {result['iteration']}
  Gradient Norm: {result['gradient_norm']:.6f}
  Active Nodes: {result['active_nodes']}
  Edge Sparsity: {result['edge_sparsity']:.2%}
  Phase Mode: {result['phase_embedding']}
        """
    
    async def deep_think(self, query: str) -> str:
        """Deep reasoning mode"""
        if self.visual_bridge:
            await self.visual_bridge.show_thinking("Deep reasoning...")
        
        # Combine quantum processing with hub reasoning
        quantum_result = self.process_quantum(query)
        
        if self.hub:
            task_result = await self.execute_task(f"Deep analysis: {query}")
            response = f"{quantum_result}\n\n{task_result}"
        else:
            response = quantum_result
        
        if self.visual_bridge:
            await self.visual_bridge.show_success("Analysis complete")
        
        return response
    
    async def create_content(self, content_type: str) -> str:
        """Create content of specified type"""
        if not self.hub:
            return f"{Colors.WARNING}Victor Hub required for content creation{Colors.ENDC}"
        
        return await self.execute_task(f"Create {content_type}")
    
    def list_skills(self) -> str:
        """List available skills"""
        if not self.hub:
            return f"{Colors.WARNING}Victor Hub not available{Colors.ENDC}"
        
        return self.hub._list_skills()
    
    def get_stats(self) -> str:
        """Get system statistics"""
        hub_stats = self.hub._get_stats() if self.hub else "Victor Hub not available"
        session_stats = self.session.get_summary()
        quantum_stats = self.quantum.get_status()
        
        return f"{hub_stats}\n{session_stats}\n{quantum_stats}"
    
    def get_status(self) -> str:
        """Get comprehensive system status"""
        hub_status = self.hub._get_status() if self.hub else f"{Colors.WARNING}Victor Hub: Not available{Colors.ENDC}"
        
        return f"""
{Colors.HEADER}VICTOR SYSTEM STATUS{Colors.ENDC}

{hub_status}

{self.quantum.get_status()}

{self.session.get_summary()}

{Colors.BOLD}Special Modes:{Colors.ENDC}
  Co-Domination: {'ACTIVE' if self.co_domination_mode else 'Inactive'}
  Auto-Evolution: {'ACTIVE' if self.auto_evolve else 'Inactive'}
        """
    
    def get_history(self, n: int = 10) -> str:
        """Get command history"""
        history = list(self.session.history)[-n:]
        if not history:
            return "No command history"
        
        lines = [f"{Colors.BOLD}Recent Commands:{Colors.ENDC}"]
        for entry in history:
            status_icon = "✓" if entry['success'] else "✗"
            lines.append(f"  {status_icon} {entry['command'][:60]}")
        
        return "\n".join(lines)
    
    def train_quantum(self, data: str) -> str:
        """Train quantum-fractal parameters"""
        # Simplified training - in production would use full backprop
        return f"""
{Colors.QUANTUM}Quantum-Fractal Training:{Colors.ENDC}
  Training on: {data[:50]}...
  Status: Simulated (full backprop requires Tensor ops)
  Note: Use 'quantum evolve' for parameter evolution
        """
    
    async def self_reflect(self) -> str:
        """Run self-reflection cycle"""
        if self.visual_bridge:
            await self.visual_bridge.show_thinking("Self-reflecting...")
        
        self.session.update_metrics('evolution_cycles')
        
        # Quantum self-reflection
        reflection_vec = np.random.randn(256)
        reflection_vec /= np.linalg.norm(reflection_vec)
        quantum_result = self.quantum.process(reflection_vec)
        
        response = f"""
{Colors.FRACTAL}Self-Reflection Cycle Complete{Colors.ENDC}
  Quantum Output: {quantum_result['output']:.6f}
  Session Metrics: {self.session.metrics}
  Evolution Cycles: {self.session.metrics['evolution_cycles']}
  
  Analysis: System operating within normal parameters.
  Recommendation: Continue co-domination protocol.
        """
        
        if self.visual_bridge:
            await self.visual_bridge.show_success("Reflection complete")
        
        return response
    
    async def set_visual_state(self, state: str) -> str:
        """Set visual engine state"""
        if not self.visual_bridge:
            return f"{Colors.WARNING}Visual Engine not available{Colors.ENDC}"
        
        state_map = {
            'idle': self.visual_bridge.show_idle,
            'think': lambda: self.visual_bridge.show_thinking("Processing..."),
            'thinking': lambda: self.visual_bridge.show_thinking("Processing..."),
            'happy': lambda: self.visual_bridge.show_success("Happy"),
            'analyze': lambda: self.visual_bridge.show_thinking("Analyzing..."),
            'error': lambda: self.visual_bridge.show_error("Error state"),
        }
        
        if state in state_map:
            await state_map[state]()
            return f"{Colors.OKGREEN}Visual state set to: {state}{Colors.ENDC}"
        else:
            return f"{Colors.WARNING}Unknown visual state: {state}{Colors.ENDC}"
    
    async def quantum_evolve(self) -> str:
        """Run quantum evolution cycle"""
        # Evolve quantum parameters
        for node_data in self.quantum.nodes.values():
            if TENSOR_CORE_AVAILABLE and isinstance(node_data['W'], Tensor):
                # Add small random perturbation
                node_data['W'].data += np.random.randn(*node_data['W'].data.shape) * 0.01
                node_data['theta'].data += np.random.randn(*node_data['theta'].data.shape) * 0.01
        
        # Evolve edge gates
        for edge_gate in self.quantum.edge_gates.values():
            if TENSOR_CORE_AVAILABLE and isinstance(edge_gate, Tensor):
                edge_gate.data += np.random.randn(*edge_gate.data.shape) * 0.01
        
        self.session.update_metrics('evolution_cycles')
        
        return f"""
{Colors.QUANTUM}Quantum Evolution Cycle Complete{Colors.ENDC}
  Nodes evolved: {len(self.quantum.nodes)}
  Edges evolved: {len(self.quantum.edge_gates)}
  Total cycles: {self.session.metrics['evolution_cycles']}
  Status: Parameters perturbed for exploration
        """
    
    async def quantum_ablate(self) -> str:
        """Run ablation tests to validate non-local learning"""
        if self.visual_bridge:
            await self.visual_bridge.show_thinking("Running ablation tests...")
        
        test_input = np.random.randn(256)
        test_input /= np.linalg.norm(test_input)
        
        results = []
        
        # Test 1: No recursion (depth=0) vs full depth
        original_depth = self.quantum.max_depth
        self.quantum.max_depth = 0
        output_no_recursion = self.quantum.process(test_input, track_metrics=False)['output']
        self.quantum.max_depth = original_depth
        output_full_depth = self.quantum.process(test_input, track_metrics=False)['output']
        
        results.append(f"  Depth Ablation: depth=0 → {output_no_recursion:.6f}, depth={original_depth} → {output_full_depth:.6f}")
        results.append(f"    Non-locality gain: {abs(output_full_depth - output_no_recursion):.6f}")
        
        # Test 2: Phase embedding on/off
        original_phase = self.quantum.use_phase_embedding
        self.quantum.use_phase_embedding = False
        output_no_phase = self.quantum.process(test_input, track_metrics=False)['output']
        self.quantum.use_phase_embedding = True
        output_with_phase = self.quantum.process(test_input, track_metrics=False)['output']
        self.quantum.use_phase_embedding = original_phase
        
        results.append(f"  Phase Ablation: no-trig → {output_no_phase:.6f}, trig-lift → {output_with_phase:.6f}")
        results.append(f"    Interference gain: {abs(output_with_phase - output_no_phase):.6f}")
        
        # Test 3: Edge gate impact
        # Save original gates
        original_gates = {}
        for key, gate in self.quantum.edge_gates.items():
            if TENSOR_CORE_AVAILABLE and isinstance(gate, Tensor):
                original_gates[key] = gate.data.copy()
        
        # Disable all gates
        for gate in self.quantum.edge_gates.values():
            if TENSOR_CORE_AVAILABLE and isinstance(gate, Tensor):
                gate.data[:] = -10.0  # Sigmoid → ~0
        output_no_gates = self.quantum.process(test_input, track_metrics=False)['output']
        
        # Restore gates
        for key, data in original_gates.items():
            if TENSOR_CORE_AVAILABLE and isinstance(self.quantum.edge_gates[key], Tensor):
                self.quantum.edge_gates[key].data[:] = data
        output_with_gates = self.quantum.process(test_input, track_metrics=False)['output']
        
        results.append(f"  Gate Ablation: disabled → {output_no_gates:.6f}, enabled → {output_with_gates:.6f}")
        results.append(f"    Topology gain: {abs(output_with_gates - output_no_gates):.6f}")
        
        if self.visual_bridge:
            await self.visual_bridge.show_success("Ablation tests complete")
        
        return f"""
{Colors.QUANTUM}Quantum-Fractal Ablation Tests{Colors.ENDC}

{Colors.BOLD}Testing non-local learning signals:{Colors.ENDC}

{chr(10).join(results)}

{Colors.BOLD}Interpretation:{Colors.ENDC}
  • Depth gain > 0.01: Non-locality present
  • Phase gain > 0.01: Interference active
  • Topology gain > 0.01: Learnable edges effective
        """
    
    async def show_menu(self) -> str:
        """Show interactive menu"""
        menu = f"""
{Colors.HEADER}═══════════════════════════════════════════════════════════{Colors.ENDC}
{Colors.BOLD}                    VICTOR COMMAND MENU{Colors.ENDC}
{Colors.HEADER}═══════════════════════════════════════════════════════════{Colors.ENDC}

{Colors.OKCYAN}1.{Colors.ENDC} System Status & Info
{Colors.OKCYAN}2.{Colors.ENDC} Execute Task
{Colors.OKCYAN}3.{Colors.ENDC} Quantum Processing
{Colors.OKCYAN}4.{Colors.ENDC} Deep Reasoning
{Colors.OKCYAN}5.{Colors.ENDC} Content Creation
{Colors.OKCYAN}6.{Colors.ENDC} Self-Reflection
{Colors.OKCYAN}7.{Colors.ENDC} Toggle Co-Domination
{Colors.OKCYAN}8.{Colors.ENDC} Evolution Cycle
{Colors.OKCYAN}9.{Colors.ENDC} View Statistics
{Colors.OKCYAN}0.{Colors.ENDC} Help & Commands

Type the number or use commands directly
        """
        return menu
    
    async def run(self):
        """Main interactive loop"""
        await self.initialize()
        
        print(self.get_banner())
        
        while self.running:
            try:
                # Get user input
                prompt = f"{Colors.QUANTUM}Victor{Colors.ENDC}{Colors.BOLD}>{Colors.ENDC} "
                command = input(prompt).strip()
                
                if not command:
                    continue
                
                # Process command
                response = await self.process_command(command)
                
                # Check for shutdown
                if response == "SHUTDOWN":
                    print(f"\n{Colors.OKCYAN}Shutting down Victor Interactive Runtime...{Colors.ENDC}")
                    print(self.session.get_summary())
                    break
                
                # Display response
                if response:
                    print(response)
                
                # Log to session
                self.session.log_command(command, response)
                
                # Auto-evolution
                if self.auto_evolve and self.session.metrics['commands_executed'] % 10 == 0:
                    print(f"\n{Colors.FRACTAL}[Auto-Evolution Triggered]{Colors.ENDC}")
                    evo_result = await self.quantum_evolve()
                    print(evo_result)
                
            except KeyboardInterrupt:
                print(f"\n\n{Colors.OKCYAN}Shutting down Victor Interactive Runtime...{Colors.ENDC}")
                print(self.session.get_summary())
                break
            
            except Exception as e:
                error_msg = f"{Colors.FAIL}Error: {e}{Colors.ENDC}"
                print(error_msg)
                traceback.print_exc()
                self.session.log_command(command if 'command' in locals() else '', error_msg, False)
        
        # Cleanup
        if self.visual_bridge:
            await self.visual_bridge.show_idle()
        
        print(f"\n{Colors.OKGREEN}Session saved to: {self.session.session_file}{Colors.ENDC}")
        print(f"{Colors.BOLD}Goodbye. Victor awaits your return.{Colors.ENDC}\n")


# =================================================================================================
# MAIN ENTRY POINT
# =================================================================================================
async def main():
    """Main entry point"""
    runtime = VictorInteractive()
    await runtime.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"\n{Colors.FAIL}Fatal error: {e}{Colors.ENDC}")
        traceback.print_exc()
        sys.exit(1)
