"""
Security Bridge
Connects AI Facilitator security systems with STFD installer
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class SecurityBridge:
    """
    Bridges AI Facilitator security with STFD installer
    
    Features:
    - Expose security status to STFD dashboard
    - Coordinate security events across systems
    - Unified security logging
    - Cross-system alerts
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize security bridge"""
        self.config = config or {}
        
        # STFD installer path
        self.stfd_path = Path(self.config.get(
            "stfd_path",
            Path.home() / "projects" / "Linux testbed" / "shut-the-front-door" / "installer"
        ))
        
        # Bridge state directory
        self.bridge_dir = Path(self.config.get(
            "bridge_dir",
            Path.home() / ".local" / "share" / "stfd_bridge"
        ))
        self.bridge_dir.mkdir(parents=True, exist_ok=True)
        
        # Shared security state file
        self.security_state_file = self.bridge_dir / "security_state.json"
        
        logger.info("Security Bridge initialized")
    
    def get_security_status(self) -> Dict[str, Any]:
        """
        Get comprehensive security status from all AI Facilitator systems
        
        Returns:
            Unified security status
        """
        from ai_facilitator.pin_auth import PINManager
        from ai_facilitator.security import DuressManager, IntrusionProtection, PhysicalSecurityManager
        from ai_facilitator.profiles import ProfileManager
        
        status = {
            "timestamp": datetime.now().isoformat(),
            "systems": {}
        }
        
        # PIN Authentication status
        try:
            pin_manager = PINManager()
            status["systems"]["pin_auth"] = {
                "available": True,
                "configured_users": []  # Would enumerate users with PINs
            }
        except Exception as e:
            status["systems"]["pin_auth"] = {
                "available": False,
                "error": str(e)
            }
        
        # Duress Protection status
        try:
            duress = DuressManager()
            status["systems"]["duress"] = {
                "available": True,
                "recent_activations": len(duress.get_activation_history(limit=10))
            }
        except Exception as e:
            status["systems"]["duress"] = {
                "available": False,
                "error": str(e)
            }
        
        # Intrusion Protection status
        try:
            intrusion = IntrusionProtection()
            intrusion_status = intrusion.get_status()
            status["systems"]["intrusion"] = {
                "available": True,
                "enabled": intrusion_status.get("enabled", True),
                "max_attempts": intrusion_status.get("max_attempts", 5),
                "recent_intrusions": intrusion_status.get("recent_intrusions", 0)
            }
        except Exception as e:
            status["systems"]["intrusion"] = {
                "available": False,
                "error": str(e)
            }
        
        # Physical Security status
        try:
            physical = PhysicalSecurityManager()
            physical_status = physical.get_status()
            status["systems"]["physical"] = {
                "available": True,
                "sentinel_enabled": physical_status.get("sentinel_enabled", False),
                "sentinel_present": physical_status.get("sentinel_present", False),
                "monitoring": physical_status.get("monitoring", False)
            }
        except Exception as e:
            status["systems"]["physical"] = {
                "available": False,
                "error": str(e)
            }
        
        # Profile Management status
        try:
            profile_manager = ProfileManager()
            stats = profile_manager.get_statistics()
            status["systems"]["profiles"] = {
                "available": True,
                "total_profiles": stats.get("total_profiles", 0),
                "by_type": stats.get("by_type", {})
            }
        except Exception as e:
            status["systems"]["profiles"] = {
                "available": False,
                "error": str(e)
            }
        
        # Save to shared state file
        self._save_security_state(status)
        
        return status
    
    def _save_security_state(self, status: Dict[str, Any]):
        """Save security state to shared file for STFD access"""
        try:
            with open(self.security_state_file, 'w') as f:
                json.dump(status, f, indent=2)
            
            logger.debug("Security state saved to bridge")
        except Exception as e:
            logger.error(f"Failed to save security state: {e}")
    
    def send_security_alert(
        self,
        alert_type: str,
        severity: str,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send security alert to STFD system
        
        Args:
            alert_type: Type of alert (duress, intrusion, physical)
            severity: Severity level (low, medium, high, critical)
            message: Alert message
            details: Additional details
            
        Returns:
            Result dictionary
        """
        alert = {
            "timestamp": datetime.now().isoformat(),
            "type": alert_type,
            "severity": severity,
            "message": message,
            "details": details or {},
            "source": "ai_facilitator"
        }
        
        # Save to alerts file
        alerts_file = self.bridge_dir / "security_alerts.json"
        
        try:
            alerts = []
            if alerts_file.exists():
                with open(alerts_file, 'r') as f:
                    alerts = json.load(f)
            
            alerts.append(alert)
            
            # Keep only last 100 alerts
            alerts = alerts[-100:]
            
            with open(alerts_file, 'w') as f:
                json.dump(alerts, f, indent=2)
            
            logger.info(f"Security alert sent: {alert_type} - {severity}")
            
            # Also log to STFD installer log if available
            self._log_to_stfd(alert)
            
            return {
                "success": True,
                "alert_id": len(alerts)
            }
            
        except Exception as e:
            logger.error(f"Failed to send security alert: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _log_to_stfd(self, alert: Dict[str, Any]):
        """Log alert to STFD installer log"""
        stfd_log = self.stfd_path / "install_log.json"
        
        if not stfd_log.exists():
            return
        
        try:
            logs = []
            with open(stfd_log, 'r') as f:
                logs = json.load(f)
            
            logs.append({
                "timestamp": alert["timestamp"],
                "action": f"security_alert_{alert['type']}",
                "details": alert,
                "status": alert["severity"]
            })
            
            with open(stfd_log, 'w') as f:
                json.dump(logs, f, indent=2)
                
        except Exception as e:
            logger.debug(f"Could not log to STFD: {e}")
    
    def get_network_security_status(self) -> Dict[str, Any]:
        """
        Get network security status from STFD modules
        
        Returns:
            Network security status
        """
        status = {
            "wireguard": {"status": "unknown"},
            "opnsense": {"status": "unknown"},
            "adguard": {"status": "unknown"}
        }
        
        # Read STFD config
        stfd_config = self.stfd_path / "install_config.json"
        
        if stfd_config.exists():
            try:
                with open(stfd_config, 'r') as f:
                    config = json.load(f)
                
                # Extract network security status
                if "modules" in config:
                    for module in config.get("modules", []):
                        module_id = module.get("id")
                        if module_id in status:
                            status[module_id] = {
                                "status": module.get("status", "unknown"),
                                "configured": module.get("configured", False)
                            }
            except Exception as e:
                logger.error(f"Failed to read STFD config: {e}")
        
        return status
    
    def coordinate_security_event(
        self,
        event_type: str,
        event_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Coordinate security event across AI Facilitator and STFD
        
        Args:
            event_type: Type of event (duress_activated, intrusion_detected, etc.)
            event_data: Event data
            
        Returns:
            Coordination result
        """
        logger.critical(f"Security event coordination: {event_type}")
        
        actions_taken = []
        
        # AI Facilitator actions
        if event_type == "duress_activated":
            # Send high-severity alert
            self.send_security_alert(
                "duress",
                "critical",
                "Duress code activated - user under coercion",
                event_data
            )
            actions_taken.append("alert_sent")
        
        elif event_type == "intrusion_detected":
            # Send high-severity alert
            self.send_security_alert(
                "intrusion",
                "critical",
                "Intrusion detected - failed login attempts exceeded",
                event_data
            )
            actions_taken.append("alert_sent")
        
        elif event_type == "physical_threat":
            # Send critical alert
            self.send_security_alert(
                "physical",
                "critical",
                "Physical security threat - USB sentinel removed",
                event_data
            )
            actions_taken.append("alert_sent")
        
        # STFD coordination actions
        # Could trigger network-level responses (e.g., block external access)
        
        return {
            "success": True,
            "event_type": event_type,
            "actions_taken": actions_taken,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_unified_logs(self, limit: int = 50) -> list:
        """
        Get unified logs from both AI Facilitator and STFD
        
        Args:
            limit: Maximum number of log entries
            
        Returns:
            Unified log entries
        """
        unified_logs = []
        
        # Get AI Facilitator logs
        from ai_facilitator import TransactionLogger
        
        try:
            transaction_logger = TransactionLogger()
            ai_logs = transaction_logger.get_history(limit=limit)
            
            for log in ai_logs:
                unified_logs.append({
                    "timestamp": log.get("timestamp"),
                    "source": "ai_facilitator",
                    "action": log.get("command"),
                    "status": log.get("status"),
                    "details": log
                })
        except Exception as e:
            logger.error(f"Failed to get AI Facilitator logs: {e}")
        
        # Get STFD logs
        stfd_log = self.stfd_path / "install_log.json"
        
        if stfd_log.exists():
            try:
                with open(stfd_log, 'r') as f:
                    stfd_logs = json.load(f)
                
                for log in stfd_logs[-limit:]:
                    unified_logs.append({
                        "timestamp": log.get("timestamp"),
                        "source": "stfd",
                        "action": log.get("action"),
                        "status": log.get("status"),
                        "details": log.get("details", {})
                    })
            except Exception as e:
                logger.error(f"Failed to get STFD logs: {e}")
        
        # Sort by timestamp
        unified_logs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        return unified_logs[:limit]
    
    def register_with_stfd(self) -> Dict[str, Any]:
        """
        Register AI Facilitator with STFD installer
        
        Creates integration configuration for STFD to access AI Facilitator
        """
        integration_config = {
            "name": "AI Facilitator Security",
            "version": "1.0.0",
            "enabled": True,
            "endpoints": {
                "security_status": str(self.security_state_file),
                "security_alerts": str(self.bridge_dir / "security_alerts.json")
            },
            "features": [
                "pin_authentication",
                "duress_protection",
                "intrusion_detection",
                "physical_security",
                "user_profiles"
            ]
        }
        
        # Save integration config
        integration_file = self.bridge_dir / "integration_config.json"
        
        try:
            with open(integration_file, 'w') as f:
                json.dump(integration_config, f, indent=2)
            
            logger.info("Registered with STFD installer")
            
            return {
                "success": True,
                "config_file": str(integration_file)
            }
            
        except Exception as e:
            logger.error(f"Failed to register with STFD: {e}")
            return {
                "success": False,
                "error": str(e)
            }
