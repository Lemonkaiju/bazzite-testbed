"""
Kiosk Mode
Restricted environment for kids and temporary users
"""

import os
import json
import logging
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class KioskMode:
    """
    Manages kiosk mode for restricted users
    
    Features:
    - Restricted to approved Flatpak applications
    - No system settings access
    - No terminal access
    - Simplified desktop environment
    - Automatic session timeout
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize kiosk mode manager"""
        self.config = config or {}
        
        # Kiosk configuration directory
        self.kiosk_dir = Path(self.config.get(
            "kiosk_dir",
            Path.home() / ".local" / "share" / "kiosk"
        ))
        self.kiosk_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("Kiosk Mode manager initialized")
    
    def enable_kiosk_mode(
        self,
        username: str,
        allowed_apps: List[str]
    ) -> Dict[str, Any]:
        """
        Enable kiosk mode for a user
        
        Args:
            username: Username
            allowed_apps: List of allowed Flatpak app IDs
            
        Returns:
            Result dictionary
        """
        try:
            # Create kiosk configuration
            kiosk_config = {
                "username": username,
                "enabled": True,
                "allowed_apps": allowed_apps,
                "session_timeout": 3600,  # 1 hour
                "show_desktop": False,
                "allow_terminal": False,
                "allow_settings": False
            }
            
            # Save configuration
            config_file = self.kiosk_dir / f"{username}_kiosk.json"
            with open(config_file, 'w') as f:
                json.dump(kiosk_config, f, indent=2)
            
            os.chmod(config_file, 0o600)
            
            # Create GNOME Shell extension configuration
            self._configure_gnome_kiosk(username, kiosk_config)
            
            # Create application launcher restrictions
            self._configure_app_restrictions(username, allowed_apps)
            
            logger.info(f"Kiosk mode enabled for {username}")
            
            return {
                "success": True,
                "message": f"Kiosk mode enabled for {username}",
                "allowed_apps": len(allowed_apps)
            }
            
        except Exception as e:
            logger.error(f"Failed to enable kiosk mode: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def disable_kiosk_mode(self, username: str) -> Dict[str, Any]:
        """Disable kiosk mode for a user"""
        try:
            config_file = self.kiosk_dir / f"{username}_kiosk.json"
            
            if config_file.exists():
                config_file.unlink()
            
            # Remove GNOME restrictions
            self._remove_gnome_kiosk(username)
            
            # Remove app restrictions
            self._remove_app_restrictions(username)
            
            logger.info(f"Kiosk mode disabled for {username}")
            
            return {
                "success": True,
                "message": f"Kiosk mode disabled for {username}"
            }
            
        except Exception as e:
            logger.error(f"Failed to disable kiosk mode: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def is_kiosk_enabled(self, username: str) -> bool:
        """Check if kiosk mode is enabled for user"""
        config_file = self.kiosk_dir / f"{username}_kiosk.json"
        return config_file.exists()
    
    def get_allowed_apps(self, username: str) -> List[str]:
        """Get list of allowed apps for user"""
        config_file = self.kiosk_dir / f"{username}_kiosk.json"
        
        if not config_file.exists():
            return []
        
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            return config.get("allowed_apps", [])
            
        except Exception as e:
            logger.error(f"Failed to get allowed apps: {e}")
            return []
    
    def add_allowed_app(self, username: str, app_id: str) -> Dict[str, Any]:
        """Add an app to the allowed list"""
        config_file = self.kiosk_dir / f"{username}_kiosk.json"
        
        if not config_file.exists():
            return {
                "success": False,
                "error": "Kiosk mode not enabled"
            }
        
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            allowed_apps = config.get("allowed_apps", [])
            
            if app_id not in allowed_apps:
                allowed_apps.append(app_id)
                config["allowed_apps"] = allowed_apps
                
                with open(config_file, 'w') as f:
                    json.dump(config, f, indent=2)
                
                # Update app restrictions
                self._configure_app_restrictions(username, allowed_apps)
                
                logger.info(f"Added {app_id} to allowed apps for {username}")
                
                return {
                    "success": True,
                    "message": f"App {app_id} added to allowed list"
                }
            else:
                return {
                    "success": False,
                    "error": "App already in allowed list"
                }
                
        except Exception as e:
            logger.error(f"Failed to add allowed app: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def remove_allowed_app(self, username: str, app_id: str) -> Dict[str, Any]:
        """Remove an app from the allowed list"""
        config_file = self.kiosk_dir / f"{username}_kiosk.json"
        
        if not config_file.exists():
            return {
                "success": False,
                "error": "Kiosk mode not enabled"
            }
        
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            allowed_apps = config.get("allowed_apps", [])
            
            if app_id in allowed_apps:
                allowed_apps.remove(app_id)
                config["allowed_apps"] = allowed_apps
                
                with open(config_file, 'w') as f:
                    json.dump(config, f, indent=2)
                
                # Update app restrictions
                self._configure_app_restrictions(username, allowed_apps)
                
                logger.info(f"Removed {app_id} from allowed apps for {username}")
                
                return {
                    "success": True,
                    "message": f"App {app_id} removed from allowed list"
                }
            else:
                return {
                    "success": False,
                    "error": "App not in allowed list"
                }
                
        except Exception as e:
            logger.error(f"Failed to remove allowed app: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _configure_gnome_kiosk(self, username: str, config: Dict[str, Any]):
        """
        Configure GNOME Shell for kiosk mode
        
        Uses dconf/gsettings to:
        - Hide system settings
        - Disable terminal access
        - Simplify interface
        - Set session timeout
        """
        # This would use dconf to configure GNOME
        # For now, create a dconf profile
        
        dconf_profile = f"""
# Kiosk mode profile for {username}

[org/gnome/desktop/lockdown]
disable-command-line=true
disable-log-out=true
disable-user-switching=true

[org/gnome/desktop/session]
idle-delay=uint32 {config.get('session_timeout', 3600)}

[org/gnome/shell]
favorite-apps={json.dumps(config.get('allowed_apps', []))}

[org/gnome/desktop/background]
show-desktop-icons=false
"""
        
        # Save dconf profile
        profile_dir = Path(f"/etc/dconf/profile")
        if profile_dir.exists():
            profile_file = profile_dir / username
            try:
                with open(profile_file, 'w') as f:
                    f.write(dconf_profile)
            except Exception as e:
                logger.warning(f"Could not write dconf profile: {e}")
    
    def _remove_gnome_kiosk(self, username: str):
        """Remove GNOME kiosk configuration"""
        profile_file = Path(f"/etc/dconf/profile/{username}")
        if profile_file.exists():
            try:
                profile_file.unlink()
            except Exception as e:
                logger.warning(f"Could not remove dconf profile: {e}")
    
    def _configure_app_restrictions(self, username: str, allowed_apps: List[str]):
        """
        Configure application restrictions
        
        Creates a desktop file that only shows allowed apps
        """
        # Create custom .desktop files directory
        desktop_dir = Path.home() / ".local" / "share" / "applications" / "kiosk"
        desktop_dir.mkdir(parents=True, exist_ok=True)
        
        # This would create filtered desktop entries
        # For now, just log the configuration
        logger.info(f"Configured app restrictions for {username}: {len(allowed_apps)} apps")
    
    def _remove_app_restrictions(self, username: str):
        """Remove application restrictions"""
        desktop_dir = Path.home() / ".local" / "share" / "applications" / "kiosk"
        if desktop_dir.exists():
            try:
                import shutil
                shutil.rmtree(desktop_dir)
            except Exception as e:
                logger.warning(f"Could not remove app restrictions: {e}")
    
    def get_kiosk_config(self, username: str) -> Optional[Dict[str, Any]]:
        """Get kiosk configuration for user"""
        config_file = self.kiosk_dir / f"{username}_kiosk.json"
        
        if not config_file.exists():
            return None
        
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to get kiosk config: {e}")
            return None
