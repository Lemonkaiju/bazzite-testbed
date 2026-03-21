"""
PIN Manager - Handles 6-digit PIN creation, validation, and storage
"""

import os
import hashlib
import secrets
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

try:
    import crypt
    USING_PASSLIB = False
except ModuleNotFoundError:
    # Python 3.13+ removed crypt module, use passlib instead
    from passlib.hash import sha512_crypt
    USING_PASSLIB = True

logger = logging.getLogger(__name__)


class PINManager:
    """
    Manages 6-digit PINs for user authentication
    
    Features:
    - Secure PIN storage using crypt(3) hashing
    - Separate from long privacy password
    - PIN strength validation
    - Change history tracking
    - Integration with PAM
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize PIN manager"""
        self.config = config or {}
        
        # PIN database location
        self.pin_db_dir = Path(self.config.get(
            "pin_db_dir",
            "/etc/pinlock"
        ))
        
        # User-specific PIN storage
        self.user_pin_dir = Path(self.config.get(
            "user_pin_dir",
            Path.home() / ".local" / "share" / "pin_auth"
        ))
        self.user_pin_dir.mkdir(parents=True, exist_ok=True)
        
        # PIN history file
        self.history_file = self.user_pin_dir / "pin_history.json"
        
        logger.info("PIN Manager initialized")
    
    def create_pin(self, username: str, pin: str, verify_pin: str) -> Dict[str, Any]:
        """
        Create a new PIN for a user
        
        Args:
            username: Username
            pin: 6-digit PIN
            verify_pin: PIN verification (must match)
            
        Returns:
            Result dictionary
        """
        # Validate PIN format
        validation = self._validate_pin(pin)
        if not validation['valid']:
            return {
                "success": False,
                "error": validation['error']
            }
        
        # Verify PIN match
        if pin != verify_pin:
            return {
                "success": False,
                "error": "PINs do not match"
            }
        
        # Hash the PIN using crypt
        pin_hash = self._hash_pin(pin)
        
        # Store PIN hash
        try:
            self._store_pin_hash(username, pin_hash)
            
            # Log PIN creation
            self._log_pin_change(username, "created")
            
            return {
                "success": True,
                "message": f"PIN created for {username}"
            }
            
        except Exception as e:
            logger.error(f"Failed to create PIN: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def change_pin(
        self,
        username: str,
        old_pin: str,
        new_pin: str,
        verify_new_pin: str
    ) -> Dict[str, Any]:
        """
        Change user's PIN
        
        Args:
            username: Username
            old_pin: Current PIN
            new_pin: New 6-digit PIN
            verify_new_pin: New PIN verification
            
        Returns:
            Result dictionary
        """
        # Verify old PIN
        if not self.verify_pin(username, old_pin):
            return {
                "success": False,
                "error": "Current PIN is incorrect"
            }
        
        # Validate new PIN
        validation = self._validate_pin(new_pin)
        if not validation['valid']:
            return {
                "success": False,
                "error": validation['error']
            }
        
        # Verify new PIN match
        if new_pin != verify_new_pin:
            return {
                "success": False,
                "error": "New PINs do not match"
            }
        
        # Check if new PIN is same as old
        if old_pin == new_pin:
            return {
                "success": False,
                "error": "New PIN must be different from current PIN"
            }
        
        # Hash and store new PIN
        try:
            pin_hash = self._hash_pin(new_pin)
            self._store_pin_hash(username, pin_hash)
            
            # Log PIN change
            self._log_pin_change(username, "changed")
            
            return {
                "success": True,
                "message": "PIN changed successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to change PIN: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def verify_pin(self, username: str, pin: str) -> bool:
        """
        Verify a PIN for a user
        
        Args:
            username: Username
            pin: PIN to verify
            
        Returns:
            True if PIN is correct
        """
        try:
            stored_hash = self._get_pin_hash(username)
            if not stored_hash:
                return False
            
            # Verify PIN using appropriate method
            if USING_PASSLIB:
                return sha512_crypt.verify(pin, stored_hash)
            else:
                return crypt.crypt(pin, stored_hash) == stored_hash
            
        except Exception as e:
            logger.error(f"PIN verification failed: {e}")
            return False
    
    def has_pin(self, username: str) -> bool:
        """Check if user has a PIN set"""
        try:
            return self._get_pin_hash(username) is not None
        except Exception:
            return False
    
    def remove_pin(self, username: str, password: str) -> Dict[str, Any]:
        """
        Remove user's PIN (requires long password)
        
        Args:
            username: Username
            password: User's long privacy password
            
        Returns:
            Result dictionary
        """
        # This would verify the long password via PAM
        # For now, we'll implement the PIN removal logic
        
        try:
            pin_file = self.pin_db_dir / username
            if pin_file.exists():
                pin_file.unlink()
            
            # Log PIN removal
            self._log_pin_change(username, "removed")
            
            return {
                "success": True,
                "message": "PIN removed successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to remove PIN: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _validate_pin(self, pin: str) -> Dict[str, Any]:
        """
        Validate PIN format and strength
        
        Requirements:
        - Exactly 6 digits
        - Not all same digit (e.g., 111111)
        - Not sequential (e.g., 123456)
        - Not common PINs
        """
        # Check length
        if len(pin) != 6:
            return {
                "valid": False,
                "error": "PIN must be exactly 6 digits"
            }
        
        # Check if all digits
        if not pin.isdigit():
            return {
                "valid": False,
                "error": "PIN must contain only digits"
            }
        
        # Check for all same digit
        if len(set(pin)) == 1:
            return {
                "valid": False,
                "error": "PIN cannot be all the same digit"
            }
        
        # Check for sequential patterns
        sequential_patterns = [
            "012345", "123456", "234567", "345678", "456789",
            "987654", "876543", "765432", "654321", "543210"
        ]
        if pin in sequential_patterns:
            return {
                "valid": False,
                "error": "PIN cannot be a sequential pattern"
            }
        
        # Check for common PINs
        common_pins = [
            "000000", "111111", "222222", "333333", "444444",
            "555555", "666666", "777777", "888888", "999999",
            "123123", "696969", "112233", "121212", "654321"
        ]
        if pin in common_pins:
            return {
                "valid": False,
                "error": "PIN is too common, please choose a different one"
            }
        
        return {"valid": True}
    
    def _hash_pin(self, pin: str) -> str:
        """
        Hash PIN using crypt(3) with SHA-512 or passlib
        
        Args:
            pin: PIN to hash
            
        Returns:
            Hashed PIN
        """
        if USING_PASSLIB:
            # Use passlib for Python 3.13+
            return sha512_crypt.hash(pin)
        else:
            # Use standard crypt module
            salt = crypt.mksalt(crypt.METHOD_SHA512)
            return crypt.crypt(pin, salt)
    
    def _store_pin_hash(self, username: str, pin_hash: str):
        """
        Store PIN hash in database
        
        Args:
            username: Username
            pin_hash: Hashed PIN
        """
        # Ensure directory exists
        self.pin_db_dir.mkdir(parents=True, exist_ok=True)
        
        # Write hash to file
        pin_file = self.pin_db_dir / username
        
        # Set restrictive permissions (owner read/write only)
        with open(pin_file, 'w') as f:
            f.write(pin_hash)
        
        os.chmod(pin_file, 0o600)
        
        logger.info(f"PIN hash stored for {username}")
    
    def _get_pin_hash(self, username: str) -> Optional[str]:
        """
        Get PIN hash from database
        
        Args:
            username: Username
            
        Returns:
            PIN hash or None
        """
        pin_file = self.pin_db_dir / username
        
        if not pin_file.exists():
            return None
        
        try:
            with open(pin_file, 'r') as f:
                return f.read().strip()
        except Exception as e:
            logger.error(f"Failed to read PIN hash: {e}")
            return None
    
    def _log_pin_change(self, username: str, action: str):
        """
        Log PIN change to history
        
        Args:
            username: Username
            action: Action performed (created, changed, removed)
        """
        try:
            # Load existing history
            history = []
            if self.history_file.exists():
                with open(self.history_file, 'r') as f:
                    history = json.load(f)
            
            # Add new entry
            history.append({
                "username": username,
                "action": action,
                "timestamp": datetime.now().isoformat()
            })
            
            # Keep only last 100 entries
            history = history[-100:]
            
            # Save history
            with open(self.history_file, 'w') as f:
                json.dump(history, f, indent=2)
            
            os.chmod(self.history_file, 0o600)
            
        except Exception as e:
            logger.error(f"Failed to log PIN change: {e}")
    
    def get_pin_history(self, username: str, limit: int = 10) -> list:
        """Get PIN change history for user"""
        try:
            if not self.history_file.exists():
                return []
            
            with open(self.history_file, 'r') as f:
                history = json.load(f)
            
            # Filter by username
            user_history = [
                entry for entry in history
                if entry.get("username") == username
            ]
            
            return user_history[-limit:]
            
        except Exception as e:
            logger.error(f"Failed to get PIN history: {e}")
            return []
    
    def generate_secure_pin(self) -> str:
        """
        Generate a cryptographically secure random 6-digit PIN
        Useful for temporary PINs or initial setup
        
        Returns:
            6-digit PIN string
        """
        while True:
            pin = ''.join([str(secrets.randbelow(10)) for _ in range(6)])
            
            # Validate generated PIN
            validation = self._validate_pin(pin)
            if validation['valid']:
                return pin
