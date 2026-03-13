"""
VictorOS File System - Sovereign File System
=============================================

A neural-enhanced file system for VictorOS:
- Hierarchical directory structure
- Content-addressable storage
- Quantum tagging for file metadata
- Bloodline-protected files
"""

import time
import hashlib
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import json


class FileType(Enum):
    """File types in VictorFS"""
    REGULAR = "regular"
    DIRECTORY = "directory"
    LINK = "link"
    DEVICE = "device"
    QUANTUM = "quantum"  # Special quantum-entangled files


class FilePermission(Enum):
    """File permissions"""
    READ = "r"
    WRITE = "w"
    EXECUTE = "x"
    BLOODLINE = "b"  # Requires bloodline verification


@dataclass
class VictorFile:
    """A file in the VictorFS
    
    Attributes:
        name: File name
        path: Full path
        file_type: Type of file
        size: File size in bytes
        content: File content (for regular files)
        children: Child files (for directories)
        permissions: File permissions
        owner_pid: Owning process
        metadata: Additional metadata
    """
    name: str
    path: str
    file_type: FileType = FileType.REGULAR
    size: int = 0
    content: Optional[bytes] = None
    children: Dict[str, 'VictorFile'] = field(default_factory=dict)
    permissions: List[FilePermission] = field(default_factory=lambda: [FilePermission.READ, FilePermission.WRITE])
    owner_pid: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Timestamps
    created_at: float = field(default_factory=time.time)
    modified_at: float = field(default_factory=time.time)
    accessed_at: float = field(default_factory=time.time)
    
    # Quantum properties
    quantum_phase: float = 0.0
    content_hash: Optional[str] = None
    
    def is_directory(self) -> bool:
        """Check if file is a directory"""
        return self.file_type == FileType.DIRECTORY
    
    def touch(self):
        """Update access time"""
        self.accessed_at = time.time()
    
    def update(self):
        """Update modification time"""
        self.modified_at = time.time()
        self.touch()
    
    def compute_hash(self) -> str:
        """Compute content hash"""
        if self.content:
            self.content_hash = hashlib.sha256(self.content).hexdigest()
        else:
            self.content_hash = hashlib.sha256(self.name.encode()).hexdigest()
        return self.content_hash
    
    def get_info(self) -> Dict[str, Any]:
        """Get file information"""
        return {
            'name': self.name,
            'path': self.path,
            'type': self.file_type.value,
            'size': self.size,
            'permissions': [p.value for p in self.permissions],
            'owner_pid': self.owner_pid,
            'created_at': self.created_at,
            'modified_at': self.modified_at,
            'is_directory': self.is_directory(),
            'children_count': len(self.children) if self.is_directory() else 0,
            'quantum_phase': self.quantum_phase,
        }


class VictorFileSystem:
    """VictorOS File System
    
    Features:
    - Hierarchical directory structure
    - Content-addressable storage
    - Bloodline-protected files
    - Neural file search
    """
    
    def __init__(self, kernel):
        """Initialize file system
        
        Args:
            kernel: Reference to VictorOS kernel
        """
        self.kernel = kernel
        
        # Statistics (initialize early since _init_directories uses it)
        self.stats = {
            'files_created': 0,
            'files_deleted': 0,
            'bytes_written': 0,
            'bytes_read': 0,
        }
        
        # Content-addressable storage (hash -> content)
        self.cas: Dict[str, bytes] = {}
        
        # Root directory
        self.root = VictorFile(
            name="/",
            path="/",
            file_type=FileType.DIRECTORY,
            permissions=[FilePermission.READ, FilePermission.WRITE, FilePermission.EXECUTE]
        )
        
        # File descriptor table
        self.fd_table: Dict[int, Dict[str, Any]] = {}
        self.next_fd = 3  # 0=stdin, 1=stdout, 2=stderr
        
        # Initialize standard file descriptors
        self._init_std_fds()
        
        # Initialize directory structure
        self._init_directories()
    
    def _init_std_fds(self):
        """Initialize standard file descriptors"""
        self.fd_table[0] = {'type': 'stdin', 'mode': 'r', 'buffer': b''}
        self.fd_table[1] = {'type': 'stdout', 'mode': 'w', 'buffer': b''}
        self.fd_table[2] = {'type': 'stderr', 'mode': 'w', 'buffer': b''}
    
    def _init_directories(self):
        """Initialize standard directory structure"""
        dirs = [
            '/home',
            '/home/victor',
            '/etc',
            '/var',
            '/var/log',
            '/tmp',
            '/bin',
            '/proc',
            '/quantum',  # Special quantum storage
        ]
        
        for dir_path in dirs:
            self.mkdir(dir_path)
        
        # Create some initial files
        self._create_file('/etc/hostname', b'victor-os')
        self._create_file('/etc/bloodline', b'ACTIVE')
        self._create_file('/etc/version', b'1.0.0-QUANTUM')
    
    def _create_file(self, path: str, content: bytes):
        """Internal file creation"""
        parent_path = '/'.join(path.split('/')[:-1]) or '/'
        name = path.split('/')[-1]
        
        parent = self._resolve_path(parent_path)
        if parent and parent.is_directory():
            file = VictorFile(
                name=name,
                path=path,
                file_type=FileType.REGULAR,
                content=content,
                size=len(content)
            )
            file.compute_hash()
            parent.children[name] = file
            self.stats['files_created'] += 1
    
    def _resolve_path(self, path: str) -> Optional[VictorFile]:
        """Resolve path to file
        
        Args:
            path: File path
            
        Returns:
            VictorFile or None
        """
        if path == '/':
            return self.root
        
        # Normalize path
        parts = [p for p in path.split('/') if p]
        
        current = self.root
        for part in parts:
            if not current.is_directory():
                return None
            if part not in current.children:
                return None
            current = current.children[part]
        
        return current
    
    def mkdir(self, path: str, permissions: Optional[List[FilePermission]] = None) -> bool:
        """Create directory
        
        Args:
            path: Directory path
            permissions: Directory permissions
            
        Returns:
            True if created successfully
        """
        if self._resolve_path(path):
            return False  # Already exists
        
        # Get parent path
        parts = [p for p in path.split('/') if p]
        parent_path = '/' + '/'.join(parts[:-1]) if len(parts) > 1 else '/'
        name = parts[-1] if parts else ''
        
        if not name:
            return False
        
        parent = self._resolve_path(parent_path)
        if parent is None:
            # Create parent directories recursively
            self.mkdir(parent_path, permissions)
            parent = self._resolve_path(parent_path)
        
        if parent is None or not parent.is_directory():
            return False
        
        # Create directory
        new_dir = VictorFile(
            name=name,
            path=path,
            file_type=FileType.DIRECTORY,
            permissions=permissions or [FilePermission.READ, FilePermission.WRITE, FilePermission.EXECUTE]
        )
        
        parent.children[name] = new_dir
        self.stats['files_created'] += 1
        
        return True
    
    def open(self, path: str, mode: str = 'r') -> Optional[int]:
        """Open file and return file descriptor
        
        Args:
            path: File path
            mode: Open mode ('r', 'w', 'a', 'rw')
            
        Returns:
            File descriptor or None
        """
        file = self._resolve_path(path)
        
        # Create file if writing and doesn't exist
        if file is None and 'w' in mode:
            parent_path = '/'.join(path.split('/')[:-1]) or '/'
            name = path.split('/')[-1]
            parent = self._resolve_path(parent_path)
            
            if parent is None or not parent.is_directory():
                return None
            
            file = VictorFile(
                name=name,
                path=path,
                file_type=FileType.REGULAR
            )
            parent.children[name] = file
            self.stats['files_created'] += 1
        
        if file is None or file.is_directory():
            return None
        
        # Check permissions
        if 'r' in mode and FilePermission.READ not in file.permissions:
            return None
        if 'w' in mode and FilePermission.WRITE not in file.permissions:
            return None
        
        # Create file descriptor
        fd = self.next_fd
        self.next_fd += 1
        
        self.fd_table[fd] = {
            'path': path,
            'file': file,
            'mode': mode,
            'position': 0,
            'buffer': b''
        }
        
        file.touch()
        
        return fd
    
    def close(self, fd: int) -> bool:
        """Close file descriptor
        
        Args:
            fd: File descriptor
            
        Returns:
            True if closed
        """
        if fd in self.fd_table and fd >= 3:  # Don't close std fds
            del self.fd_table[fd]
            return True
        return False
    
    def read_file(self, path: str) -> Optional[bytes]:
        """Read entire file content
        
        Args:
            path: File path
            
        Returns:
            File content or None
        """
        file = self._resolve_path(path)
        if file and not file.is_directory():
            file.touch()
            self.stats['bytes_read'] += file.size
            return file.content
        return None
    
    def write_file(self, path: str, content: bytes) -> bool:
        """Write content to file
        
        Args:
            path: File path
            content: Content to write
            
        Returns:
            True if written
        """
        fd = self.open(path, 'w')
        if fd is None:
            return False
        
        entry = self.fd_table[fd]
        file = entry['file']
        
        file.content = content
        file.size = len(content)
        file.update()
        file.compute_hash()
        
        # Store in CAS
        if file.content_hash:
            self.cas[file.content_hash] = content
        
        self.stats['bytes_written'] += len(content)
        self.close(fd)
        
        return True
    
    def delete(self, path: str) -> bool:
        """Delete file or empty directory
        
        Args:
            path: Path to delete
            
        Returns:
            True if deleted
        """
        if path == '/':
            return False
        
        file = self._resolve_path(path)
        if file is None:
            return False
        
        # Cannot delete non-empty directories
        if file.is_directory() and file.children:
            return False
        
        # Remove from parent
        parent_path = '/'.join(path.split('/')[:-1]) or '/'
        name = path.split('/')[-1]
        parent = self._resolve_path(parent_path)
        
        if parent and name in parent.children:
            del parent.children[name]
            self.stats['files_deleted'] += 1
            return True
        
        return False
    
    def list_dir(self, path: str) -> Optional[List[Dict[str, Any]]]:
        """List directory contents
        
        Args:
            path: Directory path
            
        Returns:
            List of file info or None
        """
        dir_file = self._resolve_path(path)
        if dir_file is None or not dir_file.is_directory():
            return None
        
        dir_file.touch()
        
        result = []
        for name, child in dir_file.children.items():
            info = child.get_info()
            result.append(info)
        
        return result
    
    def exists(self, path: str) -> bool:
        """Check if path exists
        
        Args:
            path: Path to check
            
        Returns:
            True if exists
        """
        return self._resolve_path(path) is not None
    
    def sync(self):
        """Sync file system to persistent storage (placeholder)"""
        pass
    
    def get_stats(self) -> Dict[str, Any]:
        """Get file system statistics
        
        Returns:
            Statistics dictionary
        """
        def count_files(file: VictorFile) -> tuple:
            dirs = 1 if file.is_directory() else 0
            files = 0 if file.is_directory() else 1
            total_size = file.size
            
            for child in file.children.values():
                d, f, s = count_files(child)
                dirs += d
                files += f
                total_size += s
            
            return dirs, files, total_size
        
        dirs, files, total_size = count_files(self.root)
        
        return {
            'directories': dirs,
            'files': files,
            'total_size': total_size,
            'cas_entries': len(self.cas),
            'open_fds': len(self.fd_table) - 3,  # Exclude std fds
            **self.stats
        }
