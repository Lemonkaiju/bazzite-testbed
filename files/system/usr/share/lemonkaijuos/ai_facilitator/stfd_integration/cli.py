#!/usr/bin/env python3
"""
STFD Integration CLI
Command-line interface for STFD integration features
"""

import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ai_facilitator.stfd_integration import SecurityBridge, UnifiedDashboard, NetworkCoordinator

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)

logger = logging.getLogger(__name__)


def print_header(text: str):
    """Print formatted header"""
    print("\n" + "="*60)
    print(text)
    print("="*60 + "\n")


def show_dashboard():
    """Show unified security dashboard"""
    print_header("Unified Security Dashboard")
    
    dashboard = UnifiedDashboard()
    data = dashboard.get_dashboard_data()
    
    # Local Security
    print("LOCAL SECURITY:")
    local = data['local_security']
    print(f"  Overall Status: {local['overall_status'].upper()}")
    print()
    
    for system in local['systems']:
        print(f"  {system['icon']} {system['name']}")
        print(f"     Status: {system['status']}")
        print(f"     {system['details']}")
        print()
    
    # Network Security
    print("NETWORK SECURITY:")
    for module, status in data['network_security'].items():
        print(f"  • {module.upper()}: {status.get('status', 'unknown')}")
    print()
    
    # System Health
    print("SYSTEM HEALTH:")
    health = data['system_health']
    print(f"  CPU: {health.get('cpu_percent', 0):.1f}%")
    print(f"  Memory: {health.get('memory_percent', 0):.1f}%")
    print(f"  Disk: {health.get('disk_percent', 0):.1f}%")
    print(f"  Status: {health.get('status', 'unknown').upper()}")
    print()
    
    # Recent Alerts
    if data['recent_alerts']:
        print("RECENT ALERTS:")
        for alert in data['recent_alerts'][-5:]:
            print(f"  [{alert.get('severity', 'unknown').upper()}] {alert.get('type', 'unknown')}")
            print(f"  {alert.get('message', 'No message')}")
            print(f"  {alert.get('timestamp', '')}")
            print()
    
    print("\nFor HTML dashboard, run: stfd-cli html")


def generate_html_dashboard():
    """Generate HTML dashboard"""
    print_header("Generate HTML Dashboard")
    
    dashboard = UnifiedDashboard()
    dashboard_file = dashboard.save_dashboard_html()
    
    if dashboard_file:
        print(f"✓ Dashboard saved to: {dashboard_file}")
        print(f"\nOpen in browser:")
        print(f"  file://{dashboard_file}")
    else:
        print("✗ Failed to generate dashboard")


def show_security_status():
    """Show security status"""
    print_header("Security Status")
    
    bridge = SecurityBridge()
    status = bridge.get_security_status()
    
    print(f"Timestamp: {status['timestamp']}")
    print()
    
    for system_name, system_status in status['systems'].items():
        print(f"{system_name.upper().replace('_', ' ')}:")
        
        if system_status.get('available'):
            print(f"  ✓ Available")
            for key, value in system_status.items():
                if key != 'available':
                    print(f"  {key}: {value}")
        else:
            print(f"  ✗ Not available")
            if 'error' in system_status:
                print(f"  Error: {system_status['error']}")
        print()


def show_network_status():
    """Show network status"""
    print_header("Network Status")
    
    coordinator = NetworkCoordinator()
    status = coordinator.get_network_status()
    
    print(f"Timestamp: {status['timestamp']}")
    print(f"Lockdown Active: {'YES' if status['lockdown_active'] else 'NO'}")
    print()
    
    if status['modules']:
        print("STFD Modules:")
        for module_id, module_data in status['modules'].items():
            print(f"  • {module_data.get('name', module_id)}")
            print(f"    Status: {module_data.get('status', 'unknown')}")
            print(f"    Configured: {'Yes' if module_data.get('configured') else 'No'}")
            print()
    else:
        print("No STFD modules configured")
    
    # Network health
    print("\nNetwork Health:")
    health = coordinator.monitor_network_health()
    print(f"  Connectivity: {health.get('connectivity', 'unknown')}")
    print(f"  Latency: {health.get('latency_ms', 0):.1f} ms")
    print(f"  VPN Active: {'Yes' if health.get('vpn_active') else 'No'}")


def view_unified_logs():
    """View unified logs"""
    print_header("Unified Logs")
    
    bridge = SecurityBridge()
    logs = bridge.get_unified_logs(limit=20)
    
    if logs:
        for log in logs:
            source = log.get('source', 'unknown')
            action = log.get('action', 'unknown')
            status = log.get('status', 'unknown')
            timestamp = log.get('timestamp', '')
            
            print(f"[{source.upper()}] {action}")
            print(f"  Status: {status}")
            print(f"  Time: {timestamp}")
            print()
    else:
        print("No logs available")


def register_with_stfd():
    """Register AI Facilitator with STFD"""
    print_header("Register with STFD")
    
    bridge = SecurityBridge()
    result = bridge.register_with_stfd()
    
    if result['success']:
        print(f"✓ Successfully registered with STFD")
        print(f"  Config file: {result['config_file']}")
    else:
        print(f"✗ Registration failed: {result.get('error')}")


def clear_lockdown():
    """Clear network lockdown"""
    print_header("Clear Network Lockdown")
    
    coordinator = NetworkCoordinator()
    
    # Check if lockdown is active
    status = coordinator.check_network_lockdown_status()
    
    if not status.get('active'):
        print("No active network lockdown")
        return
    
    print("Active lockdown detected:")
    print(f"  Triggered by: {status.get('triggered_by', 'unknown')}")
    print(f"  Timestamp: {status.get('timestamp', 'unknown')}")
    print()
    
    authorized_by = input("Enter your username to authorize clearance: ").strip()
    
    if not authorized_by:
        print("Cancelled")
        return
    
    confirm = input(f"Clear network lockdown? (y/N): ").strip().lower()
    
    if confirm == 'y':
        result = coordinator.clear_network_lockdown(authorized_by)
        
        if result['success']:
            print(f"\n✓ {result['message']}")
        else:
            print(f"\n✗ Error: {result.get('error')}")


def sync_policies():
    """Sync security policies"""
    print_header("Sync Security Policies")
    
    coordinator = NetworkCoordinator()
    result = coordinator.sync_security_policies()
    
    if result['success']:
        print(f"✓ Policies synced successfully")
        print(f"  File: {result['policies_file']}")
    else:
        print(f"✗ Sync failed: {result.get('error')}")


def show_help():
    """Show help message"""
    print("""
STFD Integration CLI

Usage: stfd-cli <command>

Commands:
  dashboard           Show unified security dashboard
  html                Generate HTML dashboard
  security            Show security status
  network             Show network status
  logs                View unified logs
  register            Register with STFD installer
  lockdown-clear      Clear network lockdown
  sync-policies       Sync security policies
  help                Show this help message

Dashboard:
  Unified view of AI Facilitator and STFD security systems.
  
Integration:
  Bridges local security (AI Facilitator) with network security (STFD).
  
Examples:
  stfd-cli dashboard      # View dashboard in terminal
  stfd-cli html           # Generate HTML dashboard
  stfd-cli security       # Check security status
  stfd-cli network        # Check network status

For more information, see the documentation.
""")


def main():
    """Main CLI entry point"""
    if len(sys.argv) < 2:
        show_help()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    commands = {
        'dashboard': show_dashboard,
        'html': generate_html_dashboard,
        'security': show_security_status,
        'network': show_network_status,
        'logs': view_unified_logs,
        'register': register_with_stfd,
        'lockdown-clear': clear_lockdown,
        'sync-policies': sync_policies,
        'help': show_help,
    }
    
    if command in commands:
        try:
            commands[command]()
        except KeyboardInterrupt:
            print("\n\nCancelled by user")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Command failed: {e}", exc_info=True)
            sys.exit(1)
    else:
        print(f"Unknown command: {command}")
        print("Use 'stfd-cli help' for usage information")
        sys.exit(1)


if __name__ == "__main__":
    main()
