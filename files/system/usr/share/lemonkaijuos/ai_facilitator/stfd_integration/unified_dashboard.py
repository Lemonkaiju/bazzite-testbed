"""
Unified Dashboard
Single pane of glass for AI Facilitator and STFD security status
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


class UnifiedDashboard:
    """
    Unified security dashboard combining AI Facilitator and STFD
    
    Features:
    - Single view of all security systems
    - Real-time status monitoring
    - Alert aggregation
    - Quick actions
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize unified dashboard"""
        self.config = config or {}
        
        # Dashboard state directory
        self.dashboard_dir = Path(self.config.get(
            "dashboard_dir",
            Path.home() / ".local" / "share" / "unified_dashboard"
        ))
        self.dashboard_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("Unified Dashboard initialized")
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """
        Get complete dashboard data
        
        Returns:
            Dashboard data with all system statuses
        """
        from .security_bridge import SecurityBridge
        
        bridge = SecurityBridge()
        
        dashboard = {
            "timestamp": datetime.now().isoformat(),
            "local_security": self._get_local_security_summary(),
            "network_security": bridge.get_network_security_status(),
            "recent_alerts": self._get_recent_alerts(limit=10),
            "recent_activity": self._get_recent_activity(limit=20),
            "system_health": self._get_system_health()
        }
        
        return dashboard
    
    def _get_local_security_summary(self) -> Dict[str, Any]:
        """Get summary of local security systems"""
        from ai_facilitator.pin_auth import PINManager
        from ai_facilitator.security import DuressManager, IntrusionProtection, PhysicalSecurityManager
        from ai_facilitator.profiles import ProfileManager
        
        summary = {
            "overall_status": "healthy",
            "systems": []
        }
        
        # PIN Authentication
        try:
            pin_manager = PINManager()
            summary["systems"].append({
                "name": "PIN Authentication",
                "status": "active",
                "icon": "🔐",
                "details": "6-digit PIN system active"
            })
        except Exception:
            summary["systems"].append({
                "name": "PIN Authentication",
                "status": "unavailable",
                "icon": "⚠️",
                "details": "Not configured"
            })
            summary["overall_status"] = "degraded"
        
        # Duress Protection
        try:
            duress = DuressManager()
            activations = len(duress.get_activation_history(limit=10))
            
            if activations > 0:
                summary["systems"].append({
                    "name": "Duress Protection",
                    "status": "alert",
                    "icon": "🚨",
                    "details": f"{activations} recent activations"
                })
                summary["overall_status"] = "alert"
            else:
                summary["systems"].append({
                    "name": "Duress Protection",
                    "status": "active",
                    "icon": "🛡️",
                    "details": "Monitoring for coercion"
                })
        except Exception:
            summary["systems"].append({
                "name": "Duress Protection",
                "status": "unavailable",
                "icon": "⚠️",
                "details": "Not configured"
            })
        
        # Intrusion Protection
        try:
            intrusion = IntrusionProtection()
            intrusion_status = intrusion.get_status()
            recent = intrusion_status.get("recent_intrusions", 0)
            
            if recent > 0:
                summary["systems"].append({
                    "name": "Intrusion Protection",
                    "status": "alert",
                    "icon": "🚨",
                    "details": f"{recent} recent intrusions"
                })
                summary["overall_status"] = "alert"
            else:
                summary["systems"].append({
                    "name": "Intrusion Protection",
                    "status": "active",
                    "icon": "🛡️",
                    "details": f"Max {intrusion_status.get('max_attempts', 5)} attempts"
                })
        except Exception:
            summary["systems"].append({
                "name": "Intrusion Protection",
                "status": "unavailable",
                "icon": "⚠️",
                "details": "Not configured"
            })
        
        # Physical Security
        try:
            physical = PhysicalSecurityManager()
            physical_status = physical.get_status()
            
            if physical_status.get("sentinel_enabled"):
                if physical_status.get("sentinel_present"):
                    summary["systems"].append({
                        "name": "Physical Security",
                        "status": "active",
                        "icon": "🔑",
                        "details": "USB Sentinel present"
                    })
                else:
                    summary["systems"].append({
                        "name": "Physical Security",
                        "status": "alert",
                        "icon": "🚨",
                        "details": "USB Sentinel MISSING"
                    })
                    summary["overall_status"] = "alert"
            else:
                summary["systems"].append({
                    "name": "Physical Security",
                    "status": "inactive",
                    "icon": "⏸️",
                    "details": "USB Sentinel disabled"
                })
        except Exception:
            summary["systems"].append({
                "name": "Physical Security",
                "status": "unavailable",
                "icon": "⚠️",
                "details": "Not configured"
            })
        
        # User Profiles
        try:
            profile_manager = ProfileManager()
            stats = profile_manager.get_statistics()
            total = stats.get("total_profiles", 0)
            
            summary["systems"].append({
                "name": "User Profiles",
                "status": "active",
                "icon": "👥",
                "details": f"{total} profiles configured"
            })
        except Exception:
            summary["systems"].append({
                "name": "User Profiles",
                "status": "unavailable",
                "icon": "⚠️",
                "details": "Not configured"
            })
        
        return summary
    
    def _get_recent_alerts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent security alerts"""
        from .security_bridge import SecurityBridge
        
        bridge = SecurityBridge()
        alerts_file = bridge.bridge_dir / "security_alerts.json"
        
        if not alerts_file.exists():
            return []
        
        try:
            with open(alerts_file, 'r') as f:
                alerts = json.load(f)
            
            return alerts[-limit:]
            
        except Exception as e:
            logger.error(f"Failed to get alerts: {e}")
            return []
    
    def _get_recent_activity(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent activity from all systems"""
        from .security_bridge import SecurityBridge
        
        bridge = SecurityBridge()
        
        try:
            return bridge.get_unified_logs(limit=limit)
        except Exception as e:
            logger.error(f"Failed to get activity: {e}")
            return []
    
    def _get_system_health(self) -> Dict[str, Any]:
        """Get overall system health metrics"""
        import psutil
        
        health = {
            "cpu_percent": 0,
            "memory_percent": 0,
            "disk_percent": 0,
            "status": "healthy"
        }
        
        try:
            health["cpu_percent"] = psutil.cpu_percent(interval=1)
            health["memory_percent"] = psutil.virtual_memory().percent
            health["disk_percent"] = psutil.disk_usage('/').percent
            
            # Determine health status
            if health["cpu_percent"] > 90 or health["memory_percent"] > 90 or health["disk_percent"] > 90:
                health["status"] = "critical"
            elif health["cpu_percent"] > 75 or health["memory_percent"] > 75 or health["disk_percent"] > 75:
                health["status"] = "warning"
            else:
                health["status"] = "healthy"
                
        except Exception as e:
            logger.error(f"Failed to get system health: {e}")
            health["status"] = "unknown"
        
        return health
    
    def get_quick_actions(self) -> List[Dict[str, Any]]:
        """Get available quick actions for dashboard"""
        actions = [
            {
                "id": "create_pin",
                "name": "Create PIN",
                "description": "Set up 6-digit PIN for a user",
                "command": "pin-auth create",
                "category": "authentication"
            },
            {
                "id": "create_duress",
                "name": "Create Duress PIN",
                "description": "Set up duress code for coercion protection",
                "command": "security-cli duress",
                "category": "security"
            },
            {
                "id": "configure_sentinel",
                "name": "Configure USB Sentinel",
                "description": "Set up physical security dead man's switch",
                "command": "security-cli sentinel",
                "category": "security"
            },
            {
                "id": "create_profile",
                "name": "Create User Profile",
                "description": "Set up security profile for a user",
                "command": "profile-cli create",
                "category": "profiles"
            },
            {
                "id": "backup_now",
                "name": "Backup Now",
                "description": "Perform immediate backup",
                "command": "profile-cli backup",
                "category": "maintenance"
            },
            {
                "id": "view_logs",
                "name": "View Security Logs",
                "description": "View recent security events",
                "command": "security-cli logs",
                "category": "monitoring"
            }
        ]
        
        return actions
    
    def generate_dashboard_html(self) -> str:
        """
        Generate HTML dashboard
        
        Returns:
            HTML string for dashboard
        """
        data = self.get_dashboard_data()
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Unified Security Dashboard</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0f172a;
            color: #e2e8f0;
            padding: 20px;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 30px;
        }}
        .header h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
        .header .timestamp {{ opacity: 0.8; }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .card {{
            background: #1e293b;
            border-radius: 12px;
            padding: 20px;
            border: 1px solid #334155;
        }}
        .card h2 {{
            font-size: 1.5em;
            margin-bottom: 15px;
            color: #60a5fa;
        }}
        .status-item {{
            padding: 12px;
            margin-bottom: 10px;
            background: #0f172a;
            border-radius: 8px;
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .status-icon {{ font-size: 1.5em; }}
        .status-active {{ border-left: 4px solid #10b981; }}
        .status-alert {{ border-left: 4px solid #ef4444; }}
        .status-warning {{ border-left: 4px solid #f59e0b; }}
        .status-inactive {{ border-left: 4px solid #6b7280; }}
        .alert {{
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 8px;
            background: #7f1d1d;
            border-left: 4px solid #ef4444;
        }}
        .alert-critical {{ background: #7f1d1d; }}
        .alert-high {{ background: #78350f; }}
        .alert-medium {{ background: #713f12; }}
        .activity-item {{
            padding: 10px;
            margin-bottom: 8px;
            background: #0f172a;
            border-radius: 6px;
            font-size: 0.9em;
        }}
        .activity-source {{ 
            display: inline-block;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            margin-right: 8px;
        }}
        .source-ai {{ background: #3730a3; }}
        .source-stfd {{ background: #065f46; }}
        .health-metric {{
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #334155;
        }}
        .health-bar {{
            width: 100%;
            height: 8px;
            background: #334155;
            border-radius: 4px;
            overflow: hidden;
            margin-top: 5px;
        }}
        .health-fill {{
            height: 100%;
            transition: width 0.3s;
        }}
        .health-good {{ background: #10b981; }}
        .health-warning {{ background: #f59e0b; }}
        .health-critical {{ background: #ef4444; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ Unified Security Dashboard</h1>
            <div class="timestamp">Last updated: {data['timestamp']}</div>
        </div>
        
        <div class="grid">
            <!-- Local Security -->
            <div class="card">
                <h2>Local Security Systems</h2>
"""
        
        # Add local security systems
        for system in data['local_security']['systems']:
            status_class = f"status-{system['status']}"
            html += f"""
                <div class="status-item {status_class}">
                    <div class="status-icon">{system['icon']}</div>
                    <div>
                        <div><strong>{system['name']}</strong></div>
                        <div style="font-size: 0.9em; opacity: 0.8;">{system['details']}</div>
                    </div>
                </div>
"""
        
        html += """
            </div>
            
            <!-- Network Security -->
            <div class="card">
                <h2>Network Security</h2>
"""
        
        # Add network security status
        for module, status in data['network_security'].items():
            html += f"""
                <div class="status-item">
                    <div><strong>{module.upper()}</strong></div>
                    <div style="font-size: 0.9em; opacity: 0.8;">Status: {status.get('status', 'unknown')}</div>
                </div>
"""
        
        html += """
            </div>
            
            <!-- System Health -->
            <div class="card">
                <h2>System Health</h2>
"""
        
        # Add system health metrics
        health = data['system_health']
        for metric in ['cpu_percent', 'memory_percent', 'disk_percent']:
            value = health.get(metric, 0)
            health_class = 'health-good' if value < 75 else ('health-warning' if value < 90 else 'health-critical')
            html += f"""
                <div class="health-metric">
                    <div>{metric.replace('_', ' ').title()}</div>
                    <div><strong>{value:.1f}%</strong></div>
                </div>
                <div class="health-bar">
                    <div class="health-fill {health_class}" style="width: {value}%"></div>
                </div>
"""
        
        html += """
            </div>
        </div>
        
        <!-- Recent Alerts -->
        <div class="card">
            <h2>Recent Security Alerts</h2>
"""
        
        # Add recent alerts
        if data['recent_alerts']:
            for alert in reversed(data['recent_alerts'][-5:]):
                severity_class = f"alert-{alert.get('severity', 'medium')}"
                html += f"""
            <div class="alert {severity_class}">
                <div><strong>{alert.get('type', 'Unknown').upper()}</strong> - {alert.get('severity', 'medium').upper()}</div>
                <div>{alert.get('message', 'No message')}</div>
                <div style="font-size: 0.8em; opacity: 0.7; margin-top: 5px;">{alert.get('timestamp', '')}</div>
            </div>
"""
        else:
            html += "<div style='opacity: 0.6; padding: 20px; text-align: center;'>No recent alerts</div>"
        
        html += """
        </div>
        
        <!-- Recent Activity -->
        <div class="card">
            <h2>Recent Activity</h2>
"""
        
        # Add recent activity
        if data['recent_activity']:
            for activity in data['recent_activity'][:10]:
                source_class = f"source-{activity.get('source', 'unknown').replace('_', '-')}"
                html += f"""
            <div class="activity-item">
                <span class="activity-source {source_class}">{activity.get('source', 'unknown')}</span>
                <strong>{activity.get('action', 'Unknown action')}</strong>
                <div style="font-size: 0.8em; opacity: 0.7;">{activity.get('timestamp', '')}</div>
            </div>
"""
        else:
            html += "<div style='opacity: 0.6; padding: 20px; text-align: center;'>No recent activity</div>"
        
        html += """
        </div>
    </div>
    
    <script>
        // Auto-refresh every 30 seconds
        setTimeout(() => location.reload(), 30000);
    </script>
</body>
</html>
"""
        
        return html
    
    def save_dashboard_html(self) -> str:
        """Save dashboard HTML to file"""
        html = self.generate_dashboard_html()
        dashboard_file = self.dashboard_dir / "dashboard.html"
        
        try:
            with open(dashboard_file, 'w') as f:
                f.write(html)
            
            logger.info(f"Dashboard saved to {dashboard_file}")
            return str(dashboard_file)
            
        except Exception as e:
            logger.error(f"Failed to save dashboard: {e}")
            return ""
