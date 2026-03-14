"""
VictorOS Process Manager - Quantum-Enhanced Process Management
==============================================================

Manages the lifecycle of processes in VictorOS:
- Process creation with quantum initialization
- Process states: CREATED, READY, RUNNING, WAITING, TERMINATED
- Process scheduling coordination with the kernel scheduler
- Resource tracking per process
"""

import time
import uuid
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import numpy as np


class ProcessState(Enum):
    """Process lifecycle states"""
    CREATED = "created"
    READY = "ready"
    RUNNING = "running"
    WAITING = "waiting"
    BLOCKED = "blocked"
    TERMINATED = "terminated"


@dataclass
class VictorProcess:
    """A process in the VictorOS system
    
    Each process has:
    - Unique PID and name
    - Quantum-enhanced priority system
    - Resource tracking (memory, CPU ticks)
    - Optional task function for execution
    """
    pid: int
    name: str
    state: ProcessState = ProcessState.CREATED
    priority: int = 5  # 1-10 scale
    parent_pid: Optional[int] = None
    
    # Quantum properties
    phase: float = field(default_factory=lambda: np.random.uniform(0, 2 * np.pi))
    entanglement_group: Optional[int] = None
    
    # Resource tracking
    memory_allocated: int = 0
    cpu_ticks: int = 0
    wait_time: float = 0.0
    
    # Timing
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    ended_at: Optional[float] = None
    
    # Task
    task: Optional[Callable] = None
    task_args: tuple = field(default_factory=tuple)
    task_kwargs: Dict = field(default_factory=dict)
    result: Any = None
    error: Optional[str] = None
    
    # Context (like environment variables)
    context: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.context is None:
            self.context = {}
    
    def is_alive(self) -> bool:
        """Check if process is still alive"""
        return self.state not in [ProcessState.TERMINATED]
    
    def get_runtime(self) -> float:
        """Get process runtime in seconds"""
        if self.started_at is None:
            return 0.0
        end = self.ended_at or time.time()
        return end - self.started_at
    
    def get_info(self) -> Dict[str, Any]:
        """Get process information"""
        return {
            'pid': self.pid,
            'name': self.name,
            'state': self.state.value,
            'priority': self.priority,
            'parent_pid': self.parent_pid,
            'phase': self.phase,
            'memory': self.memory_allocated,
            'cpu_ticks': self.cpu_ticks,
            'runtime': self.get_runtime(),
            'created_at': self.created_at,
        }


class ProcessManager:
    """Manages processes in VictorOS
    
    Features:
    - Quantum-enhanced process creation
    - Process lifecycle management
    - Resource allocation tracking
    - Entanglement group management
    """
    
    def __init__(self, kernel):
        """Initialize process manager
        
        Args:
            kernel: Reference to the VictorOS kernel
        """
        self.kernel = kernel
        self.processes: Dict[int, VictorProcess] = {}
        self.next_pid = 1
        self.entanglement_groups: Dict[int, List[int]] = {}
        self.next_entanglement_group = 1
        
        # Create init process (PID 0)
        self._create_init_process()
    
    def _create_init_process(self):
        """Create the init process (PID 0)
        
        The init process is the first process in the system and 
        serves as the ancestor of all other processes.
        """
        init_proc = VictorProcess(
            pid=0,
            name="init",
            state=ProcessState.RUNNING,
            priority=10,  # Highest priority
            phase=0.0,  # Stable phase
        )
        init_proc.context['is_init'] = True
        self.processes[0] = init_proc
    
    def spawn(self, name: str, task: Optional[Callable] = None,
              priority: int = 5, parent_pid: Optional[int] = None,
              entangle_with: Optional[int] = None,
              context: Optional[Dict] = None,
              args: tuple = (), kwargs: Optional[Dict] = None) -> int:
        """Spawn a new process
        
        Args:
            name: Process name
            task: Optional callable to execute
            priority: Process priority (1-10)
            parent_pid: Parent process PID
            entangle_with: PID to entangle with (share quantum state)
            context: Process context/environment
            args: Task arguments
            kwargs: Task keyword arguments
            
        Returns:
            PID of new process
        """
        pid = self.next_pid
        self.next_pid += 1
        
        # Determine entanglement
        entanglement_group = None
        if entangle_with is not None and entangle_with in self.processes:
            parent = self.processes[entangle_with]
            entanglement_group = parent.entanglement_group
            if entanglement_group is None:
                # Create new entanglement group
                entanglement_group = self.next_entanglement_group
                self.next_entanglement_group += 1
                self.entanglement_groups[entanglement_group] = [entangle_with]
                parent.entanglement_group = entanglement_group
            self.entanglement_groups[entanglement_group].append(pid)
        
        # Calculate initial phase
        if entanglement_group is not None and entangle_with in self.processes:
            # Entangled processes share phase
            base_phase = self.processes[entangle_with].phase
            phase = base_phase + np.random.randn() * 0.1  # Small variation
        else:
            phase = np.random.uniform(0, 2 * np.pi)
        
        process = VictorProcess(
            pid=pid,
            name=name,
            state=ProcessState.CREATED,
            priority=priority,
            parent_pid=parent_pid or 0,
            phase=phase,
            entanglement_group=entanglement_group,
            task=task,
            task_args=args,
            task_kwargs=kwargs or {},
            context=context or {}
        )
        
        self.processes[pid] = process
        
        # Add to scheduler
        process.state = ProcessState.READY
        if self.kernel.scheduler:
            self.kernel.scheduler.add_process(process)
        
        return pid
    
    def kill(self, pid: int, force: bool = False) -> bool:
        """Kill a process
        
        Args:
            pid: Process ID to kill
            force: Force kill even if protected
            
        Returns:
            True if killed successfully
        """
        if pid == 0 and not force:
            # Cannot kill init process
            return False
        
        if pid not in self.processes:
            return False
        
        process = self.processes[pid]
        
        # Update state
        process.state = ProcessState.TERMINATED
        process.ended_at = time.time()
        
        # Free resources (if memory manager available)
        if process.memory_allocated > 0 and self.kernel.memory_manager:
            # Memory should be freed by the memory manager
            pass
        
        # Remove from entanglement group
        if process.entanglement_group is not None:
            group = self.entanglement_groups.get(process.entanglement_group, [])
            if pid in group:
                group.remove(pid)
            if not group:
                del self.entanglement_groups[process.entanglement_group]
        
        # Update kernel metrics
        self.kernel.metrics.processes_completed += 1
        
        return True
    
    def execute_tick(self, process: VictorProcess):
        """Execute one tick for a process
        
        Args:
            process: Process to execute
        """
        if process.state != ProcessState.READY:
            return
        
        process.state = ProcessState.RUNNING
        if process.started_at is None:
            process.started_at = time.time()
        
        process.cpu_ticks += 1
        
        # Execute task if present
        if process.task is not None:
            try:
                process.result = process.task(*process.task_args, **process.task_kwargs)
                process.state = ProcessState.TERMINATED
                process.ended_at = time.time()
                self.kernel.metrics.processes_completed += 1
            except Exception as e:
                process.error = str(e)
                process.state = ProcessState.TERMINATED
                process.ended_at = time.time()
        else:
            # No task - just mark as ready for next tick
            process.state = ProcessState.READY
            if self.kernel.scheduler:
                self.kernel.scheduler.add_process(process)
    
    def get_process(self, pid: int) -> Optional[VictorProcess]:
        """Get process by PID
        
        Args:
            pid: Process ID
            
        Returns:
            Process or None if not found
        """
        return self.processes.get(pid)
    
    def list_processes(self, include_terminated: bool = False) -> List[Dict[str, Any]]:
        """List all processes
        
        Args:
            include_terminated: Include terminated processes
            
        Returns:
            List of process info dictionaries
        """
        result = []
        for proc in self.processes.values():
            if not include_terminated and proc.state == ProcessState.TERMINATED:
                continue
            result.append(proc.get_info())
        return result
    
    def terminate_all(self, exclude_init: bool = True):
        """Terminate all processes
        
        Args:
            exclude_init: Don't kill init process
        """
        for pid in list(self.processes.keys()):
            if exclude_init and pid == 0:
                continue
            self.kill(pid, force=True)
    
    def wait(self, pid: int, timeout: Optional[float] = None) -> Optional[Any]:
        """Wait for process to complete
        
        Args:
            pid: Process ID to wait for
            timeout: Maximum wait time
            
        Returns:
            Process result or None
        """
        if pid not in self.processes:
            return None
        
        process = self.processes[pid]
        start = time.time()
        
        while process.state not in [ProcessState.TERMINATED]:
            if timeout and (time.time() - start) > timeout:
                return None
            time.sleep(0.01)
        
        return process.result
    
    def get_stats(self) -> Dict[str, Any]:
        """Get process manager statistics
        
        Returns:
            Statistics dictionary
        """
        alive = sum(1 for p in self.processes.values() if p.is_alive())
        terminated = len(self.processes) - alive
        
        return {
            'total_processes': len(self.processes),
            'alive': alive,
            'terminated': terminated,
            'entanglement_groups': len(self.entanglement_groups),
            'next_pid': self.next_pid
        }
