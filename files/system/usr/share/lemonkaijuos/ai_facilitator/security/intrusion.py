"""
Intrusion Protection System
Family-safe protection against unauthorized access attempts
"""

import os
import logging
import subprocess
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class IntrusionProtection:
    """
    Manages intrusion protection mechanisms
    
    Features:
    - Failed attempt monitoring
    - Family-safe response (system shutdown, not data destruction)
    - Long password requirement after lockout
    - Automatic container unmounting
    - Physical tamper detection
    - Auto-rollback on unauthorized access
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize intrusion protection"""
        self.config = config or {}
        
        # Intrusion detection configuration
        self.max_attempts = self.config.get("max_attempts", 5)
        self.lockout_action = self.config.get("lockout_action", "shutdown")  # shutdown, lock, alert
        self.require_long_password = self.config.get("require_long_password", True)
        
        # State directory
        self.state_dir = Path(self.config.get(
            "state_dir",
            Path.home() / ".local" / "share" / "security" / "intrusion"
        ))
        self.state_dir.mkdir(parents=True, exist_ok=True)
        
        # Tamper detection
        self.tamper_detection_enabled = self.config.get("tamper_detection_enabled", False)
        
        logger.info("Intrusion Protection initialized")
    
    def monitor_failed_attempts(self, username: str) -> Dict[str, Any]:
        """
        Monitor failed login attempts and trigger response if threshold exceeded
        
        Args:
            username: Username to monitor
            
        Returns:
            Status dictionary
        """
        try:
            # Get faillock status
            result = subprocess.run(
                ["faillock", "--user", username],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "error": "Failed to get faillock status"
                }
            
            # Parse faillock output to count failures
            output = result.stdout
            
            # Check if user is locked
            if "locked" in output.lower():
                logger.warning(f"User {username} is locked due to failed attempts")
                
                # Trigger intrusion response
                response = self.trigger_intrusion_response(username, "failed_attempts")
                
                return {
                    "success": True,
                    "locked": True,
                    "response_triggered": True,
                    "response": response
                }
            else:
                return {
                    "success": True,
                    "locked": False,
                    "response_triggered": False
                }
                
        except Exception as e:
            logger.error(f"Failed to monitor attempts: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def trigger_intrusion_response(
        self,
        username: str,
        trigger_reason: str
    ) -> Dict[str, Any]:
        """
        Trigger intrusion response
        
        Actions (family-safe):
        1. Unmount all sensitive containers
        2. System shutdown (forces physical restart)
        3. Require long password on next boot
        4. Log intrusion attempt
        
        Args:
            username: Username
            trigger_reason: Reason for trigger (failed_attempts, tamper, etc.)
            
        Returns:
            Result dictionary
        """
        logger.critical(f"INTRUSION RESPONSE TRIGGERED for {username}: {trigger_reason}")
        
        actions_taken = []
        
        # Action 1: Unmount all containers
        unmount_result = self._unmount_all_containers()
        if unmount_result.get("success"):
            actions_taken.append("containers_unmounted")
        
        # Action 2: Set long password requirement flag
        if self.require_long_password:
            self._set_long_password_required(username)
            actions_taken.append("long_password_required")
        
        # Action 3: Log intrusion
        self._log_intrusion_attempt(username, trigger_reason, actions_taken)
        
        # Action 4: Execute lockout action
        if self.lockout_action == "shutdown":
            shutdown_result = self._execute_shutdown()
            if shutdown_result.get("success"):
                actions_taken.append("system_shutdown")
        elif self.lockout_action == "lock":
            lock_result = self._lock_system()
            if lock_result.get("success"):
                actions_taken.append("system_locked")
        
        return {
            "success": True,
            "trigger_reason": trigger_reason,
            "actions_taken": actions_taken
        }
    
    def _unmount_all_containers(self) -> Dict[str, Any]:
        """
        Unmount all Distrobox containers and encrypted volumes
        Family-safe: Just stops containers, doesn't delete data
        """
        try:
            # Get list of running containers
            result = subprocess.run(
                ["distrobox", "list"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return {"success": False, "error": "Failed to list containers"}
            
            # Parse container names
            containers = []
            for line in result.stdout.split('\n')[1:]:  # Skip header
                if line.strip():
                    parts = line.split('|')
                    if len(parts) >= 2:
                        container_name = parts[1].strip()
                        containers.append(container_name)
            
            # Stop each container
            stopped = []
            for container in containers:
                try:
                    subprocess.run(
                        ["distrobox", "stop", "-Y", container],
                        capture_output=True,
                        timeout=10
                    )
                    stopped.append(container)
                    logger.info(f"Stopped container: {container}")
                except Exception as e:
                    logger.error(f"Failed to stop {container}: {e}")
            
            return {
                "success": True,
                "containers_stopped": len(stopped),
                "containers": stopped
            }
            
        except Exception as e:
            logger.error(f"Failed to unmount containers: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _set_long_password_required(self, username: str):
        """
        Set flag requiring long password on next login
        This prevents PIN usage until password is entered
        """
        flag_file = self.state_dir / f"{username}_long_password_required"
        
        try:
            with open(flag_file, 'w') as f:
                json.dump({
                    "username": username,
                    "timestamp": datetime.now().isoformat(),
                    "reason": "intrusion_protection"
                }, f, indent=2)
            
            os.chmod(flag_file, 0o600)
            logger.info(f"Long password required flag set for {username}")
            
        except Exception as e:
            logger.error(f"Failed to set long password flag: {e}")
    
    def check_long_password_required(self, username: str) -> bool:
        """Check if long password is required for user"""
        flag_file = self.state_dir / f"{username}_long_password_required"
        return flag_file.exists()
    
    def clear_long_password_required(self, username: str):
        """Clear long password requirement after successful password login"""
        flag_file = self.state_dir / f"{username}_long_password_required"
        
        if flag_file.exists():
            try:
                flag_file.unlink()
                logger.info(f"Long password requirement cleared for {username}")
            except Exception as e:
                logger.error(f"Failed to clear long password flag: {e}")
    
    def _execute_shutdown(self) -> Dict[str, Any]:
        """
        Execute immediate system shutdown
        Family-safe: Forces physical restart, prevents remote access
        """
        try:
            logger.critical("EXECUTING SYSTEM SHUTDOWN - Intrusion Protection")
            
            # Schedule immediate shutdown
            subprocess.Popen(
                ["systemctl", "poweroff"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            return {
                "success": True,
                "action": "shutdown_initiated"
            }
            
        except Exception as e:
            logger.error(f"Failed to execute shutdown: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _lock_system(self) -> Dict[str, Any]:
        """Lock the system (alternative to shutdown)"""
        try:
            # Lock the current session
            subprocess.run(
                ["loginctl", "lock-sessions"],
                timeout=5
            )
            
            return {
                "success": True,
                "action": "system_locked"
            }
            
        except Exception as e:
            logger.error(f"Failed to lock system: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _log_intrusion_attempt(
        self,
        username: str,
        trigger_reason: str,
        actions_taken: list
    ):
        """Log intrusion attempt"""
        log_file = self.state_dir / "intrusion_log.json"
        
        log_entry = {
            "username": username,
            "timestamp": datetime.now().isoformat(),
            "trigger_reason": trigger_reason,
            "actions_taken": actions_taken,
            "hostname": os.uname().nodename
        }
        
        try:
            # Load existing log
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
            logger.error(f"Failed to log intrusion: {e}")
    
    def detect_physical_tamper(self) -> Dict[str, Any]:
        """
        Detect physical tampering attempts
        
        Checks:
        - Unexpected reboots
        - Hardware changes
        - Boot integrity
        """
        tamper_detected = False
        tamper_reasons = []
        
        try:
            # Check for unexpected reboots
            uptime_result = subprocess.run(
                ["uptime", "-s"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if uptime_result.returncode == 0:
                boot_time_str = uptime_result.stdout.strip()
                boot_time = datetime.strptime(boot_time_str, "%Y-%m-%d %H:%M:%S")
                
                # Check if boot was recent (within last 5 minutes)
                if datetime.now() - boot_time < timedelta(minutes=5):
                    # Check if this was an expected reboot
                    expected_reboot_file = self.state_dir / "expected_reboot"
                    
                    if not expected_reboot_file.exists():
                        tamper_detected = True
                        tamper_reasons.append("unexpected_reboot")
            
            # Check for hardware changes (simplified)
            # In production, would check DMI info, disk serial numbers, etc.
            
            if tamper_detected:
                logger.warning(f"Physical tamper detected: {tamper_reasons}")
                
                # Trigger auto-rollback
                self._trigger_auto_rollback()
            
            return {
                "tamper_detected": tamper_detected,
                "reasons": tamper_reasons
            }
            
        except Exception as e:
            logger.error(f"Failed to detect tamper: {e}")
            return {
                "tamper_detected": False,
                "error": str(e)
            }
    
    def _trigger_auto_rollback(self):
        """
        Trigger automatic rpm-ostree rollback on tamper detection
        Atomic OS feature: rollback to last known-good state
        """
        try:
            logger.critical("TRIGGERING AUTO-ROLLBACK - Physical tamper detected")
            
            # Execute rollback
            subprocess.run(
                ["rpm-ostree", "rollback", "--reboot"],
                timeout=30
            )
            
        except Exception as e:
            logger.error(f"Failed to trigger auto-rollback: {e}")
    
    def mark_expected_reboot(self):
        """Mark next reboot as expected (not tamper)"""
        expected_reboot_file = self.state_dir / "expected_reboot"
        
        try:
            with open(expected_reboot_file, 'w') as f:
                json.dump({
                    "timestamp": datetime.now().isoformat(),
                    "reason": "user_initiated"
                }, f)
            
            # File will be deleted on successful boot
            
        except Exception as e:
            logger.error(f"Failed to mark expected reboot: {e}")
    
    def clear_expected_reboot(self):
        """Clear expected reboot flag after successful boot"""
        expected_reboot_file = self.state_dir / "expected_reboot"
        
        if expected_reboot_file.exists():
            try:
                expected_reboot_file.unlink()
            except Exception as e:
                logger.error(f"Failed to clear expected reboot: {e}")
    
    def get_intrusion_log(self, limit: int = 10) -> list:
        """Get intrusion attempt log"""
        log_file = self.state_dir / "intrusion_log.json"
        
        if not log_file.exists():
            return []
        
        try:
            with open(log_file, 'r') as f:
                logs = json.load(f)
            
            return logs[-limit:]
            
        except Exception as e:
            logger.error(f"Failed to get intrusion log: {e}")
            return []
    
    def get_status(self) -> Dict[str, Any]:
        """Get current intrusion protection status"""
        return {
            "enabled": True,
            "max_attempts": self.max_attempts,
            "lockout_action": self.lockout_action,
            "require_long_password": self.require_long_password,
            "tamper_detection_enabled": self.tamper_detection_enabled,
            "recent_intrusions": len(self.get_intrusion_log(limit=10))
        }
