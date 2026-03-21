"""
Network Coordinator
Coordinates security between local AI Facilitator and network-level STFD systems
"""

import json
import logging
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


class NetworkCoordinator:
    """
    Coordinates security between local and network systems
    
    Features:
    - Coordinate local and network security responses
    - Trigger network-level protections on local threats
    - Monitor network security status
    - Unified security policy enforcement
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize network coordinator"""
        self.config = config or {}
        
        # STFD path
        self.stfd_path = Path(self.config.get(
            "stfd_path",
            Path.home() / "projects" / "Linux testbed" / "shut-the-front-door" / "installer"
        ))
        
        # Coordinator state directory
        self.coordinator_dir = Path(self.config.get(
            "coordinator_dir",
            Path.home() / ".local" / "share" / "network_coordinator"
        ))
        self.coordinator_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("Network Coordinator initialized")
    
    def coordinate_threat_response(
        self,
        threat_type: str,
        threat_level: str,
        threat_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Coordinate threat response across local and network systems
        
        Args:
            threat_type: Type of threat (duress, intrusion, physical)
            threat_level: Severity (low, medium, high, critical)
            threat_data: Threat details
            
        Returns:
            Coordination result
        """
        logger.critical(f"Coordinating threat response: {threat_type} - {threat_level}")
        
        actions_taken = []
        
        # Local actions (already handled by AI Facilitator)
        actions_taken.append("local_response_triggered")
        
        # Network-level actions based on threat level
        if threat_level in ["high", "critical"]:
            # Trigger network lockdown
            network_result = self._trigger_network_lockdown(threat_type, threat_data)
            if network_result.get("success"):
                actions_taken.append("network_lockdown")
        
        # Log coordination event
        self._log_coordination_event(threat_type, threat_level, actions_taken)
        
        return {
            "success": True,
            "threat_type": threat_type,
            "threat_level": threat_level,
            "actions_taken": actions_taken,
            "timestamp": datetime.now().isoformat()
        }
    
    def _trigger_network_lockdown(
        self,
        threat_type: str,
        threat_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Trigger network-level lockdown
        
        Actions:
        - Block external WireGuard access
        - Enable strict firewall rules
        - Alert network administrators
        """
        logger.critical(f"Triggering network lockdown for {threat_type}")
        
        actions = []
        
        # Create lockdown flag file
        lockdown_file = self.coordinator_dir / "network_lockdown.json"
        
        lockdown_data = {
            "active": True,
            "triggered_by": threat_type,
            "timestamp": datetime.now().isoformat(),
            "threat_data": threat_data
        }
        
        try:
            with open(lockdown_file, 'w') as f:
                json.dump(lockdown_data, f, indent=2)
            
            actions.append("lockdown_flag_set")
            
            # In production, this would:
            # - Call STFD API to disable WireGuard
            # - Update OPNsense firewall rules
            # - Send alerts via configured channels
            
            logger.info("Network lockdown triggered")
            
            return {
                "success": True,
                "actions": actions
            }
            
        except Exception as e:
            logger.error(f"Failed to trigger network lockdown: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def check_network_lockdown_status(self) -> Dict[str, Any]:
        """Check if network lockdown is active"""
        lockdown_file = self.coordinator_dir / "network_lockdown.json"
        
        if not lockdown_file.exists():
            return {
                "active": False
            }
        
        try:
            with open(lockdown_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to check lockdown status: {e}")
            return {
                "active": False,
                "error": str(e)
            }
    
    def clear_network_lockdown(self, authorized_by: str) -> Dict[str, Any]:
        """
        Clear network lockdown
        
        Args:
            authorized_by: Who authorized the clearance
            
        Returns:
            Result dictionary
        """
        lockdown_file = self.coordinator_dir / "network_lockdown.json"
        
        if not lockdown_file.exists():
            return {
                "success": False,
                "error": "No active lockdown"
            }
        
        try:
            # Archive lockdown data
            with open(lockdown_file, 'r') as f:
                lockdown_data = json.load(f)
            
            lockdown_data["cleared_by"] = authorized_by
            lockdown_data["cleared_at"] = datetime.now().isoformat()
            lockdown_data["active"] = False
            
            # Save to history
            history_file = self.coordinator_dir / "lockdown_history.json"
            history = []
            
            if history_file.exists():
                with open(history_file, 'r') as f:
                    history = json.load(f)
            
            history.append(lockdown_data)
            
            with open(history_file, 'w') as f:
                json.dump(history, f, indent=2)
            
            # Remove active lockdown
            lockdown_file.unlink()
            
            logger.info(f"Network lockdown cleared by {authorized_by}")
            
            return {
                "success": True,
                "message": "Network lockdown cleared"
            }
            
        except Exception as e:
            logger.error(f"Failed to clear lockdown: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_network_status(self) -> Dict[str, Any]:
        """
        Get comprehensive network security status
        
        Returns:
            Network status from STFD modules
        """
        status = {
            "timestamp": datetime.now().isoformat(),
            "lockdown_active": False,
            "modules": {}
        }
        
        # Check lockdown status
        lockdown = self.check_network_lockdown_status()
        status["lockdown_active"] = lockdown.get("active", False)
        
        # Read STFD configuration
        stfd_config = self.stfd_path / "install_config.json"
        
        if stfd_config.exists():
            try:
                with open(stfd_config, 'r') as f:
                    config = json.load(f)
                
                # Extract module statuses
                modules = config.get("modules", [])
                for module in modules:
                    module_id = module.get("id")
                    status["modules"][module_id] = {
                        "name": module.get("name"),
                        "status": module.get("status", "unknown"),
                        "configured": module.get("configured", False)
                    }
                    
            except Exception as e:
                logger.error(f"Failed to read STFD config: {e}")
        
        return status
    
    def sync_security_policies(self) -> Dict[str, Any]:
        """
        Sync security policies between local and network systems
        
        Returns:
            Sync result
        """
        from ai_facilitator.profiles import ProfileManager
        
        policies = {
            "timestamp": datetime.now().isoformat(),
            "local_policies": {},
            "network_policies": {}
        }
        
        # Get local security policies from profiles
        try:
            profile_manager = ProfileManager()
            profiles = profile_manager.list_profiles()
            
            for profile in profiles:
                username = profile["username"]
                permissions = profile_manager.get_permissions(username)
                
                policies["local_policies"][username] = {
                    "profile_type": profile["type"],
                    "permissions": permissions
                }
                
        except Exception as e:
            logger.error(f"Failed to get local policies: {e}")
        
        # Save synced policies
        policies_file = self.coordinator_dir / "synced_policies.json"
        
        try:
            with open(policies_file, 'w') as f:
                json.dump(policies, f, indent=2)
            
            logger.info("Security policies synced")
            
            return {
                "success": True,
                "policies_file": str(policies_file)
            }
            
        except Exception as e:
            logger.error(f"Failed to sync policies: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _log_coordination_event(
        self,
        threat_type: str,
        threat_level: str,
        actions: List[str]
    ):
        """Log coordination event"""
        log_file = self.coordinator_dir / "coordination_log.json"
        
        event = {
            "timestamp": datetime.now().isoformat(),
            "threat_type": threat_type,
            "threat_level": threat_level,
            "actions_taken": actions
        }
        
        try:
            logs = []
            if log_file.exists():
                with open(log_file, 'r') as f:
                    logs = json.load(f)
            
            logs.append(event)
            logs = logs[-100:]  # Keep last 100
            
            with open(log_file, 'w') as f:
                json.dump(logs, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to log coordination event: {e}")
    
    def get_coordination_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get coordination event history"""
        log_file = self.coordinator_dir / "coordination_log.json"
        
        if not log_file.exists():
            return []
        
        try:
            with open(log_file, 'r') as f:
                logs = json.load(f)
            
            return logs[-limit:]
            
        except Exception as e:
            logger.error(f"Failed to get coordination history: {e}")
            return []
    
    def monitor_network_health(self) -> Dict[str, Any]:
        """
        Monitor network health and connectivity
        
        Returns:
            Network health status
        """
        health = {
            "timestamp": datetime.now().isoformat(),
            "connectivity": "unknown",
            "latency_ms": 0,
            "vpn_active": False
        }
        
        # Check internet connectivity
        try:
            result = subprocess.run(
                ["ping", "-c", "1", "-W", "2", "8.8.8.8"],
                capture_output=True,
                timeout=5
            )
            
            if result.returncode == 0:
                health["connectivity"] = "online"
                
                # Extract latency
                output = result.stdout.decode()
                if "time=" in output:
                    latency_str = output.split("time=")[1].split()[0]
                    health["latency_ms"] = float(latency_str)
            else:
                health["connectivity"] = "offline"
                
        except Exception as e:
            logger.error(f"Failed to check connectivity: {e}")
            health["connectivity"] = "error"
        
        # Check VPN status (WireGuard)
        try:
            result = subprocess.run(
                ["wg", "show"],
                capture_output=True,
                timeout=5
            )
            
            if result.returncode == 0 and result.stdout:
                health["vpn_active"] = True
            else:
                health["vpn_active"] = False
                
        except Exception:
            health["vpn_active"] = False
        
        return health
