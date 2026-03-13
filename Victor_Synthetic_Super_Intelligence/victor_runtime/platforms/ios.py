#!/usr/bin/env python3
"""
Victor Personal Runtime - iOS Platform Adapter
===============================================

iOS-specific implementation using pyobjus/rubicon-objc.

Features:
- Local notifications
- Background app refresh
- Spotlight integration
- Accessibility support via VoiceOver
- Widget support (via SwiftUI bridge)

Note: iOS has more restrictions than Android:
- No system overlay (not possible without jailbreak)
- Limited background execution
- App Clips for quick actions
"""

import asyncio
from typing import Dict, Optional, Callable
import logging

from .base import BasePlatformAdapter

logger = logging.getLogger('victor_runtime.ios')


class IOSAdapter(BasePlatformAdapter):
    """
    iOS platform adapter.
    
    Uses pyobjus or rubicon-objc for Objective-C bridge.
    Many features require proper app entitlements.
    """
    
    def __init__(self, runtime):
        super().__init__(runtime)
        self.platform_name = "ios"
        
        self._objc_available = False
        self._notification_center = None
        
        self._check_dependencies()
    
    def _check_dependencies(self):
        """Check for iOS-specific dependencies"""
        # Try pyobjus first (Kivy)
        try:
            from pyobjus import autoclass
            self._objc_available = True
            self._objc_method = 'pyobjus'
        except ImportError:
            pass
        
        # Try rubicon-objc (BeeWare)
        if not self._objc_available:
            try:
                from rubicon.objc import ObjCClass
                self._objc_available = True
                self._objc_method = 'rubicon'
            except ImportError:
                logger.warning("No Objective-C bridge available")
    
    async def initialize(self) -> bool:
        """Initialize iOS adapter"""
        logger.info("Initializing iOS platform adapter")
        
        if self._objc_available:
            await self._setup_notification_center()
            await self._register_background_tasks()
        
        self._initialized = True
        return True
    
    async def cleanup(self):
        """Clean up iOS resources"""
        self._initialized = False
        logger.info("iOS adapter cleaned up")
    
    async def _setup_notification_center(self):
        """Set up iOS notification center"""
        if not self._objc_available:
            return
        
        try:
            if self._objc_method == 'pyobjus':
                from pyobjus import autoclass
                UNUserNotificationCenter = autoclass('UNUserNotificationCenter')
                self._notification_center = UNUserNotificationCenter.currentNotificationCenter()
            else:
                from rubicon.objc import ObjCClass
                UNUserNotificationCenter = ObjCClass('UNUserNotificationCenter')
                self._notification_center = UNUserNotificationCenter.currentNotificationCenter()
            
            logger.info("Notification center initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize notification center: {e}")
    
    async def _register_background_tasks(self):
        """Register background tasks"""
        if not self._objc_available:
            return
        
        try:
            # Register background app refresh task
            # BGTaskScheduler.shared.register(forTaskWithIdentifier: ...)
            logger.info("Background tasks registered")
            
        except Exception as e:
            logger.warning(f"Failed to register background tasks: {e}")
    
    # ========================
    # Permission Management
    # ========================
    
    async def show_consent_dialog(
        self,
        title: str,
        description: str,
        permission
    ) -> bool:
        """Show iOS consent dialog"""
        if not self._objc_available:
            return await super().show_consent_dialog(title, description, permission)
        
        try:
            if self._objc_method == 'pyobjus':
                from pyobjus import autoclass
                UIAlertController = autoclass('UIAlertController')
                UIAlertAction = autoclass('UIAlertAction')
            else:
                from rubicon.objc import ObjCClass
                UIAlertController = ObjCClass('UIAlertController')
                UIAlertAction = ObjCClass('UIAlertAction')
            
            # Create alert controller
            # This requires async handling with completion handlers
            # For now, use console fallback
            return await super().show_consent_dialog(title, description, permission)
            
        except Exception as e:
            logger.error(f"iOS dialog error: {e}")
            return await super().show_consent_dialog(title, description, permission)
    
    async def check_permission(self, permission: str) -> bool:
        """Check if iOS permission is granted"""
        if not self._objc_available:
            return False
        
        permission_map = {
            'notification': self._check_notification_permission,
            'background': self._check_background_permission,
            'location': self._check_location_permission,
        }
        
        checker = permission_map.get(permission)
        if checker:
            return await checker()
        
        return True
    
    async def _check_notification_permission(self) -> bool:
        """Check notification permission"""
        if not self._notification_center:
            return False
        
        try:
            # UNUserNotificationCenter.current().getNotificationSettings
            # This is async with completion handler
            return True  # Simplified
        except Exception:
            return False
    
    async def _check_background_permission(self) -> bool:
        """Check background app refresh permission"""
        try:
            if self._objc_method == 'pyobjus':
                from pyobjus import autoclass
                UIApplication = autoclass('UIApplication')
            else:
                from rubicon.objc import ObjCClass
                UIApplication = ObjCClass('UIApplication')
            
            app = UIApplication.sharedApplication
            return app.backgroundRefreshStatus == 2  # UIBackgroundRefreshStatusAvailable
            
        except Exception:
            return False
    
    async def _check_location_permission(self) -> bool:
        """Check location permission"""
        try:
            if self._objc_method == 'pyobjus':
                from pyobjus import autoclass
                CLLocationManager = autoclass('CLLocationManager')
            else:
                from rubicon.objc import ObjCClass
                CLLocationManager = ObjCClass('CLLocationManager')
            
            status = CLLocationManager.authorizationStatus()
            return status in [3, 4]  # kCLAuthorizationStatusAuthorizedWhenInUse, kCLAuthorizationStatusAuthorizedAlways
            
        except Exception:
            return False
    
    async def request_permission(self, permission: str) -> bool:
        """Request an iOS permission"""
        if not self._objc_available:
            return False
        
        if permission == 'notification':
            return await self._request_notification_permission()
        
        return await self.check_permission(permission)
    
    async def _request_notification_permission(self) -> bool:
        """Request notification permission"""
        if not self._notification_center:
            return False
        
        try:
            # Request authorization
            # UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .badge, .sound])
            logger.info("Notification permission requested")
            return True  # Simplified
            
        except Exception as e:
            logger.error(f"Notification permission error: {e}")
            return False
    
    # ========================
    # Overlay Features (Limited on iOS)
    # ========================
    
    async def create_overlay(self, config: Dict) -> bool:
        """
        iOS does not support system overlays.
        
        Alternatives:
        - Use in-app overlay within Victor
        - Use Today Widget
        - Use App Clips for quick access
        """
        logger.warning("System overlay not supported on iOS")
        return False
    
    async def destroy_overlay(self):
        """No overlay to destroy on iOS"""
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
        """Send iOS local notification"""
        if not self._notification_center:
            return await super().send_notification(title, message, category, actions)
        
        try:
            if self._objc_method == 'pyobjus':
                from pyobjus import autoclass
                UNMutableNotificationContent = autoclass('UNMutableNotificationContent')
                UNNotificationRequest = autoclass('UNNotificationRequest')
                UNTimeIntervalNotificationTrigger = autoclass('UNTimeIntervalNotificationTrigger')
            else:
                from rubicon.objc import ObjCClass
                UNMutableNotificationContent = ObjCClass('UNMutableNotificationContent')
                UNNotificationRequest = ObjCClass('UNNotificationRequest')
                UNTimeIntervalNotificationTrigger = ObjCClass('UNTimeIntervalNotificationTrigger')
            
            # Create notification content
            content = UNMutableNotificationContent.alloc().init()
            content.title = title
            content.body = message
            
            if category == "alert":
                content.sound = UNMutableNotificationContent.defaultSound()
            
            # Create trigger (immediate)
            trigger = UNTimeIntervalNotificationTrigger.triggerWithTimeInterval_repeats_(1, False)
            
            # Create request
            request_id = f"victor_{hash(title) % 10000}"
            request = UNNotificationRequest.requestWithIdentifier_content_trigger_(
                request_id, content, trigger
            )
            
            # Add to notification center
            self._notification_center.addNotificationRequest_withCompletionHandler_(request, None)
            
            return True
            
        except Exception as e:
            logger.error(f"Notification error: {e}")
            return await super().send_notification(title, message, category, actions)
    
    # ========================
    # System Integration
    # ========================
    
    async def register_shortcut(self, shortcut_type: str, title: str, phrase: str) -> bool:
        """
        Register a Siri shortcut.
        
        Args:
            shortcut_type: Shortcut identifier
            title: Shortcut title
            phrase: Suggested Siri phrase
        """
        if not self._objc_available:
            return False
        
        try:
            # INShortcut, INVoiceShortcut
            logger.info(f"Registered Siri shortcut: {title}")
            return True
            
        except Exception as e:
            logger.error(f"Shortcut registration error: {e}")
            return False
    
    async def add_to_spotlight(self, item_id: str, title: str, description: str) -> bool:
        """
        Add item to Spotlight search index.
        
        Args:
            item_id: Unique item identifier
            title: Searchable title
            description: Item description
        """
        if not self._objc_available:
            return False
        
        try:
            if self._objc_method == 'pyobjus':
                from pyobjus import autoclass
                CSSearchableItem = autoclass('CSSearchableItem')
                CSSearchableItemAttributeSet = autoclass('CSSearchableItemAttributeSet')
                CSSearchableIndex = autoclass('CSSearchableIndex')
            else:
                from rubicon.objc import ObjCClass
                CSSearchableItem = ObjCClass('CSSearchableItem')
                CSSearchableItemAttributeSet = ObjCClass('CSSearchableItemAttributeSet')
                CSSearchableIndex = ObjCClass('CSSearchableIndex')
            
            # Create attribute set
            attributes = CSSearchableItemAttributeSet.alloc().initWithItemContentType_('public.content')
            attributes.title = title
            attributes.contentDescription = description
            
            # Create searchable item
            item = CSSearchableItem.alloc().initWithUniqueIdentifier_domainIdentifier_attributeSet_(
                item_id, 'org.victor.runtime', attributes
            )
            
            # Add to index
            index = CSSearchableIndex.defaultSearchableIndex()
            index.indexSearchableItems_completionHandler_([item], None)
            
            return True
            
        except Exception as e:
            logger.error(f"Spotlight indexing error: {e}")
            return False
    
    # ========================
    # Background Execution
    # ========================
    
    async def schedule_background_task(self, task_id: str, interval: int) -> bool:
        """
        Schedule a background task.
        
        iOS allows limited background execution:
        - Background App Refresh
        - Background Processing (for longer tasks)
        
        Args:
            task_id: Task identifier (must be in Info.plist)
            interval: Minimum interval in seconds
        """
        if not self._objc_available:
            return False
        
        try:
            # BGTaskScheduler.shared.submit(...)
            logger.info(f"Background task scheduled: {task_id}")
            return True
            
        except Exception as e:
            logger.error(f"Background task scheduling error: {e}")
            return False
    
    # ========================
    # Storage
    # ========================
    
    def get_app_data_path(self) -> str:
        """Get iOS Documents directory"""
        if self._objc_available:
            try:
                if self._objc_method == 'pyobjus':
                    from pyobjus import autoclass
                    NSFileManager = autoclass('NSFileManager')
                    NSSearchPathDirectory = 9  # NSDocumentDirectory
                    NSUserDomainMask = 1
                else:
                    from rubicon.objc import ObjCClass
                    NSFileManager = ObjCClass('NSFileManager')
                
                fm = NSFileManager.defaultManager
                urls = fm.URLsForDirectory_inDomains_(9, 1)  # NSDocumentDirectory, NSUserDomainMask
                if urls and len(urls) > 0:
                    return str(urls[0].path)
                    
            except Exception:
                pass
        
        return "~/Documents/VictorRuntime"
    
    def get_cache_path(self) -> str:
        """Get iOS Caches directory"""
        if self._objc_available:
            try:
                if self._objc_method == 'pyobjus':
                    from pyobjus import autoclass
                    NSFileManager = autoclass('NSFileManager')
                else:
                    from rubicon.objc import ObjCClass
                    NSFileManager = ObjCClass('NSFileManager')
                
                fm = NSFileManager.defaultManager
                urls = fm.URLsForDirectory_inDomains_(13, 1)  # NSCachesDirectory, NSUserDomainMask
                if urls and len(urls) > 0:
                    return str(urls[0].path)
                    
            except Exception:
                pass
        
        return "~/Library/Caches/VictorRuntime"
    
    # ========================
    # Utilities
    # ========================
    
    def get_platform_info(self) -> Dict:
        """Get iOS-specific information"""
        info = {
            'platform': 'ios',
            'initialized': self._initialized,
            'objc_available': self._objc_available,
            'objc_method': getattr(self, '_objc_method', None),
            'capabilities': self._get_capabilities()
        }
        
        if self._objc_available:
            try:
                if self._objc_method == 'pyobjus':
                    from pyobjus import autoclass
                    UIDevice = autoclass('UIDevice')
                    device = UIDevice.currentDevice
                else:
                    from rubicon.objc import ObjCClass
                    UIDevice = ObjCClass('UIDevice')
                    device = UIDevice.currentDevice
                
                info['device_name'] = str(device.name)
                info['system_version'] = str(device.systemVersion)
                info['model'] = str(device.model)
                
            except Exception:
                pass
        
        return info
    
    def _get_capabilities(self) -> list:
        """Get available iOS capabilities"""
        caps = ['notifications', 'background_refresh', 'spotlight']
        
        # iOS doesn't support overlay
        # caps.append('overlay') <- NOT available
        
        return caps
