#!/usr/bin/env python3
"""
Security Profiles CLI
Command-line interface for profile management
"""

import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ai_facilitator.profiles import ProfileManager, KioskMode, BackupAutomation
from ai_facilitator.profiles.profile_manager import ProfileType

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


def create_profile():
    """Create a new user profile"""
    print_header("Create User Profile")
    
    username = input("Username: ").strip()
    if not username:
        print("Error: Username is required")
        return
    
    print("\nProfile Types:")
    print("  1. Primary User (Full access, all security features)")
    print("  2. Less Technical User (Simplified, AI approval required)")
    print("  3. Kids/Temporary User (Restricted, kiosk mode)")
    
    choice = input("\nSelect profile type (1/2/3): ").strip()
    
    if choice == "1":
        profile_type = ProfileType.PRIMARY
    elif choice == "2":
        profile_type = ProfileType.LESS_TECHNICAL
    elif choice == "3":
        profile_type = ProfileType.KIDS_TEMPORARY
    else:
        print("Invalid choice")
        return
    
    display_name = input(f"Display name (default: {username}): ").strip() or username
    
    # Additional configuration for kids profile
    allowed_apps = None
    if profile_type == ProfileType.KIDS_TEMPORARY:
        print("\nDefault allowed apps:")
        print("  • Firefox")
        print("  • LibreOffice")
        print("  • GNOME Games")
        
        custom = input("\nCustomize allowed apps? (y/N): ").strip().lower()
        if custom == 'y':
            print("Enter Flatpak app IDs (one per line, empty line to finish):")
            allowed_apps = []
            while True:
                app = input("  App ID: ").strip()
                if not app:
                    break
                allowed_apps.append(app)
    
    # Create profile
    profile_manager = ProfileManager()
    
    kwargs = {}
    if allowed_apps:
        kwargs['allowed_apps'] = allowed_apps
    
    result = profile_manager.create_profile(
        username,
        profile_type,
        display_name,
        **kwargs
    )
    
    if result['success']:
        print(f"\n✓ {result['message']}")
        print(f"\nProfile type: {result['profile_type']}")
        
        if profile_type == ProfileType.PRIMARY:
            print("\nFeatures enabled:")
            print("  • 6-digit PIN authentication")
            print("  • Duress PIN protection")
            print("  • Physical security (USB sentinel)")
            print("  • Daily automated backups")
            
        elif profile_type == ProfileType.LESS_TECHNICAL:
            print("\nFeatures enabled:")
            print("  • 6-digit PIN authentication")
            print("  • AI approval for system changes")
            print("  • Daily automated backups")
            print("  • Daily rollback safety net")
            
        elif profile_type == ProfileType.KIDS_TEMPORARY:
            print("\nFeatures enabled:")
            print("  • 4-digit PIN authentication")
            print("  • Kiosk mode (restricted apps)")
            print("  • Hourly automated backups")
            print("  • No system changes allowed")
        
        print("\nNext steps:")
        print(f"  1. Create PIN: pin-auth create")
        print(f"  2. Test login with new profile")
        
    else:
        print(f"\n✗ Error: {result['error']}")


def list_profiles():
    """List all profiles"""
    print_header("User Profiles")
    
    profile_manager = ProfileManager()
    profiles = profile_manager.list_profiles()
    
    if not profiles:
        print("No profiles configured")
        return
    
    for profile in profiles:
        print(f"\n{profile['display_name']} ({profile['username']})")
        print(f"  Type: {profile['type']}")
        print(f"  Created: {profile['created'][:10]}")
        
        # Get additional info
        full_profile = profile_manager.get_profile(profile['username'])
        if full_profile:
            if full_profile.get('kiosk_mode'):
                print(f"  Kiosk mode: Enabled")
            if full_profile.get('ai_approval_required'):
                print(f"  AI approval: Required")
            if full_profile.get('auto_backup_enabled'):
                print(f"  Backups: {full_profile.get('backup_interval', 'daily')}")


def show_profile():
    """Show detailed profile information"""
    print_header("Profile Details")
    
    username = input("Username: ").strip()
    if not username:
        print("Error: Username is required")
        return
    
    profile_manager = ProfileManager()
    profile = profile_manager.get_profile(username)
    
    if not profile:
        print(f"No profile found for {username}")
        return
    
    print(f"\nProfile: {profile.get('display_name', username)}")
    print(f"Username: {username}")
    print(f"Type: {profile.get('type')}")
    print(f"Created: {profile.get('created')}")
    print(f"Updated: {profile.get('updated')}")
    
    print("\nAuthentication:")
    print(f"  PIN length: {profile.get('pin_length')} digits")
    print(f"  Duress PIN: {'Enabled' if profile.get('duress_pin_enabled') else 'Disabled'}")
    
    print("\nSecurity:")
    print(f"  Physical security: {'Enabled' if profile.get('physical_security_enabled') else 'Disabled'}")
    print(f"  Kiosk mode: {'Enabled' if profile.get('kiosk_mode') else 'Disabled'}")
    
    print("\nSystem Access:")
    print(f"  AI approval required: {'Yes' if profile.get('ai_approval_required') else 'No'}")
    
    if profile.get('kiosk_mode'):
        allowed_apps = profile.get('allowed_apps', [])
        print(f"  Allowed apps: {len(allowed_apps)}")
        if allowed_apps and len(allowed_apps) <= 10:
            for app in allowed_apps:
                print(f"    • {app}")
    
    print("\nBackups:")
    print(f"  Auto-backup: {'Enabled' if profile.get('auto_backup_enabled') else 'Disabled'}")
    if profile.get('auto_backup_enabled'):
        print(f"  Interval: {profile.get('backup_interval', 'daily')}")
    
    # Show permissions
    print("\nPermissions:")
    permissions = profile_manager.get_permissions(username)
    for perm, allowed in permissions.items():
        status = "✓" if allowed else "✗"
        print(f"  {status} {perm}")


def manage_kiosk():
    """Manage kiosk mode"""
    print_header("Manage Kiosk Mode")
    
    username = input("Username: ").strip()
    if not username:
        print("Error: Username is required")
        return
    
    kiosk = KioskMode()
    
    if not kiosk.is_kiosk_enabled(username):
        print(f"Kiosk mode not enabled for {username}")
        return
    
    print("\nKiosk Mode Management:")
    print("  1. List allowed apps")
    print("  2. Add allowed app")
    print("  3. Remove allowed app")
    print("  4. Disable kiosk mode")
    
    choice = input("\nSelect action (1/2/3/4): ").strip()
    
    if choice == "1":
        apps = kiosk.get_allowed_apps(username)
        print(f"\nAllowed apps ({len(apps)}):")
        for app in apps:
            print(f"  • {app}")
    
    elif choice == "2":
        app_id = input("Flatpak app ID to add: ").strip()
        if app_id:
            result = kiosk.add_allowed_app(username, app_id)
            if result['success']:
                print(f"\n✓ {result['message']}")
            else:
                print(f"\n✗ Error: {result['error']}")
    
    elif choice == "3":
        app_id = input("Flatpak app ID to remove: ").strip()
        if app_id:
            result = kiosk.remove_allowed_app(username, app_id)
            if result['success']:
                print(f"\n✓ {result['message']}")
            else:
                print(f"\n✗ Error: {result['error']}")
    
    elif choice == "4":
        confirm = input("Disable kiosk mode? (y/N): ").strip().lower()
        if confirm == 'y':
            result = kiosk.disable_kiosk_mode(username)
            if result['success']:
                print(f"\n✓ {result['message']}")
            else:
                print(f"\n✗ Error: {result['error']}")


def manage_backups():
    """Manage backups"""
    print_header("Manage Backups")
    
    username = input("Username: ").strip()
    if not username:
        print("Error: Username is required")
        return
    
    backup = BackupAutomation()
    
    print("\nBackup Management:")
    print("  1. Show backup status")
    print("  2. Perform backup now")
    print("  3. List backups")
    print("  4. Restore backup")
    print("  5. Delete backup")
    
    choice = input("\nSelect action (1/2/3/4/5): ").strip()
    
    if choice == "1":
        status = backup.get_backup_status(username)
        if status.get('configured'):
            print(f"\nBackup Status:")
            print(f"  Enabled: {status.get('enabled')}")
            print(f"  Interval: {status.get('interval')}")
            print(f"  Keep count: {status.get('keep_count')}")
            print(f"  Last backup: {status.get('last_backup', 'Never')}")
            print(f"  Total backups: {status.get('backup_count', 0)}")
            print(f"  Total size: {status.get('total_size_mb', 0):.2f} MB")
        else:
            print("\nBackup not configured")
    
    elif choice == "2":
        print("\nPerforming backup...")
        result = backup.perform_backup(username)
        if result['success']:
            print(f"\n✓ {result['message']}")
            print(f"  File: {result['backup_file']}")
            print(f"  Size: {result['size_mb']:.2f} MB")
        else:
            print(f"\n✗ Error: {result['error']}")
    
    elif choice == "3":
        backups = backup.list_backups(username)
        if backups:
            print(f"\nBackups for {username}:")
            for i, b in enumerate(backups, 1):
                print(f"\n{i}. {b['filename']}")
                print(f"   Size: {b['size_mb']:.2f} MB")
                print(f"   Created: {b['created']}")
        else:
            print("\nNo backups found")
    
    elif choice == "4":
        backups = backup.list_backups(username)
        if not backups:
            print("\nNo backups available")
            return
        
        print("\nAvailable backups:")
        for i, b in enumerate(backups, 1):
            print(f"{i}. {b['filename']} ({b['size_mb']:.2f} MB)")
        
        choice = input("\nSelect backup to restore (number or 'latest'): ").strip()
        
        if choice.lower() == 'latest':
            backup_file = backups[0]['path']
        else:
            try:
                idx = int(choice) - 1
                backup_file = backups[idx]['path']
            except (ValueError, IndexError):
                print("Invalid selection")
                return
        
        confirm = input(f"\nRestore from {Path(backup_file).name}? (y/N): ").strip().lower()
        if confirm == 'y':
            result = backup.restore_backup(username, backup_file)
            if result['success']:
                print(f"\n✓ {result['message']}")
            else:
                print(f"\n✗ Error: {result['error']}")
    
    elif choice == "5":
        backups = backup.list_backups(username)
        if not backups:
            print("\nNo backups available")
            return
        
        print("\nAvailable backups:")
        for i, b in enumerate(backups, 1):
            print(f"{i}. {b['filename']} ({b['size_mb']:.2f} MB)")
        
        choice = input("\nSelect backup to delete (number): ").strip()
        
        try:
            idx = int(choice) - 1
            backup_file = backups[idx]['path']
        except (ValueError, IndexError):
            print("Invalid selection")
            return
        
        confirm = input(f"\nDelete {Path(backup_file).name}? (y/N): ").strip().lower()
        if confirm == 'y':
            result = backup.delete_backup(username, backup_file)
            if result['success']:
                print(f"\n✓ {result['message']}")
            else:
                print(f"\n✗ Error: {result['error']}")


def show_statistics():
    """Show profile statistics"""
    print_header("Profile Statistics")
    
    profile_manager = ProfileManager()
    stats = profile_manager.get_statistics()
    
    print(f"Total profiles: {stats['total_profiles']}")
    print(f"\nBy type:")
    print(f"  Primary users: {stats['by_type']['primary']}")
    print(f"  Less technical users: {stats['by_type']['less_technical']}")
    print(f"  Kids/temporary users: {stats['by_type']['kids_temporary']}")


def show_help():
    """Show help message"""
    print("""
Security Profiles CLI

Usage: profile-cli <command>

Commands:
  create              Create a new user profile
  list                List all profiles
  show                Show detailed profile information
  kiosk               Manage kiosk mode
  backup              Manage backups
  stats               Show profile statistics
  help                Show this help message

Profile Types:
  PRIMARY             Full access, all security features
  LESS_TECHNICAL      Simplified, AI approval required
  KIDS_TEMPORARY      Restricted, kiosk mode

Examples:
  profile-cli create  # Create a new profile
  profile-cli list    # List all profiles
  profile-cli show    # Show profile details
  profile-cli kiosk   # Manage kiosk mode
  profile-cli backup  # Manage backups

For more information, see the documentation.
""")


def main():
    """Main CLI entry point"""
    if len(sys.argv) < 2:
        show_help()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    commands = {
        'create': create_profile,
        'list': list_profiles,
        'show': show_profile,
        'kiosk': manage_kiosk,
        'backup': manage_backups,
        'stats': show_statistics,
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
        print("Use 'profile-cli help' for usage information")
        sys.exit(1)


if __name__ == "__main__":
    main()
