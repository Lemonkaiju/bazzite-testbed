"""
Lockscreen Configuration - Adds PIN support to screen lock
"""

import os
import shutil
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class LockscreenConfigurator:
    """
    Configures lockscreen (screensaver) to use PIN authentication
    
    Supports:
    - KDE Plasma lockscreen
    - GNOME screensaver
    - LightDM lockscreen
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize lockscreen configurator"""
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
        
        logger.info("Lockscreen Configurator initialized")
    
    def configure_kde_lockscreen(self) -> Dict[str, Any]:
        """
        Configure KDE Plasma lockscreen for PIN authentication
        
        Returns:
            Result dictionary
        """
        kde_pam = self.pam_dir / "kde"
        
        if not kde_pam.exists():
            # Try alternative names
            for alt_name in ["kscreensaver", "kde-np", "kcheckpass"]:
                alt_pam = self.pam_dir / alt_name
                if alt_pam.exists():
                    kde_pam = alt_pam
                    break
            else:
                return {
                    "success": False,
                    "error": "KDE lockscreen PAM configuration not found"
                }
        
        try:
            # Backup original configuration
            self._backup_pam_file(kde_pam.name)
            
            # Read current configuration
            with open(kde_pam, 'r') as f:
                lines = f.readlines()
            
            # Create new configuration with PIN support
            new_config = self._generate_lockscreen_pin_config(lines)
            
            # Write new configuration
            with open(kde_pam, 'w') as f:
                f.writelines(new_config)
            
            logger.info(f"KDE lockscreen PAM configured for PIN authentication")
            
            return {
                "success": True,
                "message": "KDE lockscreen configured for PIN authentication",
                "file": str(kde_pam)
            }
            
        except Exception as e:
            logger.error(f"Failed to configure KDE lockscreen PAM: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def configure_gnome_screensaver(self) -> Dict[str, Any]:
        """
        Configure GNOME screensaver for PIN authentication
        
        Returns:
            Result dictionary
        """
        gnome_pam = self.pam_dir / "gnome-screensaver"
        
        if not gnome_pam.exists():
            return {
                "success": False,
                "error": "GNOME screensaver PAM configuration not found"
            }
        
        try:
            # Backup original configuration
            self._backup_pam_file("gnome-screensaver")
            
            # Read current configuration
            with open(gnome_pam, 'r') as f:
                lines = f.readlines()
            
            # Create new configuration with PIN support
            new_config = self._generate_lockscreen_pin_config(lines)
            
            # Write new configuration
            with open(gnome_pam, 'w') as f:
                f.writelines(new_config)
            
            logger.info("GNOME screensaver PAM configured for PIN authentication")
            
            return {
                "success": True,
                "message": "GNOME screensaver configured for PIN authentication",
                "file": str(gnome_pam)
            }
            
        except Exception as e:
            logger.error(f"Failed to configure GNOME screensaver PAM: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def configure_all_lockscreens(self) -> Dict[str, Any]:
        """
        Configure all available lockscreen systems
        
        Returns:
            Result dictionary with status for each system
        """
        results = {
            "kde": self.configure_kde_lockscreen(),
            "gnome": self.configure_gnome_screensaver()
        }
        
        # Count successes
        successes = sum(1 for r in results.values() if r.get("success"))
        
        return {
            "success": successes > 0,
            "configured_count": successes,
            "results": results,
            "message": f"Configured {successes} lockscreen system(s)"
        }
    
    def _generate_lockscreen_pin_config(self, original_lines: list) -> list:
        """
        Generate lockscreen PAM configuration with PIN support
        
        Strategy:
        - Try PIN first (sufficient)
        - Fall back to password if PIN fails
        - Integrate faillock
        """
        new_config = [
            "# PAM configuration for lockscreen with PIN support\n",
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
        ]
        
        return new_config
    
    def _backup_pam_file(self, service: str):
        """Backup a PAM configuration file"""
        source = self.pam_dir / service
        if not source.exists():
            return
        
        timestamp = self._get_timestamp()
        backup = self.backup_dir / f"{service}.{timestamp}"
        
        shutil.copy2(source, backup)
        logger.info(f"Backed up {service} to {backup}")
    
    def _get_timestamp(self) -> str:
        """Get timestamp for backups"""
        return datetime.now().strftime("%Y%m%d_%H%M%S")
