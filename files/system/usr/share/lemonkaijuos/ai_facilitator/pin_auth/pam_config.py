"""
PAM Configurator - Manages PAM configuration for PIN authentication
"""

import os
import shutil
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class PAMConfigurator:
    """
    Configures PAM (Pluggable Authentication Modules) for PIN authentication
    
    Features:
    - Configure PAM for sudo with PIN
    - Configure PAM for GDM (login) with PIN
    - Integrate pam_faillock for attempt limiting
    - Backup and restore PAM configurations
    - Bazzite-compatible (uses /etc overlay)
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize PAM configurator"""
        self.config = config or {}
        
        # PAM configuration directories
        self.pam_dir = Path("/etc/pam.d")
        self.backup_dir = Path(self.config.get(
            "backup_dir",
            Path.home() / ".local" / "share" / "pin_auth" / "pam_backups"
        ))
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # PIN database location
        self.pin_db_path = self.config.get("pin_db_path", "/etc/pinlock")
        
        # Faillock settings
        self.max_attempts = self.config.get("max_attempts", 5)
        self.lockout_time = self.config.get("lockout_time", 600)  # 10 minutes
        
        logger.info("PAM Configurator initialized")
    
    def configure_sudo_pin(self) -> Dict[str, Any]:
        """
        Configure sudo to use PIN authentication
        
        Returns:
            Result dictionary
        """
        sudo_pam = self.pam_dir / "sudo"
        
        if not sudo_pam.exists():
            return {
                "success": False,
                "error": "sudo PAM configuration not found"
            }
        
        try:
            # Backup original configuration
            self._backup_pam_file("sudo")
            
            # Read current configuration
            with open(sudo_pam, 'r') as f:
                lines = f.readlines()
            
            # Create new configuration with PIN support
            new_config = self._generate_sudo_pin_config(lines)
            
            # Write new configuration
            with open(sudo_pam, 'w') as f:
                f.writelines(new_config)
            
            logger.info("sudo PAM configured for PIN authentication")
            
            return {
                "success": True,
                "message": "sudo configured for PIN authentication",
                "backup": str(self.backup_dir / f"sudo.{self._get_timestamp()}")
            }
            
        except Exception as e:
            logger.error(f"Failed to configure sudo PAM: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def configure_gdm_pin(self) -> Dict[str, Any]:
        """
        Configure GDM (login) to use PIN authentication
        
        Returns:
            Result dictionary
        """
        gdm_pam = self.pam_dir / "gdm-password"
        
        if not gdm_pam.exists():
            return {
                "success": False,
                "error": "gdm-password PAM configuration not found"
            }
        
        try:
            # Backup original configuration
            self._backup_pam_file("gdm-password")
            
            # Read current configuration
            with open(gdm_pam, 'r') as f:
                lines = f.readlines()
            
            # Create new configuration with PIN support
            new_config = self._generate_gdm_pin_config(lines)
            
            # Write new configuration
            with open(gdm_pam, 'w') as f:
                f.writelines(new_config)
            
            logger.info("GDM PAM configured for PIN authentication")
            
            return {
                "success": True,
                "message": "GDM configured for PIN authentication",
                "backup": str(self.backup_dir / f"gdm-password.{self._get_timestamp()}")
            }
            
        except Exception as e:
            logger.error(f"Failed to configure GDM PAM: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def configure_faillock(self) -> Dict[str, Any]:
        """
        Configure pam_faillock for login attempt limiting
        
        Returns:
            Result dictionary
        """
        try:
            # Create faillock configuration
            faillock_conf = Path("/etc/security/faillock.conf")
            
            # Backup if exists
            if faillock_conf.exists():
                self._backup_file(faillock_conf)
            
            # Generate faillock configuration
            config_content = self._generate_faillock_config()
            
            # Write configuration
            faillock_conf.parent.mkdir(parents=True, exist_ok=True)
            with open(faillock_conf, 'w') as f:
                f.write(config_content)
            
            logger.info("faillock configured")
            
            return {
                "success": True,
                "message": f"faillock configured (max {self.max_attempts} attempts)",
                "max_attempts": self.max_attempts,
                "lockout_time": self.lockout_time
            }
            
        except Exception as e:
            logger.error(f"Failed to configure faillock: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def restore_pam_config(self, service: str) -> Dict[str, Any]:
        """
        Restore PAM configuration from backup
        
        Args:
            service: Service name (sudo, gdm-password, etc.)
            
        Returns:
            Result dictionary
        """
        try:
            # Find most recent backup
            backups = sorted(self.backup_dir.glob(f"{service}.*"))
            
            if not backups:
                return {
                    "success": False,
                    "error": f"No backup found for {service}"
                }
            
            latest_backup = backups[-1]
            target = self.pam_dir / service
            
            # Restore from backup
            shutil.copy2(latest_backup, target)
            
            logger.info(f"Restored {service} PAM configuration from backup")
            
            return {
                "success": True,
                "message": f"Restored {service} configuration",
                "backup_used": str(latest_backup)
            }
            
        except Exception as e:
            logger.error(f"Failed to restore PAM config: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _generate_sudo_pin_config(self, original_lines: list) -> list:
        """
        Generate sudo PAM configuration with PIN support
        
        Strategy:
        - Try PIN first (sufficient)
        - Fall back to password if PIN fails
        - Integrate faillock
        """
        new_config = [
            "# PAM configuration for sudo with PIN support\n",
            "# Generated by LemonKaijuOS PIN Auth System\n",
            f"# Backup created: {self._get_timestamp()}\n",
            "\n",
            "# Faillock for attempt limiting\n",
            "auth       required   pam_faillock.so preauth\n",
            "\n",
            "# Try PIN authentication first (sufficient - no password needed if PIN works)\n",
            f"auth       sufficient pam_unix.so try_first_pass nullok_secure pinfile={self.pin_db_path}\n",
            "\n",
            "# Fall back to regular password authentication\n",
            "auth       required   pam_unix.so\n",
            "\n",
            "# Update faillock on authentication result\n",
            "auth       required   pam_faillock.so authfail\n",
            "\n",
            "# Account management\n",
            "account    required   pam_unix.so\n",
            "account    required   pam_faillock.so\n",
            "\n",
            "# Session management\n",
            "session    required   pam_unix.so\n",
            "\n",
            "# Password management\n",
            "password   required   pam_unix.so\n",
        ]
        
        return new_config
    
    def _generate_gdm_pin_config(self, original_lines: list) -> list:
        """
        Generate GDM PAM configuration with PIN support
        
        Strategy:
        - Try PIN first (sufficient)
        - Fall back to password if PIN fails
        - Integrate faillock with lockout
        """
        new_config = [
            "# PAM configuration for GDM with PIN support\n",
            "# Generated by LemonKaijuOS PIN Auth System\n",
            f"# Backup created: {self._get_timestamp()}\n",
            "\n",
            "# Faillock for attempt limiting\n",
            "auth       required   pam_faillock.so preauth silent\n",
            "\n",
            "# Try PIN authentication first\n",
            f"auth       sufficient pam_unix.so try_first_pass nullok_secure pinfile={self.pin_db_path}\n",
            "\n",
            "# Fall back to regular password authentication\n",
            "auth       required   pam_unix.so\n",
            "\n",
            "# Update faillock on authentication result\n",
            "auth       required   pam_faillock.so authfail\n",
            "\n",
            "# Account management\n",
            "account    required   pam_unix.so\n",
            "account    required   pam_faillock.so\n",
            "\n",
            "# Session management\n",
            "session    required   pam_unix.so\n",
            "session    optional   pam_gnome_keyring.so auto_start\n",
            "\n",
            "# Password management\n",
            "password   required   pam_unix.so\n",
        ]
        
        return new_config
    
    def _generate_faillock_config(self) -> str:
        """Generate faillock configuration"""
        return f"""# Faillock configuration for LemonKaijuOS PIN Auth
# Generated: {self._get_timestamp()}

# Number of failed attempts before lockout
deny = {self.max_attempts}

# Lockout duration in seconds (0 = permanent until admin unlock)
unlock_time = {self.lockout_time}

# Also count root failures
even_deny_root

# Audit failed attempts
audit

# Silent mode (don't display failure count to user)
silent

# Log to syslog
syslog
"""
    
    def _backup_pam_file(self, service: str):
        """Backup a PAM configuration file"""
        source = self.pam_dir / service
        if not source.exists():
            return
        
        timestamp = self._get_timestamp()
        backup = self.backup_dir / f"{service}.{timestamp}"
        
        shutil.copy2(source, backup)
        logger.info(f"Backed up {service} to {backup}")
    
    def _backup_file(self, filepath: Path):
        """Backup any file"""
        if not filepath.exists():
            return
        
        timestamp = self._get_timestamp()
        backup = self.backup_dir / f"{filepath.name}.{timestamp}"
        
        shutil.copy2(filepath, backup)
        logger.info(f"Backed up {filepath} to {backup}")
    
    def _get_timestamp(self) -> str:
        """Get timestamp for backups"""
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def list_backups(self) -> list:
        """List all PAM configuration backups"""
        backups = []
        for backup_file in sorted(self.backup_dir.glob("*")):
            backups.append({
                "file": backup_file.name,
                "path": str(backup_file),
                "size": backup_file.stat().st_size,
                "modified": datetime.fromtimestamp(backup_file.stat().st_mtime).isoformat()
            })
        return backups
    
    def get_current_config(self, service: str) -> Optional[str]:
        """Get current PAM configuration for a service"""
        pam_file = self.pam_dir / service
        if not pam_file.exists():
            return None
        
        try:
            with open(pam_file, 'r') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to read PAM config: {e}")
            return None
    
    def verify_pin_support(self) -> Dict[str, Any]:
        """Verify that PIN authentication is properly configured"""
        checks = {
            "sudo_configured": False,
            "gdm_configured": False,
            "faillock_configured": False,
            "pin_db_exists": False
        }
        
        # Check sudo configuration
        sudo_config = self.get_current_config("sudo")
        if sudo_config and "pinfile=" in sudo_config:
            checks["sudo_configured"] = True
        
        # Check GDM configuration
        gdm_config = self.get_current_config("gdm-password")
        if gdm_config and "pinfile=" in gdm_config:
            checks["gdm_configured"] = True
        
        # Check faillock configuration
        faillock_conf = Path("/etc/security/faillock.conf")
        if faillock_conf.exists():
            checks["faillock_configured"] = True
        
        # Check PIN database directory
        pin_db = Path(self.pin_db_path)
        if pin_db.exists():
            checks["pin_db_exists"] = True
        
        all_configured = all(checks.values())
        
        return {
            "configured": all_configured,
            "checks": checks,
            "message": "PIN authentication fully configured" if all_configured else "PIN authentication not fully configured"
        }
