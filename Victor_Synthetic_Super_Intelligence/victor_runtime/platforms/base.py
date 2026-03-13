#!/usr/bin/env python3
"""
Victor Personal Runtime - Base Platform Adapter
================================================

Abstract base class for platform-specific adapters.
Each platform (Windows, Android, iOS) implements this interface.
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Optional, Any
import logging

logger = logging.getLogger('victor_runtime.platform')


class BasePlatformAdapter(ABC):
    """
    Base class for platform adapters.
    
    Platform adapters handle platform-specific functionality like:
    - Permission requests
    - Overlay display
    - Accessibility services
    - System integration
    - Notifications
    
    Each platform implements its own adapter inheriting from this base.
    """
    
    def __init__(self, runtime):
        """
        Initialize platform adapter.
        
        Args:
            runtime: VictorPersonalRuntime instance
        """
        self.runtime = runtime
        self.platform_name = "generic"
        self._initialized = False
    
    async def initialize(self) -> bool:
        """
        Initialize platform-specific components.
        
        Returns:
            True if initialization successful
        """
        logger.info(f"Initializing {self.platform_name} platform adapter")
        self._initialized = True
        return True
    
    async def cleanup(self):
        """Clean up platform resources"""
        logger.info(f"Cleaning up {self.platform_name} platform adapter")
        self._initialized = False
    
    async def process_events(self):
        """Process platform-specific events"""
        pass
    
    # ========================
    # Permission Management
    # ========================
    
    async def show_consent_dialog(
        self,
        title: str,
        description: str,
        permission: Any
    ) -> bool:
        """
        Show a consent dialog to the user.
        
        Args:
            title: Dialog title
            description: Explanation of what permission is needed
            permission: Permission type
            
        Returns:
            True if user granted consent
        """
        # Default: console-based
        print(f"\n{'='*60}")
        print(f"PERMISSION REQUEST: {title}")
        print(f"{'='*60}")
        print(description)
        print("\nGrant this permission? (yes/no)")
        
        try:
            response = input("> ").strip().lower()
            return response in ('yes', 'y', 'grant', 'allow')
        except EOFError:
            return False
    
    async def check_permission(self, permission: str) -> bool:
        """
        Check if a permission is granted.
        
        Args:
            permission: Permission to check
            
        Returns:
            True if permission is granted
        """
        return True  # Base implementation assumes all granted
    
    async def request_permission(self, permission: str) -> bool:
        """
        Request a system permission.
        
        Args:
            permission: Permission to request
            
        Returns:
            True if permission granted
        """
        return await self.check_permission(permission)
    
    # ========================
    # Overlay Features
    # ========================
    
    async def create_overlay(self, config: Dict) -> bool:
        """
        Create a screen overlay.
        
        Args:
            config: Overlay configuration
            
        Returns:
            True if overlay created
        """
        logger.info("Overlay not supported on this platform")
        return False
    
    async def update_overlay(self, content: Dict):
        """Update overlay content"""
        pass
    
    async def destroy_overlay(self):
        """Destroy the overlay"""
        pass
    
    async def show_overlay(self):
        """Show the overlay"""
        pass
    
    async def hide_overlay(self):
        """Hide the overlay"""
        pass
    
    # ========================
    # Notifications
    # ========================
    
    async def send_notification(
        self,
        title: str,
        message: str,
        category: str = "info",
        actions: Optional[Dict] = None
    ) -> bool:
        """
        Send a system notification.
        
        Args:
            title: Notification title
            message: Notification message
            category: Category (info, alert, reminder)
            actions: Optional action buttons
            
        Returns:
            True if notification sent
        """
        print(f"[NOTIFICATION] {title}: {message}")
        return True
    
    # ========================
    # System Integration
    # ========================
    
    async def register_hotkey(self, hotkey: str, callback) -> bool:
        """
        Register a global hotkey.
        
        Args:
            hotkey: Hotkey combination (e.g., "ctrl+shift+v")
            callback: Function to call when hotkey pressed
            
        Returns:
            True if hotkey registered
        """
        logger.info(f"Hotkey registration not supported: {hotkey}")
        return False
    
    async def unregister_hotkey(self, hotkey: str):
        """Unregister a global hotkey"""
        pass
    
    async def get_active_window(self) -> Optional[Dict]:
        """
        Get information about the currently active window.
        
        Returns:
            Dictionary with window info or None
        """
        return None
    
    async def get_running_apps(self) -> list:
        """
        Get list of running applications.
        
        Returns:
            List of running app info
        """
        return []
    
    # ========================
    # Accessibility
    # ========================
    
    async def is_accessibility_enabled(self) -> bool:
        """Check if accessibility service is enabled"""
        return False
    
    async def enable_accessibility(self) -> bool:
        """Request user to enable accessibility service"""
        logger.info("Accessibility not supported on this platform")
        return False
    
    # ========================
    # Storage
    # ========================
    
    def get_app_data_path(self) -> str:
        """Get platform-specific app data path"""
        return str(self.runtime.data_dir) if self.runtime else "."
    
    def get_cache_path(self) -> str:
        """Get platform-specific cache path"""
        return str(self.runtime.data_dir / 'cache') if self.runtime else "./cache"
    
    # ========================
    # Utilities
    # ========================
    
    def get_platform_info(self) -> Dict:
        """Get platform-specific information"""
        return {
            'platform': self.platform_name,
            'initialized': self._initialized,
            'capabilities': []
        }
