#!/usr/bin/env python3
"""
Security Systems CLI
Command-line interface for duress, intrusion, and physical security
"""

import sys
import getpass
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ai_facilitator.security import DuressManager, IntrusionProtection, PhysicalSecurityManager
from ai_facilitator.pin_auth import PINManager

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


def create_duress_pin():
    """Create a duress PIN"""
    print_header("Create Duress PIN")
    
    print("A duress PIN is used when you're being coerced to unlock your device.")
    print("When entered, it will:")
    print("  • Send a silent alert to your other devices")
    print("  • Unmount sensitive containers")
    print("  • Appear to fail authentication (Houdini)")
    print("")
    
    username = input("Username: ").strip()
    if not username:
        print("Error: Username is required")
        return
    
    # Verify user has normal PIN
    pin_manager = PINManager()
    if not pin_manager.has_pin(username):
        print(f"Error: No normal PIN set for {username}")
        print("Create a normal PIN first with: pin-auth create")
        return
    
    duress_manager = DuressManager()
    
    # Check if duress PIN already exists
    if duress_manager.has_duress_pin(username):
        response = input(f"Duress PIN already exists for {username}. Replace? (y/N): ")
        if response.lower() != 'y':
            print("Cancelled")
            return
    
    # Get PINs
    normal_pin = getpass.getpass("Enter your normal PIN (for verification): ")
    duress_pin = getpass.getpass("Enter duress PIN (6 digits, different from normal): ")
    verify_duress = getpass.getpass("Verify duress PIN: ")
    
    # Create duress PIN
    result = duress_manager.create_duress_pin(
        username, normal_pin, duress_pin, verify_duress
    )
    
    if result['success']:
        print(f"\n✓ {result['message']}")
        print("\nIMPORTANT:")
        print("  • Remember your duress PIN")
        print("  • Use it ONLY when being coerced")
        print("  • It will trigger silent protective measures")
        print("  • The attacker will not know it was activated")
    else:
        print(f"\n✗ Error: {result['error']}")


def configure_duress_alerts():
    """Configure duress alert devices"""
    print_header("Configure Duress Alerts")
    
    print("Configure devices that will receive silent alerts when duress PIN is used.")
    print("")
    
    # This would integrate with mobile app or other alert systems
    print("Alert configuration:")
    print("  1. Mobile device (via encrypted file)")
    print("  2. Email (encrypted)")
    print("  3. Signal/Matrix message")
    print("")
    
    print("Note: Full alert integration requires additional setup")
    print("See documentation for details")


def configure_sentinel():
    """Configure USB sentinel"""
    print_header("Configure USB Sentinel")
    
    print("USB Sentinel is a physical USB device that acts as a 'dead man's switch'")
    print("If removed, the system will:")
    print("  • Lock immediately")
    print("  • Unmount all containers")
    print("  • Optionally wipe RAM (cold boot protection)")
    print("")
    
    physical_security = PhysicalSecurityManager()
    
    print("Current configuration:")
    status = physical_security.get_status()
    print(f"  Sentinel enabled: {status['sentinel_enabled']}")
    print(f"  Sentinel present: {status['sentinel_present']}")
    print(f"  Dead man's switch: {status['dead_mans_switch_enabled']}")
    print("")
    
    response = input("Configure sentinel? (y/N): ")
    if response.lower() != 'y':
        return
    
    print("\nSentinel identification method:")
    print("  1. USB Vendor/Product ID (recommended)")
    print("  2. Volume label")
    
    method = input("Choose method (1/2): ").strip()
    
    if method == "1":
        print("\nFind your USB device ID:")
        print("  Run: lsusb")
        print("  Look for your device, note the ID (e.g., 1234:5678)")
        print("")
        
        vendor_id = input("Vendor ID (4 hex digits): ").strip()
        product_id = input("Product ID (4 hex digits): ").strip()
        
        result = physical_security.configure_sentinel(
            vendor_id=vendor_id,
            product_id=product_id
        )
        
    elif method == "2":
        label = input("Volume label: ").strip()
        
        result = physical_security.configure_sentinel(label=label)
    else:
        print("Invalid choice")
        return
    
    if result['success']:
        print(f"\n✓ {result['message']}")
        print("\nTest by removing the USB device - system should lock")
    else:
        print(f"\n✗ Error: {result['error']}")


def check_security_status():
    """Check security systems status"""
    print_header("Security Systems Status")
    
    username = input("Username (optional): ").strip()
    
    # Duress status
    print("Duress Protection:")
    duress_manager = DuressManager()
    if username:
        has_duress = duress_manager.has_duress_pin(username)
        print(f"  Duress PIN configured: {'✓' if has_duress else '✗'}")
        
        if has_duress:
            config = duress_manager.get_duress_config(username)
            if config:
                print(f"  Alert devices: {len(config.get('alert_devices', []))}")
                print(f"  Houdini enabled: {config.get('houdini_enabled', False)}")
    
    # Intrusion protection status
    print("\nIntrusion Protection:")
    intrusion = IntrusionProtection()
    intrusion_status = intrusion.get_status()
    print(f"  Enabled: ✓")
    print(f"  Max attempts: {intrusion_status['max_attempts']}")
    print(f"  Lockout action: {intrusion_status['lockout_action']}")
    print(f"  Recent intrusions: {intrusion_status['recent_intrusions']}")
    
    if username:
        long_pw_required = intrusion.check_long_password_required(username)
        print(f"  Long password required: {'✓' if long_pw_required else '✗'}")
    
    # Physical security status
    print("\nPhysical Security:")
    physical = PhysicalSecurityManager()
    physical_status = physical.get_status()
    print(f"  Sentinel enabled: {'✓' if physical_status['sentinel_enabled'] else '✗'}")
    print(f"  Sentinel present: {'✓' if physical_status['sentinel_present'] else '✗'}")
    print(f"  Dead man's switch: {'✓' if physical_status['dead_mans_switch_enabled'] else '✗'}")
    print(f"  Monitoring active: {'✓' if physical_status['monitoring'] else '✗'}")


def view_security_logs():
    """View security event logs"""
    print_header("Security Event Logs")
    
    print("1. Duress activations")
    print("2. Intrusion attempts")
    print("3. Physical security events")
    
    choice = input("\nView logs (1/2/3): ").strip()
    
    if choice == "1":
        duress_manager = DuressManager()
        activations = duress_manager.get_activation_history(limit=10)
        
        if activations:
            print("\nRecent duress activations:")
            for event in activations:
                print(f"\n  {event['timestamp']}")
                print(f"  User: {event['username']}")
                print(f"  Actions: {', '.join(event['actions'])}")
        else:
            print("\nNo duress activations recorded")
    
    elif choice == "2":
        intrusion = IntrusionProtection()
        intrusions = intrusion.get_intrusion_log(limit=10)
        
        if intrusions:
            print("\nRecent intrusion attempts:")
            for event in intrusions:
                print(f"\n  {event['timestamp']}")
                print(f"  User: {event['username']}")
                print(f"  Trigger: {event['trigger_reason']}")
                print(f"  Actions: {', '.join(event['actions_taken'])}")
        else:
            print("\nNo intrusion attempts recorded")
    
    elif choice == "3":
        physical = PhysicalSecurityManager()
        events = physical.get_security_events(limit=10)
        
        if events:
            print("\nRecent physical security events:")
            for event in events:
                print(f"\n  {event['timestamp']}")
                print(f"  Type: {event['type']}")
                print(f"  Actions: {', '.join(event['actions'])}")
        else:
            print("\nNo physical security events recorded")
    else:
        print("Invalid choice")


def start_monitoring():
    """Start security monitoring"""
    print_header("Start Security Monitoring")
    
    print("Starting security monitoring services...")
    
    # Start physical security monitoring
    physical = PhysicalSecurityManager()
    physical.start_monitoring()
    
    print("✓ Physical security monitoring started")
    print("\nMonitoring:")
    print("  • USB sentinel presence")
    print("  • Dead man's switch")
    print("")
    print("Press Ctrl+C to stop monitoring")
    
    try:
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nStopping monitoring...")
        physical.stop_monitoring()
        print("✓ Monitoring stopped")


def show_help():
    """Show help message"""
    print("""
Security Systems CLI

Usage: security-cli <command>

Commands:
  duress              Create duress PIN
  alerts              Configure duress alerts
  sentinel            Configure USB sentinel
  status              Check security status
  logs                View security event logs
  monitor             Start security monitoring
  help                Show this help message

Duress Protection:
  A duress PIN triggers silent protective measures when you're being coerced.
  Use 'security-cli duress' to set it up.

Intrusion Protection:
  Automatically responds to failed login attempts with system shutdown.
  Configured via intrusion protection settings.

Physical Security:
  USB sentinel acts as a dead man's switch - removal triggers lockdown.
  Use 'security-cli sentinel' to configure.

Examples:
  security-cli duress     # Create duress PIN
  security-cli sentinel   # Configure USB sentinel
  security-cli status     # Check all security systems
  security-cli monitor    # Start monitoring

For more information, see the documentation.
""")


def main():
    """Main CLI entry point"""
    if len(sys.argv) < 2:
        show_help()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    commands = {
        'duress': create_duress_pin,
        'alerts': configure_duress_alerts,
        'sentinel': configure_sentinel,
        'status': check_security_status,
        'logs': view_security_logs,
        'monitor': start_monitoring,
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
        print("Use 'security-cli help' for usage information")
        sys.exit(1)


if __name__ == "__main__":
    main()
