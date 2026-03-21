"""
Shutdown Handler - Manages failed authentication attempts and system shutdown
"""

import os
import subprocess
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ShutdownHandler:
    """
    Handles authentication failure escalation and system shutdown
    
    Security Behavior:
    - 5 PIN attempts allowed
    - After 5 PIN failures, fall back to password
    - 5 password attempts allowed
    - After 10 total failures (5 PIN + 5 password), shutdown system
    
    This protects against:
    - Brute force attacks
    - Physical theft (attacker can't keep trying)
    - Unauthorized access attempts
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize shutdown handler"""
        self.config = config or {}
        
        # Attempt limits
        self.pin_attempt_limit = self.config.get("pin_attempt_limit", 5)
        self.password_attempt_limit = self.config.get("password_attempt_limit", 5)
        self.total_attempt_limit = self.pin_attempt_limit + self.password_attempt_limit
        
        # Faillock settings
        self.faillock_dir = Path("/var/run/faillock")
        
        # Shutdown settings
        self.shutdown_delay = self.config.get("shutdown_delay", 10)  # seconds
        self.shutdown_message = self.config.get(
            "shutdown_message",
            "Too many failed authentication attempts. System shutting down for security."
        )
        
        logger.info("Shutdown Handler initialized")
    
    def get_failed_attempts(self, username: str) -> int:
        """
        Get number of failed authentication attempts for user
        
        Args:
            username: Username to check
            
        Returns:
            Number of failed attempts
        """
        try:
            result = subprocess.run(
                ['faillock', '--user', username],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            # Parse faillock output
            # Format: "When                Type  Source   Valid"
            # Count lines with "RHOST" (failed attempts)
            attempts = 0
            for line in result.stdout.split('\n'):
                if 'RHOST' in line or 'TTY' in line:
                    attempts += 1
            
            return attempts
            
        except Exception as e:
            logger.error(f"Failed to get failed attempts: {e}")
            return 0
    
    def check_and_handle_attempts(self, username: str) -> Dict[str, Any]:
        """
        Check failed attempts and take action if limit exceeded
        
        Args:
            username: Username to check
            
        Returns:
            Result dictionary with action taken
        """
        attempts = self.get_failed_attempts(username)
        
        logger.info(f"User {username} has {attempts} failed attempts")
        
        # Check if PIN attempt limit exceeded (switch to password)
        if attempts >= self.pin_attempt_limit and attempts < self.total_attempt_limit:
            return {
                "action": "fallback_to_password",
                "attempts": attempts,
                "remaining": self.total_attempt_limit - attempts,
                "message": f"PIN attempts exhausted. Use password ({self.total_attempt_limit - attempts} attempts remaining)"
            }
        
        # Check if total attempt limit exceeded (shutdown)
        elif attempts >= self.total_attempt_limit:
            logger.warning(f"Total attempt limit exceeded for {username}. Initiating shutdown.")
            self.initiate_shutdown()
            return {
                "action": "shutdown",
                "attempts": attempts,
                "message": "Too many failed attempts. System shutting down."
            }
        
        # Still within PIN attempt limit
        else:
            return {
                "action": "continue",
                "attempts": attempts,
                "remaining": self.pin_attempt_limit - attempts,
                "message": f"{self.pin_attempt_limit - attempts} PIN attempts remaining"
            }
    
    def initiate_shutdown(self):
        """
        Initiate system shutdown after failed authentication attempts
        
        This is a security measure to prevent brute force attacks.
        """
        try:
            # Log shutdown event
            self._log_shutdown_event()
            
            # Show warning to user
            self._show_shutdown_warning()
            
            # Execute shutdown
            subprocess.run(
                ['systemctl', 'poweroff'],
                timeout=5
            )
            
            logger.info("System shutdown initiated")
            
        except Exception as e:
            logger.error(f"Failed to initiate shutdown: {e}")
            # Fallback: try alternative shutdown method
            try:
                subprocess.run(['shutdown', '-h', 'now'], timeout=5)
            except Exception as e2:
                logger.error(f"Fallback shutdown also failed: {e2}")
    
    def reset_attempts(self, username: str) -> Dict[str, Any]:
        """
        Reset failed attempt counter for user
        
        Args:
            username: Username to reset
            
        Returns:
            Result dictionary
        """
        try:
            subprocess.run(
                ['faillock', '--user', username, '--reset'],
                capture_output=True,
                timeout=5,
                check=True
            )
            
            logger.info(f"Reset failed attempts for {username}")
            
            return {
                "success": True,
                "message": f"Failed attempts reset for {username}"
            }
            
        except Exception as e:
            logger.error(f"Failed to reset attempts: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _show_shutdown_warning(self):
        """Show shutdown warning to user"""
        try:
            # Try to show GUI notification
            subprocess.run(
                ['notify-send', 
                 '--urgency=critical',
                 '--icon=dialog-error',
                 'Security Alert',
                 self.shutdown_message],
                timeout=2
            )
        except:
            pass  # Notification not critical
        
        # Also write to console
        try:
            subprocess.run(
                ['wall', self.shutdown_message],
                timeout=2
            )
        except:
            pass
    
    def _log_shutdown_event(self):
        """Log shutdown event to system log"""
        try:
            log_dir = Path.home() / ".local" / "share" / "pin_auth"
            log_dir.mkdir(parents=True, exist_ok=True)
            
            log_file = log_dir / "security_events.log"
            
            with open(log_file, 'a') as f:
                timestamp = datetime.now().isoformat()
                f.write(f"{timestamp} - SECURITY SHUTDOWN: Too many failed authentication attempts\n")
                
        except Exception as e:
            logger.error(f"Failed to log shutdown event: {e}")
    
    def get_attempt_status(self, username: str) -> Dict[str, Any]:
        """
        Get detailed attempt status for user
        
        Args:
            username: Username to check
            
        Returns:
            Status dictionary
        """
        attempts = self.get_failed_attempts(username)
        
        # Determine current phase
        if attempts < self.pin_attempt_limit:
            phase = "pin"
            remaining = self.pin_attempt_limit - attempts
        elif attempts < self.total_attempt_limit:
            phase = "password"
            remaining = self.total_attempt_limit - attempts
        else:
            phase = "locked"
            remaining = 0
        
        return {
            "username": username,
            "total_attempts": attempts,
            "phase": phase,
            "remaining_attempts": remaining,
            "pin_limit": self.pin_attempt_limit,
            "password_limit": self.password_attempt_limit,
            "total_limit": self.total_attempt_limit,
            "will_shutdown": attempts >= self.total_attempt_limit
        }


def check_authentication_attempts(username: str) -> Dict[str, Any]:
    """
    Convenience function to check authentication attempts
    
    Args:
        username: Username to check
        
    Returns:
        Status and action dictionary
    """
    handler = ShutdownHandler()
    return handler.check_and_handle_attempts(username)


def reset_authentication_attempts(username: str) -> Dict[str, Any]:
    """
    Convenience function to reset authentication attempts
    
    Args:
        username: Username to reset
        
    Returns:
        Result dictionary
    """
    handler = ShutdownHandler()
    return handler.reset_attempts(username)


if __name__ == "__main__":
    # Test the shutdown handler
    import sys
    
    if len(sys.argv) > 1:
        username = sys.argv[1]
        handler = ShutdownHandler()
        
        # Get status
        status = handler.get_attempt_status(username)
        print(f"Attempt Status for {username}:")
        print(f"  Total attempts: {status['total_attempts']}")
        print(f"  Current phase: {status['phase']}")
        print(f"  Remaining attempts: {status['remaining_attempts']}")
        print(f"  Will shutdown: {status['will_shutdown']}")
        
        # Check and handle
        result = handler.check_and_handle_attempts(username)
        print(f"\nAction: {result['action']}")
        print(f"Message: {result['message']}")
    else:
        print("Usage: python shutdown_handler.py <username>")
