"""
User-Present Flag Detection
Implements the "Kill Switch" - AI only operates when user is present
"""

import os
import logging
import threading
import time
from pathlib import Path
from typing import Dict, Any, Optional
import subprocess

logger = logging.getLogger(__name__)


class UserPresentDetector:
    """
    Detects if user is present via:
    1. USB Sentinel Key (physical USB device)
    2. Mobile Dashboard Toggle (network-based flag)
    
    The AI command server is only authorized to execute when this flag is active.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize user presence detector"""
        self.config = config
        self.usb_sentinel_enabled = config.get("usb_sentinel_enabled", True)
        self.mobile_dashboard_enabled = config.get("mobile_dashboard_enabled", False)
        self.check_interval = config.get("check_interval", 5)
        
        # USB sentinel configuration
        self.sentinel_vendor_id = config.get("sentinel_vendor_id", None)
        self.sentinel_product_id = config.get("sentinel_product_id", None)
        self.sentinel_label = config.get("sentinel_label", "AI_SENTINEL")
        
        # Mobile dashboard configuration
        self.dashboard_flag_file = Path(config.get(
            "dashboard_flag_file",
            Path.home() / ".local" / "share" / "ai_facilitator" / "user_present.flag"
        ))
        
        # State
        self._user_present = False
        self._monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        
        logger.info("User-Present Detector initialized")
    
    def is_user_present(self) -> bool:
        """Check if user is currently present"""
        with self._lock:
            return self._user_present
    
    def start_monitoring(self):
        """Start continuous monitoring of user presence"""
        if self._monitoring:
            logger.warning("Monitoring already active")
            return
        
        self._monitoring = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        logger.info("User presence monitoring started")
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
        logger.info("User presence monitoring stopped")
    
    def _monitor_loop(self):
        """Background monitoring loop"""
        while self._monitoring:
            present = self._check_presence()
            
            with self._lock:
                if present != self._user_present:
                    self._user_present = present
                    if present:
                        logger.info("User presence detected - AI facilitator ACTIVE")
                    else:
                        logger.warning("User presence lost - AI facilitator DISABLED")
            
            time.sleep(self.check_interval)
    
    def _check_presence(self) -> bool:
        """Check all configured presence methods"""
        # If USB sentinel is enabled, check for it
        if self.usb_sentinel_enabled:
            if self._check_usb_sentinel():
                return True
        
        # If mobile dashboard is enabled, check flag file
        if self.mobile_dashboard_enabled:
            if self._check_mobile_dashboard():
                return True
        
        # No presence detected
        return False
    
    def _check_usb_sentinel(self) -> bool:
        """
        Check if USB sentinel key is present
        
        Methods:
        1. If vendor/product ID specified, check via lsusb
        2. If label specified, check for mounted volume
        3. Fallback: check for any USB storage device with specific label
        """
        # Method 1: Check by vendor/product ID
        if self.sentinel_vendor_id and self.sentinel_product_id:
            try:
                result = subprocess.run(
                    ["lsusb"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0:
                    # Look for vendor:product ID
                    search_string = f"{self.sentinel_vendor_id}:{self.sentinel_product_id}"
                    if search_string in result.stdout:
                        return True
            except Exception as e:
                logger.debug(f"lsusb check failed: {e}")
        
        # Method 2: Check by volume label
        if self.sentinel_label:
            try:
                # Check mounted volumes
                result = subprocess.run(
                    ["findmnt", "-n", "-o", "LABEL"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0:
                    labels = result.stdout.strip().split('\n')
                    if self.sentinel_label in labels:
                        return True
                
                # Also check /dev/disk/by-label/
                label_path = Path(f"/dev/disk/by-label/{self.sentinel_label}")
                if label_path.exists():
                    return True
                    
            except Exception as e:
                logger.debug(f"Volume label check failed: {e}")
        
        return False
    
    def _check_mobile_dashboard(self) -> bool:
        """Check if mobile dashboard has set the user-present flag"""
        try:
            if self.dashboard_flag_file.exists():
                # Check if flag is recent (within last 60 seconds)
                mtime = self.dashboard_flag_file.stat().st_mtime
                age = time.time() - mtime
                
                if age < 60:
                    return True
                else:
                    # Flag is stale, remove it
                    self.dashboard_flag_file.unlink()
                    
        except Exception as e:
            logger.debug(f"Mobile dashboard check failed: {e}")
        
        return False
    
    def set_mobile_dashboard_flag(self, enabled: bool):
        """
        Set the mobile dashboard flag
        Called by the mobile dashboard API
        """
        try:
            if enabled:
                # Create flag file
                self.dashboard_flag_file.parent.mkdir(parents=True, exist_ok=True)
                self.dashboard_flag_file.touch()
                logger.info("Mobile dashboard flag enabled")
            else:
                # Remove flag file
                if self.dashboard_flag_file.exists():
                    self.dashboard_flag_file.unlink()
                logger.info("Mobile dashboard flag disabled")
        except Exception as e:
            logger.error(f"Failed to set mobile dashboard flag: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status"""
        return {
            "user_present": self.is_user_present(),
            "usb_sentinel_enabled": self.usb_sentinel_enabled,
            "usb_sentinel_detected": self._check_usb_sentinel() if self.usb_sentinel_enabled else None,
            "mobile_dashboard_enabled": self.mobile_dashboard_enabled,
            "mobile_dashboard_active": self._check_mobile_dashboard() if self.mobile_dashboard_enabled else None,
            "monitoring": self._monitoring
        }
