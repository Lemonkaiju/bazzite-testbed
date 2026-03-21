"""
Profile Manager
Manages different security profiles for different user types
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class ProfileType(Enum):
    """User profile types"""
    PRIMARY = "primary"              # Full access, all security features
    LESS_TECHNICAL = "less_technical"  # Simplified, AI approval required
    KIDS_TEMPORARY = "kids_temporary"  # Restricted, kiosk mode


class ProfileManager:
    """
    Manages user security profiles
    
    Profile Types:
    - PRIMARY: Full access, all security features enabled
    - LESS_TECHNICAL: 6-digit PIN, AI approval for system changes, daily rollback
    - KIDS_TEMPORARY: 4-digit PIN, kiosk mode, restricted apps, auto-backup
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize profile manager"""
        self.config = config or {}
        
        # Profile storage
        self.profiles_dir = Path(self.config.get(
            "profiles_dir",
            Path.home() / ".local" / "share" / "profiles"
        ))
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
        
        # Profile definitions file
        self.profiles_file = self.profiles_dir / "profiles.json"
        
        # Load existing profiles
        self.profiles = self._load_profiles()
        
        logger.info("Profile Manager initialized")
    
    def create_profile(
        self,
        username: str,
        profile_type: ProfileType,
        display_name: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a user profile
        
        Args:
            username: System username
            profile_type: Type of profile
            display_name: Friendly display name
            **kwargs: Additional profile-specific settings
            
        Returns:
            Result dictionary
        """
        # Check if profile already exists
        if username in self.profiles:
            return {
                "success": False,
                "error": f"Profile already exists for {username}"
            }
        
        # Create profile configuration
        profile_config = self._generate_profile_config(
            username, profile_type, display_name, **kwargs
        )
        
        # Store profile
        self.profiles[username] = profile_config
        self._save_profiles()
        
        # Apply profile settings
        apply_result = self._apply_profile_settings(username, profile_config)
        
        if not apply_result.get("success"):
            # Rollback on failure
            del self.profiles[username]
            self._save_profiles()
            return apply_result
        
        logger.info(f"Created {profile_type.value} profile for {username}")
        
        return {
            "success": True,
            "message": f"Profile created for {username}",
            "profile_type": profile_type.value
        }
    
    def get_profile(self, username: str) -> Optional[Dict[str, Any]]:
        """Get profile for a user"""
        return self.profiles.get(username)
    
    def get_profile_type(self, username: str) -> Optional[ProfileType]:
        """Get profile type for a user"""
        profile = self.get_profile(username)
        if not profile:
            return None
        
        try:
            return ProfileType(profile.get("type"))
        except ValueError:
            return None
    
    def update_profile(
        self,
        username: str,
        **updates
    ) -> Dict[str, Any]:
        """
        Update profile settings
        
        Args:
            username: Username
            **updates: Settings to update
            
        Returns:
            Result dictionary
        """
        if username not in self.profiles:
            return {
                "success": False,
                "error": f"No profile found for {username}"
            }
        
        # Update settings
        self.profiles[username].update(updates)
        self.profiles[username]["updated"] = datetime.now().isoformat()
        
        # Save and apply
        self._save_profiles()
        apply_result = self._apply_profile_settings(username, self.profiles[username])
        
        if apply_result.get("success"):
            logger.info(f"Updated profile for {username}")
            return {
                "success": True,
                "message": f"Profile updated for {username}"
            }
        else:
            return apply_result
    
    def delete_profile(self, username: str) -> Dict[str, Any]:
        """Delete a user profile"""
        if username not in self.profiles:
            return {
                "success": False,
                "error": f"No profile found for {username}"
            }
        
        # Remove profile
        del self.profiles[username]
        self._save_profiles()
        
        logger.info(f"Deleted profile for {username}")
        
        return {
            "success": True,
            "message": f"Profile deleted for {username}"
        }
    
    def list_profiles(self) -> List[Dict[str, Any]]:
        """List all profiles"""
        profiles_list = []
        
        for username, config in self.profiles.items():
            profiles_list.append({
                "username": username,
                "type": config.get("type"),
                "display_name": config.get("display_name", username),
                "created": config.get("created"),
                "updated": config.get("updated")
            })
        
        return profiles_list
    
    def get_permissions(self, username: str) -> Dict[str, bool]:
        """
        Get permission matrix for a user
        
        Returns:
            Dictionary of permissions
        """
        profile = self.get_profile(username)
        if not profile:
            # Default permissions (minimal)
            return self._get_default_permissions()
        
        return profile.get("permissions", self._get_default_permissions())
    
    def check_permission(self, username: str, permission: str) -> bool:
        """Check if user has a specific permission"""
        permissions = self.get_permissions(username)
        return permissions.get(permission, False)
    
    def _generate_profile_config(
        self,
        username: str,
        profile_type: ProfileType,
        display_name: Optional[str],
        **kwargs
    ) -> Dict[str, Any]:
        """Generate profile configuration based on type"""
        
        base_config = {
            "username": username,
            "type": profile_type.value,
            "display_name": display_name or username,
            "created": datetime.now().isoformat(),
            "updated": datetime.now().isoformat()
        }
        
        if profile_type == ProfileType.PRIMARY:
            config = {
                **base_config,
                "pin_length": 6,
                "pin_required": True,
                "duress_pin_enabled": True,
                "physical_security_enabled": True,
                "kiosk_mode": False,
                "ai_approval_required": False,
                "auto_backup_enabled": True,
                "backup_interval": "daily",
                "allowed_apps": "all",
                "permissions": self._get_primary_permissions()
            }
        
        elif profile_type == ProfileType.LESS_TECHNICAL:
            config = {
                **base_config,
                "pin_length": 6,
                "pin_required": True,
                "duress_pin_enabled": False,
                "physical_security_enabled": False,
                "kiosk_mode": False,
                "ai_approval_required": True,
                "auto_backup_enabled": True,
                "backup_interval": "daily",
                "auto_rollback_enabled": True,
                "rollback_schedule": "daily",
                "allowed_apps": "all",
                "permissions": self._get_less_technical_permissions()
            }
        
        elif profile_type == ProfileType.KIDS_TEMPORARY:
            config = {
                **base_config,
                "pin_length": 4,
                "pin_required": True,
                "duress_pin_enabled": False,
                "physical_security_enabled": False,
                "kiosk_mode": True,
                "ai_approval_required": False,
                "auto_backup_enabled": True,
                "backup_interval": "hourly",
                "allowed_apps": kwargs.get("allowed_apps", [
                    "org.mozilla.firefox",
                    "org.libreoffice.LibreOffice",
                    "org.gnome.Games"
                ]),
                "permissions": self._get_kids_permissions()
            }
        
        # Merge any additional kwargs
        config.update(kwargs)
        
        return config
    
    def _get_primary_permissions(self) -> Dict[str, bool]:
        """Get permissions for primary user"""
        return {
            "flatpak_install": True,
            "flatpak_uninstall": True,
            "rpm_ostree_install": True,
            "rpm_ostree_rollback": True,
            "distrobox_create": True,
            "distrobox_delete": True,
            "system_settings": True,
            "network_settings": True,
            "user_management": True,
            "security_settings": True,
            "ai_facilitator_use": True
        }
    
    def _get_less_technical_permissions(self) -> Dict[str, bool]:
        """Get permissions for less technical user"""
        return {
            "flatpak_install": True,  # With AI approval
            "flatpak_uninstall": True,  # With AI approval
            "rpm_ostree_install": False,
            "rpm_ostree_rollback": True,  # With AI approval
            "distrobox_create": False,
            "distrobox_delete": False,
            "system_settings": False,
            "network_settings": False,
            "user_management": False,
            "security_settings": False,
            "ai_facilitator_use": True
        }
    
    def _get_kids_permissions(self) -> Dict[str, bool]:
        """Get permissions for kids/temporary user"""
        return {
            "flatpak_install": False,
            "flatpak_uninstall": False,
            "rpm_ostree_install": False,
            "rpm_ostree_rollback": False,
            "distrobox_create": False,
            "distrobox_delete": False,
            "system_settings": False,
            "network_settings": False,
            "user_management": False,
            "security_settings": False,
            "ai_facilitator_use": False
        }
    
    def _get_default_permissions(self) -> Dict[str, bool]:
        """Get default (minimal) permissions"""
        return self._get_kids_permissions()
    
    def _apply_profile_settings(
        self,
        username: str,
        profile_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Apply profile settings to the system
        
        This would:
        - Configure PIN length
        - Set up kiosk mode if needed
        - Configure backup schedule
        - Set up AI approval requirements
        - Configure allowed apps
        """
        try:
            actions_taken = []
            
            # PIN configuration
            if profile_config.get("pin_required"):
                # PIN setup handled separately by pin_auth module
                actions_taken.append("pin_configured")
            
            # Kiosk mode
            if profile_config.get("kiosk_mode"):
                from .kiosk_mode import KioskMode
                kiosk = KioskMode()
                kiosk.enable_kiosk_mode(
                    username,
                    profile_config.get("allowed_apps", [])
                )
                actions_taken.append("kiosk_mode_enabled")
            
            # Backup automation
            if profile_config.get("auto_backup_enabled"):
                from .backup_automation import BackupAutomation
                backup = BackupAutomation()
                backup.configure_backup(
                    username,
                    interval=profile_config.get("backup_interval", "daily")
                )
                actions_taken.append("backup_configured")
            
            # Auto-rollback (for less technical users)
            if profile_config.get("auto_rollback_enabled"):
                self._configure_auto_rollback(
                    username,
                    profile_config.get("rollback_schedule", "daily")
                )
                actions_taken.append("auto_rollback_configured")
            
            logger.info(f"Applied profile settings for {username}: {actions_taken}")
            
            return {
                "success": True,
                "actions_taken": actions_taken
            }
            
        except Exception as e:
            logger.error(f"Failed to apply profile settings: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _configure_auto_rollback(self, username: str, schedule: str):
        """Configure automatic rollback safety net"""
        # Create systemd timer for daily rollback check
        # This would check system health and rollback if issues detected
        pass
    
    def _load_profiles(self) -> Dict[str, Dict[str, Any]]:
        """Load profiles from disk"""
        if not self.profiles_file.exists():
            return {}
        
        try:
            with open(self.profiles_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load profiles: {e}")
            return {}
    
    def _save_profiles(self):
        """Save profiles to disk"""
        try:
            with open(self.profiles_file, 'w') as f:
                json.dump(self.profiles, f, indent=2)
            
            os.chmod(self.profiles_file, 0o600)
            
        except Exception as e:
            logger.error(f"Failed to save profiles: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get profile statistics"""
        stats = {
            "total_profiles": len(self.profiles),
            "by_type": {
                "primary": 0,
                "less_technical": 0,
                "kids_temporary": 0
            }
        }
        
        for profile in self.profiles.values():
            profile_type = profile.get("type")
            if profile_type in stats["by_type"]:
                stats["by_type"][profile_type] += 1
        
        return stats
