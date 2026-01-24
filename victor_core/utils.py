"""
Victor Core Utilities
=====================

Core utilities for state management, logging, configuration, and serialization.

Author: Brandon Emery x Victor
License: Proprietary - Massive Magnetics
"""

from typing import Any, Dict, Optional, Union, List
import json
import pickle
import logging
import os
from pathlib import Path
from datetime import datetime


# =============================================================================
# Logging Infrastructure
# =============================================================================

def setup_logger(
    name: str,
    level: int = logging.INFO,
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Set up a logger with consistent formatting.
    
    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for logging
        
    Returns:
        Configured logger instance
        
    Example:
        >>> logger = setup_logger("victor.tensor", level=logging.DEBUG)
        >>> logger.info("Tensor operation complete")
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Clear existing handlers
    logger.handlers = []
    
    # Format: [2026-01-24 10:30:45] [INFO] [victor.tensor] Message
    formatter = logging.Formatter(
        fmt='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


# =============================================================================
# Configuration Management
# =============================================================================

class Config:
    """
    Configuration container with dot-notation access and persistence.
    
    Example:
        >>> config = Config({"model": {"lr": 0.01, "layers": 3}})
        >>> print(config.model.lr)  # 0.01
        >>> config.model.lr = 0.001
        >>> config.save("config.json")
    """
    
    def __init__(self, data: Optional[Dict[str, Any]] = None):
        self._data = data or {}
        
        # Convert nested dicts to Config objects
        for key, value in self._data.items():
            if isinstance(value, dict):
                self._data[key] = Config(value)
    
    def __getattr__(self, name: str) -> Any:
        if name.startswith('_'):
            return object.__getattribute__(self, name)
        if name in self._data:
            return self._data[name]
        raise AttributeError(f"Config has no attribute '{name}'")
    
    def __setattr__(self, name: str, value: Any) -> None:
        if name.startswith('_'):
            object.__setattr__(self, name, value)
        else:
            self._data[name] = value
    
    def __getitem__(self, key: str) -> Any:
        return self._data[key]
    
    def __setitem__(self, key: str, value: Any) -> None:
        self._data[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value with default fallback."""
        return self._data.get(key, default)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to plain dictionary."""
        result = {}
        for key, value in self._data.items():
            if isinstance(value, Config):
                result[key] = value.to_dict()
            else:
                result[key] = value
        return result
    
    def save(self, filepath: str) -> None:
        """Save configuration to JSON file."""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @staticmethod
    def load(filepath: str) -> 'Config':
        """Load configuration from JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        return Config(data)
    
    def __repr__(self) -> str:
        return f"Config({self._data!r})"


# =============================================================================
# State Management
# =============================================================================

class StateManager:
    """
    Manage application state with checkpointing and rollback.
    
    Example:
        >>> state = StateManager()
        >>> state.set("counter", 0)
        >>> state.checkpoint("initial")
        >>> state.set("counter", 10)
        >>> state.rollback("initial")
        >>> print(state.get("counter"))  # 0
    """
    
    def __init__(self):
        self._state: Dict[str, Any] = {}
        self._checkpoints: Dict[str, Dict[str, Any]] = {}
    
    def set(self, key: str, value: Any) -> None:
        """Set state value."""
        self._state[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get state value with optional default."""
        return self._state.get(key, default)
    
    def delete(self, key: str) -> None:
        """Delete state value."""
        if key in self._state:
            del self._state[key]
    
    def checkpoint(self, name: str) -> None:
        """Save current state as checkpoint."""
        self._checkpoints[name] = self._state.copy()
    
    def rollback(self, name: str) -> None:
        """Restore state from checkpoint."""
        if name not in self._checkpoints:
            raise KeyError(f"No checkpoint named '{name}'")
        self._state = self._checkpoints[name].copy()
    
    def list_checkpoints(self) -> List[str]:
        """List available checkpoint names."""
        return list(self._checkpoints.keys())
    
    def clear(self) -> None:
        """Clear all state."""
        self._state.clear()
    
    def save(self, filepath: str) -> None:
        """Save state to file."""
        with open(filepath, 'wb') as f:
            pickle.dump({
                'state': self._state,
                'checkpoints': self._checkpoints
            }, f)
    
    def load(self, filepath: str) -> None:
        """Load state from file."""
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
            self._state = data['state']
            self._checkpoints = data['checkpoints']


# =============================================================================
# File I/O Helpers
# =============================================================================

def ensure_dir(path: Union[str, Path]) -> Path:
    """
    Ensure directory exists, creating it if necessary.
    
    Args:
        path: Directory path
        
    Returns:
        Path object
        
    Example:
        >>> ensure_dir("outputs/models")
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def safe_save_json(data: Any, filepath: str, indent: int = 2) -> None:
    """
    Safely save JSON with atomic write (temp file + rename).
    
    Args:
        data: Data to serialize
        filepath: Target file path
        indent: JSON indentation level
    """
    temp_path = filepath + ".tmp"
    try:
        with open(temp_path, 'w') as f:
            json.dump(data, f, indent=indent)
        os.replace(temp_path, filepath)
    except Exception:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise


def load_json(filepath: str) -> Any:
    """
    Load data from JSON file.
    
    Args:
        filepath: Path to JSON file
        
    Returns:
        Deserialized data
    """
    with open(filepath, 'r') as f:
        return json.load(f)


def save_pickle(obj: Any, filepath: str) -> None:
    """
    Save object using pickle.
    
    Args:
        obj: Object to serialize
        filepath: Target file path
    """
    with open(filepath, 'wb') as f:
        pickle.dump(obj, f)


def load_pickle(filepath: str) -> Any:
    """
    Load object from pickle file.
    
    Args:
        filepath: Path to pickle file
        
    Returns:
        Deserialized object
    """
    with open(filepath, 'rb') as f:
        return pickle.load(f)


# =============================================================================
# Timing Utilities
# =============================================================================

class Timer:
    """
    Context manager for timing code blocks.
    
    Example:
        >>> with Timer("Model training"):
        ...     train_model()
        [Timer] Model training: 45.23s
    """
    
    def __init__(self, name: str = "Operation", verbose: bool = True):
        self.name = name
        self.verbose = verbose
        self.start_time = None
        self.elapsed = None
    
    def __enter__(self):
        self.start_time = datetime.now()
        return self
    
    def __exit__(self, *args):
        self.elapsed = (datetime.now() - self.start_time).total_seconds()
        if self.verbose:
            print(f"[Timer] {self.name}: {self.elapsed:.2f}s")


# =============================================================================
# Format Utilities
# =============================================================================

def format_bytes(num_bytes: int) -> str:
    """
    Format bytes in human-readable format.
    
    Args:
        num_bytes: Number of bytes
        
    Returns:
        Formatted string (e.g., "1.5 MB")
        
    Example:
        >>> print(format_bytes(1536000))  # "1.46 MB"
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if num_bytes < 1024.0:
            return f"{num_bytes:.2f} {unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.2f} PB"


def format_number(num: Union[int, float]) -> str:
    """
    Format large numbers with thousand separators.
    
    Args:
        num: Number to format
        
    Returns:
        Formatted string (e.g., "1,234,567")
        
    Example:
        >>> print(format_number(1234567))  # "1,234,567"
    """
    if isinstance(num, float):
        return f"{num:,.2f}"
    return f"{num:,}"


# =============================================================================
# Deprecation Warnings
# =============================================================================

def deprecated(message: str):
    """
    Decorator to mark functions as deprecated.
    
    Args:
        message: Deprecation message
        
    Example:
        >>> @deprecated("Use new_function() instead")
        ... def old_function():
        ...     pass
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            import warnings
            warnings.warn(
                f"{func.__name__} is deprecated. {message}",
                category=DeprecationWarning,
                stacklevel=2
            )
            return func(*args, **kwargs)
        return wrapper
    return decorator
