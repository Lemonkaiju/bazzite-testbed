"""
MCP Tool Wrappers
Safe command execution wrappers for Bazzite immutable OS
"""

import logging
import subprocess
import shlex
from typing import Dict, Any, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class MCPToolWrapper:
    """
    Wraps system commands in safe MCP tools
    
    Allowed commands (per Universal Tooling Map):
    1. flatpak install [App X]
    2. rpm-ostree rollback
    3. distrobox create -n [Env]
    4. ujust setup-gaming
    
    NO raw shell script execution allowed.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize MCP tool wrapper"""
        self.config = config
        self.allowed_commands = config.get("allowed_commands", [
            "flatpak install",
            "rpm-ostree rollback",
            "distrobox create",
            "ujust setup-gaming"
        ])
        
        logger.info("MCP Tool Wrapper initialized")
    
    def execute(self, command: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a command through MCP tool wrapper
        
        Args:
            command: Command name (e.g., "flatpak_install")
            args: Command arguments
            
        Returns:
            Result dictionary
        """
        # Route to appropriate handler
        if command == "flatpak_install":
            return self._flatpak_install(args)
        elif command == "rpm_ostree_rollback":
            return self._rpm_ostree_rollback(args)
        elif command == "distrobox_create":
            return self._distrobox_create(args)
        elif command == "ujust_setup_gaming":
            return self._ujust_setup_gaming(args)
        else:
            raise ValueError(f"Unknown or forbidden command: {command}")
    
    def _flatpak_install(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Install Flatpak application
        
        Args:
            app_name: Application name or ID
            remote: Flatpak remote (default: flathub)
            system: Install system-wide (default: False, user install)
        """
        app_name = args.get("app_name")
        if not app_name:
            raise ValueError("app_name is required")
        
        remote = args.get("remote", "flathub")
        system = args.get("system", False)
        
        # Build command
        cmd = ["flatpak", "install"]
        
        if system:
            cmd.append("--system")
        else:
            cmd.append("--user")
        
        cmd.extend(["-y", remote, app_name])
        
        logger.info(f"Executing: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "output": result.stdout,
                    "message": f"Successfully installed {app_name}"
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr,
                    "message": f"Failed to install {app_name}"
                }
                
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Command timeout",
                "message": "Installation took too long"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Installation failed: {e}"
            }
    
    def _rpm_ostree_rollback(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Roll back to previous rpm-ostree deployment
        Used for "Something feels broken" recovery
        
        Args:
            reboot: Whether to reboot after rollback (default: False)
        """
        reboot = args.get("reboot", False)
        
        # Build command
        cmd = ["rpm-ostree", "rollback"]
        
        if reboot:
            cmd.append("--reboot")
        
        logger.info(f"Executing: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                message = "Successfully rolled back to previous deployment"
                if reboot:
                    message += " - System will reboot"
                
                return {
                    "success": True,
                    "output": result.stdout,
                    "message": message,
                    "requires_reboot": not reboot
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr,
                    "message": "Rollback failed"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Rollback failed: {e}"
            }
    
    def _distrobox_create(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a Distrobox container
        
        Args:
            name: Container name
            distro: Distribution image (default: fedora:39)
            home: Custom home directory
            additional_packages: List of packages to pre-install
        """
        name = args.get("name")
        if not name:
            raise ValueError("name is required")
        
        distro = args.get("distro", "fedora:39")
        home = args.get("home")
        additional_packages = args.get("additional_packages", [])
        
        # Build command
        cmd = ["distrobox", "create", "-n", name, "-i", distro]
        
        if home:
            cmd.extend(["--home", home])
        
        if additional_packages:
            cmd.extend(["--additional-packages", " ".join(additional_packages)])
        
        logger.info(f"Executing: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "output": result.stdout,
                    "message": f"Successfully created Distrobox '{name}'",
                    "container_name": name
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr,
                    "message": f"Failed to create Distrobox '{name}'"
                }
                
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Command timeout",
                "message": "Container creation took too long"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Container creation failed: {e}"
            }
    
    def _ujust_setup_gaming(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Set up gaming environment using ujust
        Bazzite-specific command for gaming setup
        
        Args:
            None (ujust handles configuration)
        """
        cmd = ["ujust", "setup-gaming"]
        
        logger.info(f"Executing: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600
            )
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "output": result.stdout,
                    "message": "Gaming environment setup complete"
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr,
                    "message": "Gaming setup failed"
                }
                
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Command timeout",
                "message": "Gaming setup took too long"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Gaming setup failed: {e}"
            }
    
    def list_available_flatpaks(self, search_term: Optional[str] = None) -> List[Dict[str, str]]:
        """
        List available Flatpak applications
        
        Args:
            search_term: Optional search term to filter results
            
        Returns:
            List of available applications
        """
        cmd = ["flatpak", "search"]
        
        if search_term:
            cmd.append(search_term)
        else:
            # List popular apps if no search term
            return []
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                apps = []
                for line in result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split('\t')
                        if len(parts) >= 3:
                            apps.append({
                                "name": parts[0],
                                "description": parts[1],
                                "app_id": parts[2]
                            })
                return apps
            else:
                logger.error(f"Flatpak search failed: {result.stderr}")
                return []
                
        except Exception as e:
            logger.error(f"Flatpak search failed: {e}")
            return []
    
    def list_distrobox_containers(self) -> List[Dict[str, str]]:
        """List existing Distrobox containers"""
        cmd = ["distrobox", "list"]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                containers = []
                lines = result.stdout.strip().split('\n')
                
                # Skip header line
                for line in lines[1:]:
                    if line:
                        parts = line.split('|')
                        if len(parts) >= 3:
                            containers.append({
                                "id": parts[0].strip(),
                                "name": parts[1].strip(),
                                "status": parts[2].strip()
                            })
                return containers
            else:
                return []
                
        except Exception as e:
            logger.error(f"Distrobox list failed: {e}")
            return []
    
    def get_rpm_ostree_status(self) -> Dict[str, Any]:
        """Get current rpm-ostree deployment status"""
        cmd = ["rpm-ostree", "status", "--json"]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                import json
                return json.loads(result.stdout)
            else:
                return {"error": result.stderr}
                
        except Exception as e:
            logger.error(f"rpm-ostree status failed: {e}")
            return {"error": str(e)}
