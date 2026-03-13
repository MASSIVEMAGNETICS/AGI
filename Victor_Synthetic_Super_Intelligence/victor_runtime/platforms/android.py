#!/usr/bin/env python3
"""
Victor Personal Runtime - Android Platform Adapter
===================================================

Android-specific implementation using Kivy/python-for-android.

Features:
- System overlay (requires SYSTEM_ALERT_WINDOW permission)
- Accessibility service integration
- Notifications via Android NotificationManager
- App usage tracking (with permission)
- Foreground service for background operation
"""

import asyncio
from typing import Dict, Optional, Callable
import logging

from .base import BasePlatformAdapter

logger = logging.getLogger('victor_runtime.android')


class AndroidAdapter(BasePlatformAdapter):
    """
    Android platform adapter.
    
    Uses python-for-android and Android APIs through pyjnius.
    Requires appropriate permissions declared in AndroidManifest.xml.
    """
    
    # Required Android permissions
    REQUIRED_PERMISSIONS = [
        'INTERNET',
        'RECEIVE_BOOT_COMPLETED',
        'FOREGROUND_SERVICE'
    ]
    
    # Optional permissions (requested as needed)
    OPTIONAL_PERMISSIONS = {
        'overlay': 'SYSTEM_ALERT_WINDOW',
        'accessibility': 'BIND_ACCESSIBILITY_SERVICE',
        'usage_stats': 'PACKAGE_USAGE_STATS',
        'notification': 'POST_NOTIFICATIONS'
    }
    
    def __init__(self, runtime):
        super().__init__(runtime)
        self.platform_name = "android"
        
        self._jnius_available = False
        self._context = None
        self._overlay_view = None
        self._foreground_service = None
        
        self._check_dependencies()
    
    def _check_dependencies(self):
        """Check for Android-specific dependencies"""
        try:
            from jnius import autoclass
            self._jnius_available = True
            
            # Get Android context
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            self._context = PythonActivity.mActivity
            
        except ImportError:
            logger.warning("pyjnius not available - running in simulation mode")
    
    async def initialize(self) -> bool:
        """Initialize Android adapter"""
        logger.info("Initializing Android platform adapter")
        
        if self._jnius_available:
            # Start foreground service for background operation
            await self._start_foreground_service()
        
        self._initialized = True
        return True
    
    async def cleanup(self):
        """Clean up Android resources"""
        # Stop foreground service
        if self._foreground_service:
            await self._stop_foreground_service()
        
        # Remove overlay
        if self._overlay_view:
            await self.destroy_overlay()
        
        self._initialized = False
        logger.info("Android adapter cleaned up")
    
    async def _start_foreground_service(self):
        """Start a foreground service for background operation"""
        if not self._jnius_available:
            return
        
        try:
            from jnius import autoclass
            
            # This would start a foreground service
            # In production, you'd have a proper Service class
            logger.info("Foreground service started")
            
        except Exception as e:
            logger.error(f"Failed to start foreground service: {e}")
    
    async def _stop_foreground_service(self):
        """Stop the foreground service"""
        if self._foreground_service:
            # Stop service
            self._foreground_service = None
    
    # ========================
    # Permission Management
    # ========================
    
    async def show_consent_dialog(
        self,
        title: str,
        description: str,
        permission
    ) -> bool:
        """Show Android consent dialog"""
        if not self._jnius_available:
            return await super().show_consent_dialog(title, description, permission)
        
        try:
            from jnius import autoclass
            
            AlertDialog = autoclass('android.app.AlertDialog$Builder')
            
            # Create dialog
            builder = AlertDialog(self._context)
            builder.setTitle(title)
            builder.setMessage(description)
            
            # This is simplified - real implementation needs proper callbacks
            # builder.setPositiveButton("Allow", callback)
            # builder.setNegativeButton("Deny", callback)
            
            # For now, use console fallback
            return await super().show_consent_dialog(title, description, permission)
            
        except Exception as e:
            logger.error(f"Android dialog error: {e}")
            return await super().show_consent_dialog(title, description, permission)
    
    async def check_permission(self, permission: str) -> bool:
        """Check if Android permission is granted"""
        if not self._jnius_available:
            return False
        
        try:
            from jnius import autoclass
            
            Context = autoclass('android.content.Context')
            PackageManager = autoclass('android.content.pm.PackageManager')
            
            # Get the correct permission string
            # OPTIONAL_PERMISSIONS values are just the permission name without prefix
            if permission in self.OPTIONAL_PERMISSIONS:
                # Values like 'SYSTEM_ALERT_WINDOW' need the full prefix
                android_permission = f'android.permission.{self.OPTIONAL_PERMISSIONS[permission]}'
            else:
                # Direct permission name like 'INTERNET'
                android_permission = f'android.permission.{permission.upper()}'
            
            result = self._context.checkSelfPermission(android_permission)
            
            return result == PackageManager.PERMISSION_GRANTED
            
        except Exception as e:
            logger.error(f"Permission check error: {e}")
            return False
    
    async def request_permission(self, permission: str) -> bool:
        """Request an Android permission"""
        if not self._jnius_available:
            return False
        
        try:
            # Special handling for overlay permission
            if permission == 'overlay':
                return await self._request_overlay_permission()
            
            # For other permissions, request through activity
            # ActivityCompat.requestPermissions(activity, [permission], requestCode)
            
            # For now, check if already granted
            return await self.check_permission(permission)
            
        except Exception as e:
            logger.error(f"Permission request error: {e}")
            return False
    
    async def _request_overlay_permission(self) -> bool:
        """Request SYSTEM_ALERT_WINDOW permission"""
        if not self._jnius_available:
            return False
        
        try:
            from jnius import autoclass
            
            Settings = autoclass('android.provider.Settings')
            Intent = autoclass('android.content.Intent')
            Uri = autoclass('android.net.Uri')
            
            # Check if we have overlay permission
            if Settings.canDrawOverlays(self._context):
                return True
            
            # Request permission via settings
            intent = Intent(
                Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                Uri.parse(f"package:{self._context.getPackageName()}")
            )
            self._context.startActivity(intent)
            
            # User needs to enable manually
            logger.info("Overlay permission requested - user action required")
            return False
            
        except Exception as e:
            logger.error(f"Overlay permission error: {e}")
            return False
    
    # ========================
    # Overlay Features
    # ========================
    
    async def create_overlay(self, config: Dict) -> bool:
        """Create a system overlay on Android"""
        if not self._jnius_available:
            return False
        
        # Check overlay permission first
        if not await self._request_overlay_permission():
            logger.warning("Overlay permission not granted")
            return False
        
        try:
            from jnius import autoclass
            
            Context = autoclass('android.content.Context')
            WindowManager = autoclass('android.view.WindowManager')
            LayoutParams = autoclass('android.view.WindowManager$LayoutParams')
            View = autoclass('android.view.View')
            
            # Get window manager
            wm = self._context.getSystemService(Context.WINDOW_SERVICE)
            
            # Create overlay layout params
            # TYPE_APPLICATION_OVERLAY for Android 8.0+
            params = LayoutParams(
                LayoutParams.WRAP_CONTENT,
                LayoutParams.WRAP_CONTENT,
                LayoutParams.TYPE_APPLICATION_OVERLAY,
                LayoutParams.FLAG_NOT_FOCUSABLE,
                -3  # PixelFormat.TRANSLUCENT
            )
            
            # Position
            params.gravity = 51  # Gravity.TOP | Gravity.LEFT
            params.x = config.get('x', 0)
            params.y = config.get('y', 100)
            
            # Create view (would be custom view in production)
            # view = VictorOverlayView(self._context)
            # wm.addView(view, params)
            # self._overlay_view = view
            
            logger.info("Android overlay created")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create overlay: {e}")
            return False
    
    async def destroy_overlay(self):
        """Remove the overlay"""
        if not self._overlay_view or not self._jnius_available:
            return
        
        try:
            from jnius import autoclass
            
            Context = autoclass('android.content.Context')
            wm = self._context.getSystemService(Context.WINDOW_SERVICE)
            wm.removeView(self._overlay_view)
            self._overlay_view = None
            
        except Exception as e:
            logger.error(f"Error removing overlay: {e}")
    
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
        """Send Android notification"""
        if not self._jnius_available:
            return await super().send_notification(title, message, category, actions)
        
        try:
            from jnius import autoclass
            
            Context = autoclass('android.content.Context')
            NotificationManager = autoclass('android.app.NotificationManager')
            NotificationCompat = autoclass('androidx.core.app.NotificationCompat$Builder')
            
            # Get notification manager
            nm = self._context.getSystemService(Context.NOTIFICATION_SERVICE)
            
            # Build notification
            builder = NotificationCompat(self._context, "victor_channel")
            builder.setContentTitle(title)
            builder.setContentText(message)
            builder.setSmallIcon(self._context.getApplicationInfo().icon)
            builder.setAutoCancel(True)
            
            # Set priority based on category
            if category == "alert":
                builder.setPriority(NotificationCompat.PRIORITY_HIGH)
            
            # Add actions if provided
            if actions:
                for action_id, action_label in actions.items():
                    # Add action button
                    pass
            
            # Show notification
            notification_id = hash(title) % 10000
            nm.notify(notification_id, builder.build())
            
            return True
            
        except Exception as e:
            logger.error(f"Notification error: {e}")
            return await super().send_notification(title, message, category, actions)
    
    # ========================
    # Accessibility
    # ========================
    
    async def is_accessibility_enabled(self) -> bool:
        """Check if accessibility service is enabled"""
        if not self._jnius_available:
            return False
        
        try:
            from jnius import autoclass
            
            Settings = autoclass('android.provider.Settings')
            ContentResolver = autoclass('android.content.ContentResolver')
            
            resolver = self._context.getContentResolver()
            enabled_services = Settings.Secure.getString(
                resolver,
                Settings.Secure.ENABLED_ACCESSIBILITY_SERVICES
            )
            
            # Check if our service is in the list
            package_name = self._context.getPackageName()
            return package_name in (enabled_services or '')
            
        except Exception as e:
            logger.error(f"Accessibility check error: {e}")
            return False
    
    async def enable_accessibility(self) -> bool:
        """Open accessibility settings for user to enable"""
        if not self._jnius_available:
            return False
        
        try:
            from jnius import autoclass
            
            Intent = autoclass('android.content.Intent')
            Settings = autoclass('android.provider.Settings')
            
            intent = Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS)
            self._context.startActivity(intent)
            
            logger.info("Accessibility settings opened - user action required")
            return False  # User needs to enable manually
            
        except Exception as e:
            logger.error(f"Failed to open accessibility settings: {e}")
            return False
    
    # ========================
    # System Integration
    # ========================
    
    async def get_running_apps(self) -> list:
        """Get list of running apps (requires PACKAGE_USAGE_STATS)"""
        if not self._jnius_available:
            return []
        
        # Check permission
        if not await self.check_permission('usage_stats'):
            return []
        
        try:
            from jnius import autoclass
            
            Context = autoclass('android.content.Context')
            UsageStatsManager = autoclass('android.app.usage.UsageStatsManager')
            
            usm = self._context.getSystemService(Context.USAGE_STATS_SERVICE)
            # Query usage stats
            # ...
            
            return []
            
        except Exception as e:
            logger.error(f"Failed to get running apps: {e}")
            return []
    
    # ========================
    # Storage
    # ========================
    
    def get_app_data_path(self) -> str:
        """Get Android internal storage path"""
        if self._jnius_available and self._context:
            return str(self._context.getFilesDir().getAbsolutePath())
        return "/data/data/org.victor.runtime/files"
    
    def get_cache_path(self) -> str:
        """Get Android cache path"""
        if self._jnius_available and self._context:
            return str(self._context.getCacheDir().getAbsolutePath())
        return "/data/data/org.victor.runtime/cache"
    
    # ========================
    # Utilities
    # ========================
    
    def get_platform_info(self) -> Dict:
        """Get Android-specific information"""
        info = {
            'platform': 'android',
            'initialized': self._initialized,
            'jnius_available': self._jnius_available,
            'capabilities': []
        }
        
        if self._jnius_available:
            try:
                from jnius import autoclass
                Build = autoclass('android.os.Build')
                info['sdk_version'] = Build.VERSION.SDK_INT
                info['device'] = Build.MODEL
                info['manufacturer'] = Build.MANUFACTURER
            except Exception:
                pass
        
        return info
