#!/usr/bin/env python3
"""
PIN Authentication CLI
Command-line interface for PIN management
"""

import sys
import getpass
import logging
from pathlib import Path
from typing import Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ai_facilitator.pin_auth import PINManager, PAMConfigurator, RecoveryManager

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


def create_pin():
    """Create a new PIN"""
    print_header("Create New PIN")
    
    username = input("Username: ").strip()
    if not username:
        print("Error: Username is required")
        return
    
    pin_manager = PINManager()
    
    # Check if PIN already exists
    if pin_manager.has_pin(username):
        response = input(f"PIN already exists for {username}. Replace? (y/N): ")
        if response.lower() != 'y':
            print("Cancelled")
            return
    
    # Get PIN
    pin = getpass.getpass("Enter 6-digit PIN: ")
    verify_pin = getpass.getpass("Verify PIN: ")
    
    # Create PIN
    result = pin_manager.create_pin(username, pin, verify_pin)
    
    if result['success']:
        print(f"\n✓ {result['message']}")
        print("\nIMPORTANT: Remember your PIN. You will need it for sudo and login.")
        print("If you forget it, you can reset it using your long password.")
    else:
        print(f"\n✗ Error: {result['error']}")


def change_pin():
    """Change existing PIN"""
    print_header("Change PIN")
    
    username = input("Username: ").strip()
    if not username:
        print("Error: Username is required")
        return
    
    pin_manager = PINManager()
    
    # Check if PIN exists
    if not pin_manager.has_pin(username):
        print(f"Error: No PIN set for {username}")
        print("Use 'create' command to create a new PIN")
        return
    
    # Get PINs
    old_pin = getpass.getpass("Current PIN: ")
    new_pin = getpass.getpass("New 6-digit PIN: ")
    verify_new_pin = getpass.getpass("Verify new PIN: ")
    
    # Change PIN
    result = pin_manager.change_pin(username, old_pin, new_pin, verify_new_pin)
    
    if result['success']:
        print(f"\n✓ {result['message']}")
    else:
        print(f"\n✗ Error: {result['error']}")


def reset_pin():
    """Reset PIN using password"""
    print_header("Reset PIN with Password")
    
    username = input("Username: ").strip()
    if not username:
        print("Error: Username is required")
        return
    
    recovery_manager = RecoveryManager()
    
    # Get password and new PIN
    password = getpass.getpass("Long password: ")
    new_pin = getpass.getpass("New 6-digit PIN: ")
    verify_new_pin = getpass.getpass("Verify new PIN: ")
    
    # Reset PIN
    result = recovery_manager.reset_pin_with_password(
        username, password, new_pin, verify_new_pin
    )
    
    if result['success']:
        print(f"\n✓ {result['message']}")
    else:
        print(f"\n✗ Error: {result['error']}")


def generate_recovery_code():
    """Generate recovery code"""
    print_header("Generate Recovery Code")
    
    username = input("Username: ").strip()
    if not username:
        print("Error: Username is required")
        return
    
    recovery_manager = RecoveryManager()
    
    result = recovery_manager.generate_recovery_code(username)
    
    if result['success']:
        print(f"\n✓ Recovery code generated!")
        print(f"\nRecovery Code: {result['recovery_code']}")
        print("\nIMPORTANT:")
        print("  • Write this code down and store it in a safe place")
        print("  • This code can be used ONCE to reset your PIN")
        print("  • Do not share this code with anyone")
    else:
        print(f"\n✗ Error: {result['error']}")


def unlock_account():
    """Unlock account after failed attempts"""
    print_header("Unlock Account")
    
    username = input("Username: ").strip()
    if not username:
        print("Error: Username is required")
        return
    
    recovery_manager = RecoveryManager()
    
    # Check current status
    status = recovery_manager.get_faillock_status(username)
    if not status.get('locked', False):
        print(f"Account {username} is not locked")
        return
    
    print(f"Account {username} is locked due to failed login attempts")
    
    # Get password
    password = getpass.getpass("Long password to unlock: ")
    
    # Unlock
    result = recovery_manager.unlock_after_failed_attempts(username, password)
    
    if result['success']:
        print(f"\n✓ {result['message']}")
    else:
        print(f"\n✗ Error: {result['error']}")


def check_status():
    """Check PIN authentication status"""
    print_header("PIN Authentication Status")
    
    username = input("Username (optional): ").strip()
    
    pin_manager = PINManager()
    pam_config = PAMConfigurator()
    
    # Check PAM configuration
    verification = pam_config.verify_pin_support()
    
    print("System Configuration:")
    print(f"  sudo configured: {'✓' if verification['checks']['sudo_configured'] else '✗'}")
    print(f"  GDM configured: {'✓' if verification['checks']['gdm_configured'] else '✗'}")
    print(f"  faillock configured: {'✓' if verification['checks']['faillock_configured'] else '✗'}")
    print(f"  PIN database exists: {'✓' if verification['checks']['pin_db_exists'] else '✗'}")
    
    if username:
        print(f"\nUser Status ({username}):")
        print(f"  PIN set: {'✓' if pin_manager.has_pin(username) else '✗'}")
        
        # Check faillock status
        recovery_manager = RecoveryManager()
        faillock_status = recovery_manager.get_faillock_status(username)
        print(f"  Account locked: {'✓' if faillock_status.get('locked', False) else '✗'}")
        
        # Show PIN history
        history = pin_manager.get_pin_history(username, limit=5)
        if history:
            print(f"\n  Recent PIN changes:")
            for entry in history:
                print(f"    • {entry['timestamp']}: {entry['action']}")


def configure_system():
    """Configure system for PIN authentication"""
    print_header("Configure System for PIN Authentication")
    
    print("This will configure PAM for PIN authentication.")
    print("Backups will be created automatically.")
    print("\nWARNING: This requires root access and will modify system files.")
    
    response = input("\nContinue? (y/N): ")
    if response.lower() != 'y':
        print("Cancelled")
        return
    
    pam_config = PAMConfigurator()
    
    # Configure sudo
    print("\nConfiguring sudo...")
    result = pam_config.configure_sudo_pin()
    if result['success']:
        print(f"✓ {result['message']}")
    else:
        print(f"✗ {result['error']}")
        return
    
    # Configure GDM
    print("\nConfiguring GDM (login)...")
    result = pam_config.configure_gdm_pin()
    if result['success']:
        print(f"✓ {result['message']}")
    else:
        print(f"✗ {result['error']}")
        return
    
    # Configure faillock
    print("\nConfiguring faillock...")
    result = pam_config.configure_faillock()
    if result['success']:
        print(f"✓ {result['message']}")
    else:
        print(f"✗ {result['error']}")
        return
    
    print("\n" + "="*60)
    print("System configured successfully!")
    print("="*60)
    print("\nNext steps:")
    print("  1. Create a PIN: pin-auth create")
    print("  2. Test sudo: sudo -v")
    print("  3. Test login: logout and login with PIN")


def show_help():
    """Show help message"""
    print("""
PIN Authentication CLI

Usage: pin-auth <command> [options]

Commands:
  create              Create a new PIN
  change              Change existing PIN
  reset               Reset PIN using long password
  unlock              Unlock account after failed attempts
  recovery            Generate recovery code
  status              Check PIN authentication status
  configure           Configure system for PIN authentication
  help                Show this help message

Examples:
  pin-auth create     # Create a new PIN
  pin-auth change     # Change your PIN
  pin-auth reset      # Reset PIN with password
  pin-auth status     # Check system status

For more information, see the documentation.
""")


def main():
    """Main CLI entry point"""
    if len(sys.argv) < 2:
        show_help()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    commands = {
        'create': create_pin,
        'change': change_pin,
        'reset': reset_pin,
        'unlock': unlock_account,
        'recovery': generate_recovery_code,
        'status': check_status,
        'configure': configure_system,
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
        print("Use 'pin-auth help' for usage information")
        sys.exit(1)


if __name__ == "__main__":
    main()
