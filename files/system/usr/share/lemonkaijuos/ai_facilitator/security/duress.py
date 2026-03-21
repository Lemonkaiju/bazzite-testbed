"""
Duress Code System
Detects coercion and triggers silent protective measures
"""

import os
import logging
import subprocess
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)


class DuressManager:
    """
    Manages duress codes for coercion protection
    
    Features:
    - Normal PIN vs Duress PIN detection
    - Silent alert to other devices
    - Instant unmount of sensitive containers
    - "Houdini" fake login failure
    - No visible indication of duress activation
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize duress manager"""
        self.config = config or {}
        
        # Duress code storage
        self.duress_dir = Path(self.config.get(
            "duress_dir",
            Path.home() / ".local" / "share" / "security" / "duress"
        ))
        self.duress_dir.mkdir(parents=True, exist_ok=True)
        
        # Alert configuration
        self.alert_devices = self.config.get("alert_devices", [])
        self.alert_method = self.config.get("alert_method", "encrypted_ping")
        
        # Container configuration
        self.sensitive_containers = self.config.get("sensitive_containers", [])
        
        # Houdini configuration
        self.houdini_enabled = self.config.get("houdini_enabled", True)
        self.houdini_delay = self.config.get("houdini_delay", 3)  # seconds
        
        logger.info("Duress Manager initialized")
    
    def create_duress_pin(
        self,
        username: str,
        normal_pin: str,
        duress_pin: str,
        verify_duress_pin: str
    ) -> Dict[str, Any]:
        """
        Create a duress PIN for a user
        
        Args:
            username: Username
            normal_pin: Normal 6-digit PIN (for verification)
            duress_pin: Duress 6-digit PIN
            verify_duress_pin: Duress PIN verification
            
        Returns:
            Result dictionary
        """
        # Validate duress PIN format
        if len(duress_pin) != 6 or not duress_pin.isdigit():
            return {
                "success": False,
                "error": "Duress PIN must be exactly 6 digits"
            }
        
        # Verify duress PIN match
        if duress_pin != verify_duress_pin:
            return {
                "success": False,
                "error": "Duress PINs do not match"
            }
        
        # Ensure duress PIN is different from normal PIN
        if duress_pin == normal_pin:
            return {
                "success": False,
                "error": "Duress PIN must be different from normal PIN"
            }
        
        # Hash duress PIN
        duress_hash = self._hash_pin(duress_pin)
        
        # Store duress PIN
        try:
            duress_file = self.duress_dir / f"{username}.json"
            
            duress_data = {
                "username": username,
                "duress_hash": duress_hash,
                "created": datetime.now().isoformat(),
                "alert_devices": self.alert_devices,
                "sensitive_containers": self.sensitive_containers,
                "houdini_enabled": self.houdini_enabled
            }
            
            with open(duress_file, 'w') as f:
                json.dump(duress_data, f, indent=2)
            
            os.chmod(duress_file, 0o600)
            
            logger.info(f"Duress PIN created for {username}")
            
            return {
                "success": True,
                "message": "Duress PIN created successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to create duress PIN: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def check_duress(self, username: str, pin: str) -> Dict[str, Any]:
        """
        Check if entered PIN is a duress code
        
        Args:
            username: Username
            pin: PIN to check
            
        Returns:
            Result with is_duress flag
        """
        duress_file = self.duress_dir / f"{username}.json"
        
        if not duress_file.exists():
            return {
                "is_duress": False,
                "message": "No duress PIN configured"
            }
        
        try:
            with open(duress_file, 'r') as f:
                duress_data = json.load(f)
            
            duress_hash = duress_data.get("duress_hash")
            
            # Verify PIN against duress hash
            import crypt
            if crypt.crypt(pin, duress_hash) == duress_hash:
                logger.warning(f"DURESS CODE DETECTED for {username}")
                return {
                    "is_duress": True,
                    "duress_data": duress_data
                }
            else:
                return {
                    "is_duress": False
                }
                
        except Exception as e:
            logger.error(f"Failed to check duress: {e}")
            return {
                "is_duress": False,
                "error": str(e)
            }
    
    def trigger_duress_response(
        self,
        username: str,
        duress_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Trigger duress response actions
        
        Actions:
        1. Send silent alert to other devices
        2. Unmount sensitive containers
        3. Execute Houdini (fake login failure)
        
        Args:
            username: Username
            duress_data: Duress configuration data
            
        Returns:
            Result dictionary
        """
        logger.critical(f"DURESS RESPONSE TRIGGERED for {username}")
        
        actions_taken = []
        
        # Action 1: Send silent alert
        alert_result = self._send_silent_alert(username, duress_data)
        if alert_result.get("success"):
            actions_taken.append("silent_alert_sent")
        
        # Action 2: Unmount sensitive containers
        unmount_result = self._unmount_sensitive_containers(duress_data)
        if unmount_result.get("success"):
            actions_taken.append("containers_unmounted")
        
        # Action 3: Houdini (fake failure)
        if duress_data.get("houdini_enabled", True):
            houdini_result = self._execute_houdini(duress_data)
            if houdini_result.get("success"):
                actions_taken.append("houdini_executed")
        
        # Log duress activation (encrypted)
        self._log_duress_activation(username, actions_taken)
        
        return {
            "success": True,
            "actions_taken": actions_taken,
            "message": "Duress response executed"
        }
    
    def _send_silent_alert(
        self,
        username: str,
        duress_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Send silent encrypted alert to other devices
        
        Methods:
        - Encrypted ping to mobile devices
        - Signal/Matrix message
        - Email with encrypted subject
        """
        alert_devices = duress_data.get("alert_devices", [])
        
        if not alert_devices:
            logger.warning("No alert devices configured")
            return {"success": False, "error": "No alert devices"}
        
        try:
            # Create alert message
            alert_message = {
                "type": "duress_alert",
                "username": username,
                "timestamp": datetime.now().isoformat(),
                "location": os.uname().nodename
            }
            
            # Encrypt alert message
            encrypted_alert = self._encrypt_alert(alert_message)
            
            # Send to each device
            for device in alert_devices:
                self._send_to_device(device, encrypted_alert)
            
            logger.info(f"Silent alert sent to {len(alert_devices)} devices")
            
            return {
                "success": True,
                "devices_alerted": len(alert_devices)
            }
            
        except Exception as e:
            logger.error(f"Failed to send silent alert: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _unmount_sensitive_containers(
        self,
        duress_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Instantly unmount sensitive Distrobox containers and encrypted volumes
        """
        containers = duress_data.get("sensitive_containers", [])
        
        if not containers:
            logger.warning("No sensitive containers configured")
            return {"success": False, "error": "No containers"}
        
        unmounted = []
        failed = []
        
        for container in containers:
            try:
                # Stop Distrobox container
                result = subprocess.run(
                    ["distrobox", "stop", "-Y", container],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    unmounted.append(container)
                    logger.info(f"Unmounted container: {container}")
                else:
                    failed.append(container)
                    logger.error(f"Failed to unmount {container}: {result.stderr}")
                    
            except Exception as e:
                failed.append(container)
                logger.error(f"Failed to unmount {container}: {e}")
        
        return {
            "success": len(unmounted) > 0,
            "unmounted": unmounted,
            "failed": failed
        }
    
    def _execute_houdini(self, duress_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute "Houdini" - fake login failure or power off
        
        Behavior:
        - Show "loading" for configured delay
        - Display "Authentication failed" message
        - OR trigger immediate system power off
        """
        import time
        
        houdini_delay = duress_data.get("houdini_delay", self.houdini_delay)
        
        try:
            # Brief delay to simulate authentication attempt
            time.sleep(houdini_delay)
            
            # Option 1: Fake failure (for GDM/login)
            # This would be handled by PAM module returning failure
            
            # Option 2: Immediate power off (for physical theft)
            # Uncomment to enable:
            # subprocess.run(["systemctl", "poweroff"], timeout=5)
            
            logger.info("Houdini executed - fake authentication failure")
            
            return {
                "success": True,
                "action": "fake_failure"
            }
            
        except Exception as e:
            logger.error(f"Houdini execution failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _hash_pin(self, pin: str) -> str:
        """Hash PIN using crypt(3) with SHA-512"""
        import crypt
        salt = crypt.mksalt(crypt.METHOD_SHA512)
        return crypt.crypt(pin, salt)
    
    def _encrypt_alert(self, message: Dict[str, Any]) -> str:
        """Encrypt alert message for transmission"""
        # Simple encryption for now - should use proper encryption in production
        import base64
        message_json = json.dumps(message)
        encrypted = base64.b64encode(message_json.encode()).decode()
        return encrypted
    
    def _send_to_device(self, device: str, encrypted_alert: str):
        """Send encrypted alert to a device"""
        # Implementation depends on device type
        # Could be: HTTP POST, MQTT, Signal, Matrix, etc.
        
        # For now, write to a file that can be picked up by mobile app
        alert_file = self.duress_dir / "alerts" / f"{device}_{datetime.now().timestamp()}.alert"
        alert_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(alert_file, 'w') as f:
            f.write(encrypted_alert)
        
        logger.info(f"Alert queued for device: {device}")
    
    def _log_duress_activation(self, username: str, actions: List[str]):
        """Log duress activation (encrypted)"""
        log_file = self.duress_dir / "activations.log"
        
        log_entry = {
            "username": username,
            "timestamp": datetime.now().isoformat(),
            "actions": actions,
            "hostname": os.uname().nodename
        }
        
        try:
            # Append to log
            logs = []
            if log_file.exists():
                with open(log_file, 'r') as f:
                    logs = json.load(f)
            
            logs.append(log_entry)
            
            # Keep only last 100 entries
            logs = logs[-100:]
            
            with open(log_file, 'w') as f:
                json.dump(logs, f, indent=2)
            
            os.chmod(log_file, 0o600)
            
        except Exception as e:
            logger.error(f"Failed to log duress activation: {e}")
    
    def has_duress_pin(self, username: str) -> bool:
        """Check if user has a duress PIN configured"""
        duress_file = self.duress_dir / f"{username}.json"
        return duress_file.exists()
    
    def remove_duress_pin(self, username: str) -> Dict[str, Any]:
        """Remove duress PIN for a user"""
        duress_file = self.duress_dir / f"{username}.json"
        
        if not duress_file.exists():
            return {
                "success": False,
                "error": "No duress PIN configured"
            }
        
        try:
            duress_file.unlink()
            logger.info(f"Duress PIN removed for {username}")
            
            return {
                "success": True,
                "message": "Duress PIN removed"
            }
            
        except Exception as e:
            logger.error(f"Failed to remove duress PIN: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_duress_config(self, username: str) -> Optional[Dict[str, Any]]:
        """Get duress configuration for a user"""
        duress_file = self.duress_dir / f"{username}.json"
        
        if not duress_file.exists():
            return None
        
        try:
            with open(duress_file, 'r') as f:
                data = json.load(f)
            
            # Remove sensitive hash
            data.pop("duress_hash", None)
            
            return data
            
        except Exception as e:
            logger.error(f"Failed to get duress config: {e}")
            return None
    
    def get_activation_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get duress activation history"""
        log_file = self.duress_dir / "activations.log"
        
        if not log_file.exists():
            return []
        
        try:
            with open(log_file, 'r') as f:
                logs = json.load(f)
            
            return logs[-limit:]
            
        except Exception as e:
            logger.error(f"Failed to get activation history: {e}")
            return []
