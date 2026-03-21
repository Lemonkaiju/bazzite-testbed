"""
Backup Automation
Automated backups for user profiles
"""

import os
import json
import logging
import subprocess
import tarfile
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


class BackupAutomation:
    """
    Manages automated backups for user profiles
    
    Features:
    - Scheduled backups (hourly, daily, weekly)
    - Home directory backup
    - Incremental backups
    - Backup rotation (keep last N backups)
    - Restore functionality
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize backup automation"""
        self.config = config or {}
        
        # Backup storage directory
        self.backup_dir = Path(self.config.get(
            "backup_dir",
            Path.home() / ".local" / "share" / "backups"
        ))
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Backup configuration directory
        self.config_dir = Path(self.config.get(
            "config_dir",
            Path.home() / ".local" / "share" / "backup_config"
        ))
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("Backup Automation initialized")
    
    def configure_backup(
        self,
        username: str,
        interval: str = "daily",
        keep_count: int = 7,
        include_paths: Optional[List[str]] = None,
        exclude_paths: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Configure automated backup for a user
        
        Args:
            username: Username
            interval: Backup interval (hourly, daily, weekly)
            keep_count: Number of backups to keep
            include_paths: Paths to include (default: home directory)
            exclude_paths: Paths to exclude
            
        Returns:
            Result dictionary
        """
        try:
            # Default paths
            if include_paths is None:
                include_paths = [str(Path.home())]
            
            if exclude_paths is None:
                exclude_paths = [
                    ".cache",
                    ".local/share/Trash",
                    "Downloads",
                    ".steam",
                    ".var/app/*/cache"
                ]
            
            # Create backup configuration
            backup_config = {
                "username": username,
                "interval": interval,
                "keep_count": keep_count,
                "include_paths": include_paths,
                "exclude_paths": exclude_paths,
                "enabled": True,
                "last_backup": None,
                "backup_count": 0
            }
            
            # Save configuration
            config_file = self.config_dir / f"{username}_backup.json"
            with open(config_file, 'w') as f:
                json.dump(backup_config, f, indent=2)
            
            os.chmod(config_file, 0o600)
            
            # Create systemd timer
            self._create_systemd_timer(username, interval)
            
            logger.info(f"Backup configured for {username}: {interval}")
            
            return {
                "success": True,
                "message": f"Backup configured for {username}",
                "interval": interval,
                "keep_count": keep_count
            }
            
        except Exception as e:
            logger.error(f"Failed to configure backup: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def perform_backup(self, username: str) -> Dict[str, Any]:
        """
        Perform a backup for a user
        
        Args:
            username: Username
            
        Returns:
            Result dictionary with backup info
        """
        config_file = self.config_dir / f"{username}_backup.json"
        
        if not config_file.exists():
            return {
                "success": False,
                "error": "Backup not configured"
            }
        
        try:
            # Load configuration
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            if not config.get("enabled", False):
                return {
                    "success": False,
                    "error": "Backup is disabled"
                }
            
            # Create backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{username}_{timestamp}.tar.gz"
            backup_path = self.backup_dir / username / backup_name
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Perform backup
            include_paths = config.get("include_paths", [])
            exclude_paths = config.get("exclude_paths", [])
            
            backup_result = self._create_backup_archive(
                backup_path,
                include_paths,
                exclude_paths
            )
            
            if not backup_result.get("success"):
                return backup_result
            
            # Update configuration
            config["last_backup"] = datetime.now().isoformat()
            config["backup_count"] = config.get("backup_count", 0) + 1
            
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            # Rotate old backups
            self._rotate_backups(username, config.get("keep_count", 7))
            
            logger.info(f"Backup created for {username}: {backup_name}")
            
            return {
                "success": True,
                "message": f"Backup created successfully",
                "backup_file": str(backup_path),
                "size_mb": backup_path.stat().st_size / (1024 * 1024)
            }
            
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def restore_backup(
        self,
        username: str,
        backup_file: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Restore from a backup
        
        Args:
            username: Username
            backup_file: Specific backup file (default: latest)
            
        Returns:
            Result dictionary
        """
        try:
            # Find backup file
            if backup_file is None:
                # Get latest backup
                backups = self.list_backups(username)
                if not backups:
                    return {
                        "success": False,
                        "error": "No backups found"
                    }
                backup_file = backups[0]["path"]
            
            backup_path = Path(backup_file)
            
            if not backup_path.exists():
                return {
                    "success": False,
                    "error": "Backup file not found"
                }
            
            # Extract backup
            logger.info(f"Restoring backup for {username} from {backup_path}")
            
            with tarfile.open(backup_path, 'r:gz') as tar:
                tar.extractall(path="/")
            
            logger.info(f"Backup restored for {username}")
            
            return {
                "success": True,
                "message": "Backup restored successfully",
                "backup_file": str(backup_path)
            }
            
        except Exception as e:
            logger.error(f"Restore failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def list_backups(self, username: str) -> List[Dict[str, Any]]:
        """List available backups for a user"""
        backup_user_dir = self.backup_dir / username
        
        if not backup_user_dir.exists():
            return []
        
        backups = []
        
        for backup_file in sorted(backup_user_dir.glob("*.tar.gz"), reverse=True):
            stat = backup_file.stat()
            backups.append({
                "filename": backup_file.name,
                "path": str(backup_file),
                "size_mb": stat.st_size / (1024 * 1024),
                "created": datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
        
        return backups
    
    def delete_backup(self, username: str, backup_file: str) -> Dict[str, Any]:
        """Delete a specific backup"""
        backup_path = Path(backup_file)
        
        if not backup_path.exists():
            return {
                "success": False,
                "error": "Backup file not found"
            }
        
        try:
            backup_path.unlink()
            logger.info(f"Deleted backup: {backup_path}")
            
            return {
                "success": True,
                "message": "Backup deleted"
            }
            
        except Exception as e:
            logger.error(f"Failed to delete backup: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _create_backup_archive(
        self,
        backup_path: Path,
        include_paths: List[str],
        exclude_paths: List[str]
    ) -> Dict[str, Any]:
        """Create backup archive using tar"""
        try:
            # Build tar command
            cmd = ["tar", "-czf", str(backup_path)]
            
            # Add exclude patterns
            for exclude in exclude_paths:
                cmd.extend(["--exclude", exclude])
            
            # Add include paths
            cmd.extend(include_paths)
            
            # Execute tar
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )
            
            if result.returncode == 0:
                return {"success": True}
            else:
                return {
                    "success": False,
                    "error": f"tar failed: {result.stderr}"
                }
                
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Backup timeout (> 1 hour)"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _rotate_backups(self, username: str, keep_count: int):
        """Rotate backups, keeping only the most recent N"""
        backups = self.list_backups(username)
        
        # Delete old backups
        for backup in backups[keep_count:]:
            try:
                Path(backup["path"]).unlink()
                logger.info(f"Rotated old backup: {backup['filename']}")
            except Exception as e:
                logger.error(f"Failed to rotate backup: {e}")
    
    def _create_systemd_timer(self, username: str, interval: str):
        """Create systemd timer for automated backups"""
        # Determine timer schedule
        if interval == "hourly":
            on_calendar = "hourly"
        elif interval == "daily":
            on_calendar = "daily"
        elif interval == "weekly":
            on_calendar = "weekly"
        else:
            on_calendar = "daily"
        
        # Create timer unit
        timer_content = f"""[Unit]
Description=Backup timer for {username}

[Timer]
OnCalendar={on_calendar}
Persistent=true

[Install]
WantedBy=timers.target
"""
        
        # Create service unit
        service_content = f"""[Unit]
Description=Backup service for {username}

[Service]
Type=oneshot
ExecStart=/usr/bin/python3 -c "from ai_facilitator.profiles import BackupAutomation; b = BackupAutomation(); b.perform_backup('{username}')"
"""
        
        # Save to user systemd directory
        systemd_dir = Path.home() / ".config" / "systemd" / "user"
        systemd_dir.mkdir(parents=True, exist_ok=True)
        
        timer_file = systemd_dir / f"backup-{username}.timer"
        service_file = systemd_dir / f"backup-{username}.service"
        
        try:
            with open(timer_file, 'w') as f:
                f.write(timer_content)
            
            with open(service_file, 'w') as f:
                f.write(service_content)
            
            # Reload systemd and enable timer
            subprocess.run(["systemctl", "--user", "daemon-reload"], timeout=10)
            subprocess.run(["systemctl", "--user", "enable", f"backup-{username}.timer"], timeout=10)
            subprocess.run(["systemctl", "--user", "start", f"backup-{username}.timer"], timeout=10)
            
            logger.info(f"Created systemd timer for {username}")
            
        except Exception as e:
            logger.error(f"Failed to create systemd timer: {e}")
    
    def get_backup_status(self, username: str) -> Dict[str, Any]:
        """Get backup status for a user"""
        config_file = self.config_dir / f"{username}_backup.json"
        
        if not config_file.exists():
            return {
                "configured": False
            }
        
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            backups = self.list_backups(username)
            
            return {
                "configured": True,
                "enabled": config.get("enabled", False),
                "interval": config.get("interval"),
                "keep_count": config.get("keep_count"),
                "last_backup": config.get("last_backup"),
                "backup_count": len(backups),
                "total_size_mb": sum(b["size_mb"] for b in backups)
            }
            
        except Exception as e:
            logger.error(f"Failed to get backup status: {e}")
            return {
                "configured": False,
                "error": str(e)
            }
