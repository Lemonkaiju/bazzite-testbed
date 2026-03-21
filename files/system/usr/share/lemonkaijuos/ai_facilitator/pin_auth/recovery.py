"""
Recovery Manager - Handles PIN recovery and reset workflows
"""

import logging
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from .pin_manager import PINManager

logger = logging.getLogger(__name__)


class RecoveryManager:
    """
    Manages PIN recovery and reset workflows
    
    Features:
    - Reset PIN using long privacy password
    - Emergency recovery procedures
    - Unlock after failed attempts
    - Recovery code generation
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize recovery manager"""
        self.config = config or {}
        self.pin_manager = PINManager(config)
        
        # Recovery codes storage
        self.recovery_dir = Path(self.config.get(
            "recovery_dir",
            Path.home() / ".local" / "share" / "pin_auth" / "recovery"
        ))
        self.recovery_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("Recovery Manager initialized")
    
    def reset_pin_with_password(
        self,
        username: str,
        password: str,
        new_pin: str,
        verify_new_pin: str
    ) -> Dict[str, Any]:
        """
        Reset PIN using long privacy password
        
        Args:
            username: Username
            password: User's long privacy password
            new_pin: New 6-digit PIN
            verify_new_pin: New PIN verification
            
        Returns:
            Result dictionary
        """
        # Verify password using PAM
        if not self._verify_password(username, password):
            return {
                "success": False,
                "error": "Password verification failed"
            }
        
        # Create new PIN
        result = self.pin_manager.create_pin(username, new_pin, verify_new_pin)
        
        if result['success']:
            logger.info(f"PIN reset for {username} using password")
            return {
                "success": True,
                "message": "PIN reset successfully"
            }
        else:
            return result
    
    def unlock_after_failed_attempts(self, username: str, password: str) -> Dict[str, Any]:
        """
        Unlock account after failed PIN attempts
        Requires long privacy password
        
        Args:
            username: Username
            password: User's long privacy password
            
        Returns:
            Result dictionary
        """
        # Verify password
        if not self._verify_password(username, password):
            return {
                "success": False,
                "error": "Password verification failed"
            }
        
        # Reset faillock counter
        try:
            result = subprocess.run(
                ["faillock", "--user", username, "--reset"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                logger.info(f"Faillock reset for {username}")
                return {
                    "success": True,
                    "message": "Account unlocked successfully"
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to reset faillock: {result.stderr}"
                }
                
        except Exception as e:
            logger.error(f"Failed to unlock account: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_recovery_code(self, username: str) -> Dict[str, Any]:
        """
        Generate a one-time recovery code for PIN reset
        
        Args:
            username: Username
            
        Returns:
            Result dictionary with recovery code
        """
        import secrets
        import json
        
        # Generate secure random recovery code
        recovery_code = ''.join([
            secrets.choice('ABCDEFGHJKLMNPQRSTUVWXYZ23456789')
            for _ in range(16)
        ])
        
        # Format as XXXX-XXXX-XXXX-XXXX
        formatted_code = '-'.join([
            recovery_code[i:i+4]
            for i in range(0, 16, 4)
        ])
        
        # Store recovery code (hashed)
        import hashlib
        code_hash = hashlib.sha256(recovery_code.encode()).hexdigest()
        
        recovery_file = self.recovery_dir / f"{username}.json"
        recovery_data = {
            "username": username,
            "code_hash": code_hash,
            "generated": datetime.now().isoformat(),
            "used": False
        }
        
        try:
            with open(recovery_file, 'w') as f:
                json.dump(recovery_data, f, indent=2)
            
            # Set restrictive permissions
            import os
            os.chmod(recovery_file, 0o600)
            
            logger.info(f"Recovery code generated for {username}")
            
            return {
                "success": True,
                "recovery_code": formatted_code,
                "message": "Store this recovery code in a safe place. It can be used once to reset your PIN."
            }
            
        except Exception as e:
            logger.error(f"Failed to generate recovery code: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def reset_pin_with_recovery_code(
        self,
        username: str,
        recovery_code: str,
        new_pin: str,
        verify_new_pin: str
    ) -> Dict[str, Any]:
        """
        Reset PIN using recovery code
        
        Args:
            username: Username
            recovery_code: Recovery code (with or without dashes)
            new_pin: New 6-digit PIN
            verify_new_pin: New PIN verification
            
        Returns:
            Result dictionary
        """
        import json
        import hashlib
        
        # Remove dashes from recovery code
        recovery_code = recovery_code.replace('-', '').upper()
        
        # Load recovery data
        recovery_file = self.recovery_dir / f"{username}.json"
        
        if not recovery_file.exists():
            return {
                "success": False,
                "error": "No recovery code found for this user"
            }
        
        try:
            with open(recovery_file, 'r') as f:
                recovery_data = json.load(f)
            
            # Check if already used
            if recovery_data.get('used', False):
                return {
                    "success": False,
                    "error": "Recovery code has already been used"
                }
            
            # Verify recovery code
            code_hash = hashlib.sha256(recovery_code.encode()).hexdigest()
            if code_hash != recovery_data.get('code_hash'):
                return {
                    "success": False,
                    "error": "Invalid recovery code"
                }
            
            # Create new PIN
            result = self.pin_manager.create_pin(username, new_pin, verify_new_pin)
            
            if result['success']:
                # Mark recovery code as used
                recovery_data['used'] = True
                recovery_data['used_at'] = datetime.now().isoformat()
                
                with open(recovery_file, 'w') as f:
                    json.dump(recovery_data, f, indent=2)
                
                logger.info(f"PIN reset for {username} using recovery code")
                
                return {
                    "success": True,
                    "message": "PIN reset successfully using recovery code"
                }
            else:
                return result
                
        except Exception as e:
            logger.error(f"Failed to reset PIN with recovery code: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def emergency_disable_pin(self, username: str) -> Dict[str, Any]:
        """
        Emergency disable PIN authentication
        Falls back to password-only authentication
        
        Args:
            username: Username
            
        Returns:
            Result dictionary
        """
        try:
            # Remove PIN
            pin_file = Path(self.pin_manager.pin_db_dir) / username
            if pin_file.exists():
                pin_file.unlink()
            
            # Reset faillock
            subprocess.run(
                ["faillock", "--user", username, "--reset"],
                capture_output=True,
                timeout=10
            )
            
            logger.warning(f"Emergency PIN disable for {username}")
            
            return {
                "success": True,
                "message": "PIN authentication disabled. Use password to login."
            }
            
        except Exception as e:
            logger.error(f"Failed to disable PIN: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_faillock_status(self, username: str) -> Dict[str, Any]:
        """
        Get current faillock status for user
        
        Args:
            username: Username
            
        Returns:
            Status dictionary
        """
        try:
            result = subprocess.run(
                ["faillock", "--user", username],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                output = result.stdout
                
                # Parse faillock output
                locked = "locked" in output.lower()
                
                return {
                    "username": username,
                    "locked": locked,
                    "output": output
                }
            else:
                return {
                    "username": username,
                    "locked": False,
                    "error": "Could not determine lock status"
                }
                
        except Exception as e:
            logger.error(f"Failed to get faillock status: {e}")
            return {
                "username": username,
                "locked": False,
                "error": str(e)
            }
    
    def _verify_password(self, username: str, password: str) -> bool:
        """
        Verify user's long privacy password using PAM
        
        Args:
            username: Username
            password: Password to verify
            
        Returns:
            True if password is correct
        """
        try:
            # Use pamela or python-pam for PAM authentication
            # For now, we'll use a subprocess approach with su
            result = subprocess.run(
                ["su", "-c", "true", username],
                input=password.encode(),
                capture_output=True,
                timeout=10
            )
            
            return result.returncode == 0
            
        except Exception as e:
            logger.error(f"Password verification failed: {e}")
            return False
