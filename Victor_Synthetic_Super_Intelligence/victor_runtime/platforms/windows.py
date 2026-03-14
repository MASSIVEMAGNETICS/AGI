#!/usr/bin/env python3
"""
Victor Personal Runtime - Windows Platform Adapter
===================================================

Windows-specific implementation using Win32 APIs and UWP.

Features:
- System tray integration
- Global hotkeys
- Toast notifications
- Window overlay (transparency)
- Accessibility support via UI Automation
"""

import asyncio
import sys
from typing import Dict, Optional, Callable
import logging

from .base import BasePlatformAdapter

logger = logging.getLogger('victor_runtime.windows')


class WindowsAdapter(BasePlatformAdapter):
    """
    Windows platform adapter.
    
    Uses Win32 APIs and optionally UWP for modern features.
    """
    
    def __init__(self, runtime):
        super().__init__(runtime)
        self.platform_name = "windows"
        
        self._tray_icon = None
        self._hotkeys: Dict[str, Callable] = {}
        self._overlay_window = None
        
        # Check for required modules
        self._win32_available = False
        self._uwp_available = False
        self._check_dependencies()
    
    def _check_dependencies(self):
        """Check for Windows-specific dependencies"""
        try:
            import win32api
            import win32con
            import win32gui
            self._win32_available = True
        except ImportError:
            logger.warning("pywin32 not available - some features disabled")
        
        try:
            from windows_toasts import Toast, WindowsToaster
            self._uwp_available = True
        except ImportError:
            logger.debug("windows-toasts not available")
    
    async def initialize(self) -> bool:
        """Initialize Windows adapter"""
        if sys.platform != 'win32':
            logger.error("Windows adapter initialized on non-Windows platform")
            return False
        
        logger.info("Initializing Windows platform adapter")
        
        # Initialize system tray
        if self._win32_available:
            try:
                await self._init_system_tray()
            except Exception as e:
                logger.warning(f"Failed to initialize system tray: {e}")
        
        self._initialized = True
        return True
    
    async def cleanup(self):
        """Clean up Windows resources"""
        # Remove system tray icon
        if self._tray_icon:
            try:
                await self._destroy_tray_icon()
            except Exception as e:
                logger.warning(f"Error destroying tray icon: {e}")
        
        # Unregister hotkeys
        for hotkey in list(self._hotkeys.keys()):
            await self.unregister_hotkey(hotkey)
        
        # Destroy overlay
        if self._overlay_window:
            await self.destroy_overlay()
        
        self._initialized = False
        logger.info("Windows adapter cleaned up")
    
    async def _init_system_tray(self):
        """Initialize system tray icon"""
        if not self._win32_available:
            return
        
        # Placeholder for system tray initialization
        # In production, use win32gui.Shell_NotifyIcon
        logger.info("System tray initialized")
    
    async def _destroy_tray_icon(self):
        """Destroy system tray icon"""
        self._tray_icon = None
    
    # ========================
    # Permission Management
    # ========================
    
    async def show_consent_dialog(
        self,
        title: str,
        description: str,
        permission
    ) -> bool:
        """Show Windows consent dialog"""
        if not self._win32_available:
            return await super().show_consent_dialog(title, description, permission)
        
        try:
            import win32api
            import win32con
            
            # Use MessageBox for simple consent
            result = win32api.MessageBox(
                0,
                f"{description}\n\nGrant this permission?",
                f"Victor - {title}",
                win32con.MB_YESNO | win32con.MB_ICONQUESTION
            )
            
            return result == win32con.IDYES
            
        except Exception as e:
            logger.error(f"Consent dialog error: {e}")
            return await super().show_consent_dialog(title, description, permission)
    
    async def check_permission(self, permission: str) -> bool:
        """Check if permission is available on Windows"""
        # Windows doesn't have the same permission model as mobile
        # Most permissions are granted by default
        
        if permission == 'accessibility':
            return await self.is_accessibility_enabled()
        elif permission == 'notification':
            return True  # Usually always available
        elif permission == 'background':
            return True  # Process management is different on Windows
        
        return True
    
    # ========================
    # Overlay Features
    # ========================
    
    async def create_overlay(self, config: Dict) -> bool:
        """Create a transparent overlay window"""
        if not self._win32_available:
            return False
        
        try:
            import win32gui
            import win32con
            import win32api
            
            # Create a transparent layered window
            # This is a placeholder - full implementation would use
            # CreateWindowEx with WS_EX_LAYERED | WS_EX_TOPMOST | WS_EX_TRANSPARENT
            
            logger.info("Windows overlay created")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create overlay: {e}")
            return False
    
    async def update_overlay(self, content: Dict):
        """Update overlay content"""
        if not self._overlay_window:
            return
        
        # Update overlay content
        # In production, redraw the window with new content
    
    async def destroy_overlay(self):
        """Destroy the overlay window"""
        if self._overlay_window:
            try:
                import win32gui
                # win32gui.DestroyWindow(self._overlay_window)
                self._overlay_window = None
            except Exception as e:
                logger.error(f"Error destroying overlay: {e}")
    
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
        """Send Windows toast notification"""
        
        # Try UWP toast first
        if self._uwp_available:
            try:
                from windows_toasts import Toast, WindowsToaster
                
                toaster = WindowsToaster('Victor')
                toast = Toast()
                toast.text_fields = [title, message]
                
                if actions:
                    for action_id, action_label in actions.items():
                        toast.AddAction(action_id, action_label)
                
                toaster.show_toast(toast)
                return True
                
            except Exception as e:
                logger.warning(f"UWP toast failed: {e}")
        
        # Fallback to balloon notification
        if self._win32_available and self._tray_icon:
            try:
                import win32gui
                import win32con
                
                # Show balloon notification from tray icon
                # win32gui.Shell_NotifyIcon(win32gui.NIM_MODIFY, ...)
                return True
                
            except Exception as e:
                logger.warning(f"Balloon notification failed: {e}")
        
        # Final fallback
        return await super().send_notification(title, message, category, actions)
    
    # ========================
    # System Integration
    # ========================
    
    async def register_hotkey(self, hotkey: str, callback: Callable) -> bool:
        """Register a global hotkey"""
        if not self._win32_available:
            return False
        
        try:
            import win32con
            
            # Parse hotkey string (e.g., "ctrl+shift+v")
            modifiers = 0
            key = 0
            
            parts = hotkey.lower().split('+')
            for part in parts:
                if part == 'ctrl':
                    modifiers |= win32con.MOD_CONTROL
                elif part == 'shift':
                    modifiers |= win32con.MOD_SHIFT
                elif part == 'alt':
                    modifiers |= win32con.MOD_ALT
                elif part == 'win':
                    modifiers |= win32con.MOD_WIN
                else:
                    # Assume it's the key
                    key = ord(part.upper())
            
            # Register hotkey (would need a message loop)
            # ctypes.windll.user32.RegisterHotKey(None, id, modifiers, key)
            
            self._hotkeys[hotkey] = callback
            logger.info(f"Hotkey registered: {hotkey}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register hotkey: {e}")
            return False
    
    async def unregister_hotkey(self, hotkey: str):
        """Unregister a global hotkey"""
        if hotkey in self._hotkeys:
            del self._hotkeys[hotkey]
            # ctypes.windll.user32.UnregisterHotKey(None, id)
    
    async def get_active_window(self) -> Optional[Dict]:
        """Get information about the active window"""
        if not self._win32_available:
            return None
        
        try:
            import win32gui
            import win32process
            
            hwnd = win32gui.GetForegroundWindow()
            title = win32gui.GetWindowText(hwnd)
            
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            
            return {
                'handle': hwnd,
                'title': title,
                'process_id': pid
            }
            
        except Exception as e:
            logger.error(f"Failed to get active window: {e}")
            return None
    
    async def get_running_apps(self) -> list:
        """Get list of running applications"""
        if not self._win32_available:
            return []
        
        apps = []
        try:
            import win32gui
            import win32process
            
            def callback(hwnd, result):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if title:
                        result.append({
                            'title': title,
                            'handle': hwnd
                        })
                return True
            
            win32gui.EnumWindows(callback, apps)
            
        except Exception as e:
            logger.error(f"Failed to enumerate windows: {e}")
        
        return apps
    
    # ========================
    # Accessibility
    # ========================
    
    async def is_accessibility_enabled(self) -> bool:
        """Check if accessibility/UI Automation is available"""
        try:
            # UI Automation is generally always available on Windows
            import comtypes.client
            return True
        except ImportError:
            return False
    
    async def enable_accessibility(self) -> bool:
        """Enable accessibility features"""
        # On Windows, accessibility is typically always available
        return await self.is_accessibility_enabled()
    
    # ========================
    # Storage
    # ========================
    
    def get_app_data_path(self) -> str:
        """Get Windows AppData path"""
        import os
        base = os.environ.get('APPDATA', os.path.expanduser('~'))
        return os.path.join(base, 'VictorRuntime')
    
    def get_cache_path(self) -> str:
        """Get Windows cache path"""
        import os
        base = os.environ.get('LOCALAPPDATA', os.path.expanduser('~'))
        return os.path.join(base, 'VictorRuntime', 'cache')
    
    # ========================
    # Utilities
    # ========================
    
    def get_platform_info(self) -> Dict:
        """Get Windows-specific information"""
        import platform
        
        return {
            'platform': 'windows',
            'version': platform.version(),
            'release': platform.release(),
            'initialized': self._initialized,
            'win32_available': self._win32_available,
            'uwp_available': self._uwp_available,
            'capabilities': self._get_capabilities()
        }
    
    def _get_capabilities(self) -> list:
        """Get available capabilities"""
        caps = []
        if self._win32_available:
            caps.extend(['tray', 'hotkeys', 'overlay'])
        if self._uwp_available:
            caps.append('toast_notifications')
        return caps
