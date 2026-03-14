"""
VictorOS Memory Manager - Fractal Memory Architecture
=====================================================

Implements fractal memory management for VictorOS:
- Hierarchical memory blocks with quantum addressing
- Golden ratio-based allocation strategy
- Memory compression using fractal patterns
- Garbage collection with phase-aware cleanup
"""

import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import numpy as np


@dataclass
class MemoryBlock:
    """A memory block in the fractal memory system
    
    Attributes:
        address: Starting address of block
        size: Size in memory units
        allocated: Whether block is allocated
        owner_pid: PID of owning process
        data: Stored data
        phase: Quantum phase for the block
        level: Fractal hierarchy level
    """
    address: int
    size: int
    allocated: bool = False
    owner_pid: Optional[int] = None
    data: Any = None
    phase: float = 0.0
    level: int = 0
    created_at: float = field(default_factory=time.time)
    accessed_at: float = field(default_factory=time.time)
    
    def touch(self):
        """Update last accessed time"""
        self.accessed_at = time.time()
    
    def get_info(self) -> Dict[str, Any]:
        """Get block information"""
        return {
            'address': self.address,
            'size': self.size,
            'allocated': self.allocated,
            'owner_pid': self.owner_pid,
            'phase': self.phase,
            'level': self.level,
            'age': time.time() - self.created_at,
        }


class FractalAllocator:
    """Fractal-based memory allocator
    
    Uses golden ratio partitioning for optimal memory layout:
    - Larger blocks at lower fractal levels
    - Smaller blocks at higher levels (more granular)
    - Phase-aware allocation for entangled processes
    """
    
    PHI = (1 + np.sqrt(5)) / 2  # Golden ratio
    
    def __init__(self, total_size: int, max_levels: int = 5):
        """Initialize fractal allocator
        
        Args:
            total_size: Total memory size
            max_levels: Maximum fractal depth
        """
        self.total_size = total_size
        self.max_levels = max_levels
        
        # Compute block sizes for each level using golden ratio
        self.level_sizes = []
        current_size = total_size
        for level in range(max_levels):
            self.level_sizes.append(int(current_size))
            current_size = int(current_size / self.PHI)
        
    def suggest_level(self, requested_size: int) -> int:
        """Suggest appropriate fractal level for allocation
        
        Args:
            requested_size: Size requested
            
        Returns:
            Suggested fractal level
        """
        for level, size in enumerate(self.level_sizes):
            if size >= requested_size:
                # Check if next level would be too small
                if level < len(self.level_sizes) - 1:
                    if self.level_sizes[level + 1] < requested_size:
                        return level
        return len(self.level_sizes) - 1


class MemoryManager:
    """VictorOS Memory Manager
    
    Features:
    - Fractal hierarchy for efficient allocation
    - Phase-based memory grouping
    - Automatic garbage collection
    - Memory statistics tracking
    """
    
    def __init__(self, total_size: int = 1024 * 1024, max_levels: int = 5):
        """Initialize memory manager
        
        Args:
            total_size: Total memory size in units
            max_levels: Maximum fractal hierarchy levels
        """
        self.total_size = total_size
        self.used_size = 0
        self.max_levels = max_levels
        
        # Memory blocks indexed by address
        self.blocks: Dict[int, MemoryBlock] = {}
        
        # Free list per level
        self.free_lists: List[List[int]] = [[] for _ in range(max_levels)]
        
        # Initialize with one large free block
        initial_block = MemoryBlock(
            address=0,
            size=total_size,
            allocated=False,
            level=0
        )
        self.blocks[0] = initial_block
        self.free_lists[0].append(0)
        
        # Fractal allocator helper
        self.fractal = FractalAllocator(total_size, max_levels)
        
        # Statistics
        self.allocations = 0
        self.frees = 0
        self.gc_runs = 0
    
    def allocate(self, size: int, owner_pid: Optional[int] = None,
                 phase: Optional[float] = None) -> Optional[MemoryBlock]:
        """Allocate memory block
        
        Args:
            size: Size to allocate
            owner_pid: Owning process PID
            phase: Quantum phase (for entangled allocation)
            
        Returns:
            MemoryBlock if successful, None otherwise
        """
        if size <= 0:
            return None
        
        if self.used_size + size > self.total_size:
            # Try garbage collection
            self._gc()
            if self.used_size + size > self.total_size:
                return None
        
        # Find best level for this allocation
        level = self.fractal.suggest_level(size)
        
        # Find suitable free block
        block = self._find_free_block(size, level)
        if block is None:
            # Try lower levels (larger blocks)
            for l in range(level - 1, -1, -1):
                block = self._find_free_block(size, l)
                if block:
                    break
        
        if block is None:
            return None
        
        # Split block if necessary
        if block.size > size * 2:
            self._split_block(block, size)
        
        # Allocate the block
        block.allocated = True
        block.owner_pid = owner_pid
        block.phase = phase if phase is not None else np.random.uniform(0, 2 * np.pi)
        block.touch()
        
        self.used_size += block.size
        self.allocations += 1
        
        # Remove from free list
        if block.address in self.free_lists[block.level]:
            self.free_lists[block.level].remove(block.address)
        
        return block
    
    def _find_free_block(self, size: int, level: int) -> Optional[MemoryBlock]:
        """Find a free block at given level
        
        Args:
            size: Minimum size needed
            level: Fractal level to search
            
        Returns:
            Free block or None
        """
        if level >= len(self.free_lists):
            return None
        
        for addr in self.free_lists[level]:
            block = self.blocks.get(addr)
            if block and not block.allocated and block.size >= size:
                return block
        
        return None
    
    def _split_block(self, block: MemoryBlock, size: int):
        """Split a block into smaller pieces
        
        Args:
            block: Block to split
            size: Size for first piece
        """
        if block.size <= size:
            return
        
        # Create new block for remainder
        new_level = min(block.level + 1, self.max_levels - 1)
        remainder_size = block.size - size
        
        new_block = MemoryBlock(
            address=block.address + size,
            size=remainder_size,
            allocated=False,
            level=new_level
        )
        
        self.blocks[new_block.address] = new_block
        self.free_lists[new_level].append(new_block.address)
        
        # Resize original block
        block.size = size
    
    def free(self, address: int) -> int:
        """Free memory at address
        
        Args:
            address: Memory address to free
            
        Returns:
            Size freed, 0 if not found
        """
        block = self.blocks.get(address)
        if block is None or not block.allocated:
            return 0
        
        freed_size = block.size
        
        block.allocated = False
        block.owner_pid = None
        block.data = None
        
        self.used_size -= freed_size
        self.frees += 1
        
        # Add back to free list
        self.free_lists[block.level].append(address)
        
        # Try to merge with adjacent blocks
        self._try_merge(block)
        
        return freed_size
    
    def _try_merge(self, block: MemoryBlock):
        """Try to merge block with adjacent free blocks
        
        Args:
            block: Block to try merging
        """
        # Simple merge: look for adjacent block
        end_address = block.address + block.size
        
        for addr, other in list(self.blocks.items()):
            if addr == block.address:
                continue
            
            # Check if other block is right after this one
            if addr == end_address and not other.allocated:
                # Merge: extend block, remove other
                block.size += other.size
                block.level = min(block.level, other.level)
                
                if addr in self.free_lists[other.level]:
                    self.free_lists[other.level].remove(addr)
                del self.blocks[addr]
                
                # Update free list for this block
                for level_list in self.free_lists:
                    if block.address in level_list:
                        level_list.remove(block.address)
                self.free_lists[block.level].append(block.address)
                
                return
    
    def read(self, address: int) -> Any:
        """Read data from memory address
        
        Args:
            address: Memory address
            
        Returns:
            Data stored at address
        """
        block = self.blocks.get(address)
        if block and block.allocated:
            block.touch()
            return block.data
        return None
    
    def write(self, address: int, data: Any) -> bool:
        """Write data to memory address
        
        Args:
            address: Memory address
            data: Data to write
            
        Returns:
            True if successful
        """
        block = self.blocks.get(address)
        if block and block.allocated:
            block.data = data
            block.touch()
            return True
        return False
    
    def _gc(self):
        """Run garbage collection"""
        self.gc_runs += 1
        
        # Find and free old unused blocks (basic GC)
        now = time.time()
        for addr, block in list(self.blocks.items()):
            if block.allocated and block.data is None:
                # Block is allocated but has no data - free it
                if now - block.accessed_at > 60:  # Not accessed in 60s
                    self.free(addr)
    
    def cleanup(self):
        """Cleanup all memory"""
        for addr in list(self.blocks.keys()):
            self.free(addr)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics
        
        Returns:
            Statistics dictionary
        """
        allocated_blocks = sum(1 for b in self.blocks.values() if b.allocated)
        free_blocks = sum(1 for b in self.blocks.values() if not b.allocated)
        
        return {
            'total_size': self.total_size,
            'used_size': self.used_size,
            'free_size': self.total_size - self.used_size,
            'utilization': self.used_size / self.total_size if self.total_size > 0 else 0,
            'allocated_blocks': allocated_blocks,
            'free_blocks': free_blocks,
            'total_blocks': len(self.blocks),
            'allocations': self.allocations,
            'frees': self.frees,
            'gc_runs': self.gc_runs,
        }
    
    def list_blocks(self, allocated_only: bool = False) -> List[Dict[str, Any]]:
        """List memory blocks
        
        Args:
            allocated_only: Only show allocated blocks
            
        Returns:
            List of block info dictionaries
        """
        result = []
        for block in self.blocks.values():
            if allocated_only and not block.allocated:
                continue
            result.append(block.get_info())
        return result
