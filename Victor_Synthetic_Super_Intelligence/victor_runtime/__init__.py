"""
Victor Personal Runtime - Cross-Platform Personal AI Assistant
==============================================================

A secure, user-controlled cross-platform runtime for personal AI assistance
across Windows, Android, and iOS devices with federated learning capabilities.

Key Features:
- Personal use only with explicit user consent
- Full user control (can be disabled/uninstalled anytime)
- Cross-device mesh learning for your personal device ecosystem
- Accessibility-compliant overlay features (optional)
- GitHub-synced configuration and learning state

Security Principles:
- User owns all data
- No data leaves your devices without explicit consent
- All overlay/automation requires accessibility permissions
- Standard platform shutdown mechanisms always work

Version: 1.0.0
Author: MASSIVEMAGNETICS
"""

__version__ = "1.0.0"
__author__ = "MASSIVEMAGNETICS"

from .core.runtime import VictorPersonalRuntime
from .core.consent import ConsentManager
from .core.user_control import UserControlPanel

__all__ = [
    'VictorPersonalRuntime',
    'ConsentManager', 
    'UserControlPanel',
    '__version__'
]
