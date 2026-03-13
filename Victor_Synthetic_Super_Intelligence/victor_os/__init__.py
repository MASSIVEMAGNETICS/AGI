"""
Victor Operating System (VictorOS)
==================================

A novel operating system built on the VictorSSI runtime foundation.

VictorOS provides:
- Quantum-enhanced process management
- Fractal memory architecture
- Neural I/O subsystem
- Sovereign file system
- Interactive shell interface

This is not a traditional OS - it's a cognitive operating environment
that leverages the Victor Synthetic Super Intelligence runtime.
"""

from victor_os.kernel import VictorKernel
from victor_os.process_manager import ProcessManager, VictorProcess
from victor_os.memory_manager import MemoryManager, MemoryBlock
from victor_os.file_system import VictorFileSystem, VictorFile
from victor_os.shell import VictorShell
from victor_os.io_subsystem import IOSubsystem

__version__ = "1.0.0-QUANTUM"
__all__ = [
    'VictorKernel',
    'ProcessManager', 
    'VictorProcess',
    'MemoryManager',
    'MemoryBlock',
    'VictorFileSystem',
    'VictorFile',
    'VictorShell',
    'IOSubsystem'
]
