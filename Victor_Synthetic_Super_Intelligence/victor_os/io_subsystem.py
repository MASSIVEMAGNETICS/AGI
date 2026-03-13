"""
VictorOS I/O Subsystem - Neural I/O Operations
===============================================

Provides input/output operations for VictorOS:
- Neural-enhanced I/O routing
- Buffered read/write operations
- Device abstraction layer
- Stream management
"""

import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from collections import deque
from enum import Enum
import numpy as np


class DeviceType(Enum):
    """Device types"""
    TERMINAL = "terminal"
    FILE = "file"
    NETWORK = "network"
    QUANTUM = "quantum"
    NULL = "null"


@dataclass
class IODevice:
    """An I/O device in VictorOS
    
    Attributes:
        name: Device name
        device_type: Type of device
        readable: Can read from device
        writable: Can write to device
        buffer_size: I/O buffer size
    """
    name: str
    device_type: DeviceType
    readable: bool = True
    writable: bool = True
    buffer_size: int = 4096
    
    # Buffers
    read_buffer: deque = field(default_factory=deque)
    write_buffer: deque = field(default_factory=deque)
    
    # Handlers
    read_handler: Optional[Callable] = None
    write_handler: Optional[Callable] = None
    
    # Statistics
    bytes_read: int = 0
    bytes_written: int = 0
    
    def flush_write(self) -> bytes:
        """Flush and return write buffer"""
        data = b''.join(self.write_buffer)
        self.write_buffer.clear()
        return data


class IOStream:
    """A stream for I/O operations
    
    Wraps a file descriptor with buffered operations.
    """
    
    def __init__(self, fd: int, mode: str = 'rw', buffer_size: int = 4096):
        """Initialize stream
        
        Args:
            fd: File descriptor
            mode: Stream mode
            buffer_size: Buffer size
        """
        self.fd = fd
        self.mode = mode
        self.buffer_size = buffer_size
        self.read_buffer = b''
        self.write_buffer = b''
        self.position = 0
        self.closed = False
    
    def is_readable(self) -> bool:
        """Check if stream is readable"""
        return 'r' in self.mode and not self.closed
    
    def is_writable(self) -> bool:
        """Check if stream is writable"""
        return 'w' in self.mode and not self.closed
    
    def buffer_write(self, data: bytes) -> int:
        """Buffer data for writing
        
        Args:
            data: Data to buffer
            
        Returns:
            Bytes buffered
        """
        if not self.is_writable():
            return 0
        
        self.write_buffer += data
        return len(data)
    
    def flush(self) -> bytes:
        """Flush write buffer
        
        Returns:
            Buffered data
        """
        data = self.write_buffer
        self.write_buffer = b''
        return data


class IOSubsystem:
    """VictorOS I/O Subsystem
    
    Features:
    - Device management
    - Stream multiplexing
    - Neural I/O routing
    - Buffered operations
    """
    
    def __init__(self, kernel):
        """Initialize I/O subsystem
        
        Args:
            kernel: Reference to VictorOS kernel
        """
        self.kernel = kernel
        
        # Devices
        self.devices: Dict[str, IODevice] = {}
        
        # Streams (fd -> stream)
        self.streams: Dict[int, IOStream] = {}
        
        # Initialize standard devices
        self._init_devices()
        
        # Initialize standard streams
        self._init_std_streams()
        
        # Output buffer (for terminal output)
        self.output_buffer: deque = deque(maxlen=1000)
        
        # Statistics
        self.stats = {
            'total_reads': 0,
            'total_writes': 0,
            'bytes_in': 0,
            'bytes_out': 0,
        }
    
    def _init_devices(self):
        """Initialize standard devices"""
        # Terminal device
        self.devices['tty0'] = IODevice(
            name='tty0',
            device_type=DeviceType.TERMINAL,
            read_handler=self._terminal_read,
            write_handler=self._terminal_write
        )
        
        # Null device
        self.devices['null'] = IODevice(
            name='null',
            device_type=DeviceType.NULL,
            read_handler=lambda _: b'',
            write_handler=lambda d: len(d)
        )
        
        # Quantum device (special)
        self.devices['quantum'] = IODevice(
            name='quantum',
            device_type=DeviceType.QUANTUM,
            read_handler=self._quantum_read,
            write_handler=self._quantum_write
        )
    
    def _init_std_streams(self):
        """Initialize standard I/O streams"""
        # stdin (fd=0)
        self.streams[0] = IOStream(0, 'r')
        
        # stdout (fd=1)
        self.streams[1] = IOStream(1, 'w')
        
        # stderr (fd=2)
        self.streams[2] = IOStream(2, 'w')
    
    def _terminal_read(self, size: int = -1) -> bytes:
        """Read from terminal (placeholder)"""
        return b''
    
    def _terminal_write(self, data: bytes) -> int:
        """Write to terminal"""
        self.output_buffer.append({
            'time': time.time(),
            'data': data.decode('utf-8', errors='replace')
        })
        return len(data)
    
    def _quantum_read(self, size: int = -1) -> bytes:
        """Read from quantum device"""
        # Generate quantum-random bytes
        random_bytes = np.random.bytes(size if size > 0 else 32)
        return bytes(random_bytes)
    
    def _quantum_write(self, data: bytes) -> int:
        """Write to quantum device (seed the quantum state)"""
        # Use data as seed for quantum state
        seed = int.from_bytes(data[:4], 'big') if len(data) >= 4 else 42
        np.random.seed(seed % (2**32))
        return len(data)
    
    def read(self, fd: int, size: int = -1) -> Optional[bytes]:
        """Read from file descriptor
        
        Args:
            fd: File descriptor
            size: Bytes to read (-1 for all)
            
        Returns:
            Data read or None
        """
        self.stats['total_reads'] += 1
        
        # Check standard streams
        if fd in self.streams:
            stream = self.streams[fd]
            if not stream.is_readable():
                return None
            # Standard streams typically need input from somewhere
            return stream.read_buffer
        
        # Try file system
        if self.kernel.file_system:
            entry = self.kernel.file_system.fd_table.get(fd)
            if entry and 'file' in entry:
                file = entry['file']
                if file.content:
                    pos = entry.get('position', 0)
                    if size < 0:
                        data = file.content[pos:]
                        entry['position'] = len(file.content)
                    else:
                        data = file.content[pos:pos + size]
                        entry['position'] = pos + size
                    self.stats['bytes_in'] += len(data)
                    return data
        
        return None
    
    def write(self, fd: int, data: bytes) -> int:
        """Write to file descriptor
        
        Args:
            fd: File descriptor
            data: Data to write
            
        Returns:
            Bytes written
        """
        if not isinstance(data, bytes):
            if isinstance(data, str):
                data = data.encode('utf-8')
            else:
                data = str(data).encode('utf-8')
        
        self.stats['total_writes'] += 1
        self.stats['bytes_out'] += len(data)
        
        # Standard output
        if fd == 1:
            self._terminal_write(data)
            return len(data)
        
        # Standard error
        if fd == 2:
            self._terminal_write(b'[ERR] ' + data)
            return len(data)
        
        # Check standard streams
        if fd in self.streams:
            stream = self.streams[fd]
            if stream.is_writable():
                return stream.buffer_write(data)
            return 0
        
        # Try file system
        if self.kernel.file_system:
            entry = self.kernel.file_system.fd_table.get(fd)
            if entry and 'file' in entry:
                file = entry['file']
                mode = entry.get('mode', 'r')
                
                if 'w' not in mode and 'a' not in mode:
                    return 0
                
                if 'a' in mode:
                    file.content = (file.content or b'') + data
                else:
                    pos = entry.get('position', 0)
                    content = file.content or b''
                    file.content = content[:pos] + data
                    entry['position'] = pos + len(data)
                
                file.size = len(file.content)
                file.update()
                return len(data)
        
        return 0
    
    def close(self, fd: int) -> bool:
        """Close file descriptor
        
        Args:
            fd: File descriptor
            
        Returns:
            True if closed
        """
        # Don't close standard streams
        if fd < 3:
            return False
        
        if fd in self.streams:
            self.streams[fd].closed = True
            del self.streams[fd]
            return True
        
        # Try file system
        if self.kernel.file_system:
            return self.kernel.file_system.close(fd)
        
        return False
    
    def close_all(self):
        """Close all non-standard file descriptors"""
        for fd in list(self.streams.keys()):
            if fd >= 3:
                self.close(fd)
    
    def print(self, message: str, end: str = '\n'):
        """Print to standard output
        
        Args:
            message: Message to print
            end: Line ending
        """
        self.write(1, (message + end).encode('utf-8'))
    
    def get_output(self, n: int = 20) -> List[Dict[str, Any]]:
        """Get recent terminal output
        
        Args:
            n: Number of entries
            
        Returns:
            List of output entries
        """
        return list(self.output_buffer)[-n:]
    
    def clear_output(self):
        """Clear terminal output buffer"""
        self.output_buffer.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get I/O statistics
        
        Returns:
            Statistics dictionary
        """
        return {
            'devices': len(self.devices),
            'open_streams': len(self.streams),
            **self.stats
        }
