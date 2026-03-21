# Security Profiles System

**Different security and access levels for different user types**

Comprehensive profile management system for LemonKaijuOS that provides appropriate security and usability for primary users, less technical users, and kids/temporary users.

## Profile Types

### PRIMARY User
**Full access with all security features**

- 6-digit PIN authentication
- Duress PIN protection
- Physical security (USB sentinel)
- All system permissions
- AI facilitator access
- Daily automated backups

**Use case:** System administrator, primary family member

### LESS_TECHNICAL User
**Simplified with AI approval required**

- 6-digit PIN authentication
- AI approval for system changes
- Full app access
- Daily automated backups
- Daily rollback safety net
- No direct system modifications

**Use case:** Family members who need full app access but simplified system management

### KIDS_TEMPORARY User
**Restricted with kiosk mode**

- 4-digit PIN (simplified)
- Kiosk mode (restricted apps only)
- No system changes allowed
- Hourly automated backups
- No terminal access
- No settings access

**Use case:** Children, temporary users, supervised access

## Installation

```bash
cd /home/LemonKaiju/projects/Linux\ testbed/ai_facilitator/profiles
./install_profiles.sh
```

Or with sudo for full installation:
```bash
sudo ./install_profiles.sh
```

## Usage

### Create a Profile

```bash
profile-cli create
```

Interactive prompts will guide you through:
1. Username
2. Profile type selection
3. Display name
4. Additional configuration (for kids profiles)

### List Profiles

```bash
profile-cli list
```

Shows all configured profiles with type and creation date.

### Show Profile Details

```bash
profile-cli show
```

Displays complete profile information including:
- Authentication settings
- Security features
- Permissions matrix
- Backup configuration

### Manage Kiosk Mode

```bash
profile-cli kiosk
```

For kids/temporary users:
- List allowed apps
- Add/remove allowed apps
- Disable kiosk mode

### Manage Backups

```bash
profile-cli backup
```

Backup operations:
- Show backup status
- Perform backup now
- List available backups
- Restore from backup
- Delete old backups

## Profile Features

### PRIMARY User Features

**Authentication:**
- 6-digit PIN for daily use
- Duress PIN for coercion protection
- Long password for recovery

**Security:**
- USB Sentinel dead man's switch
- Physical security monitoring
- Intrusion protection
- Full duress response

**System Access:**
- Install/uninstall Flatpaks
- Create/delete Distroboxes
- rpm-ostree operations
- System settings access
- Network configuration
- User management

**Automation:**
- Daily automated backups
- AI facilitator integration
- Security monitoring

### LESS_TECHNICAL User Features

**Authentication:**
- 6-digit PIN for daily use
- Long password for recovery

**Security:**
- Intrusion protection
- Failed attempt monitoring
- No duress PIN (simplified)

**System Access:**
- Install/uninstall Flatpaks (with AI approval)
- Full app access
- No direct system modifications
- No Distrobox access
- No system settings

**Automation:**
- Daily automated backups
- Daily rollback safety net
- AI approval workflow

**Safety Net:**
Automatic rollback if system issues detected on boot.

### KIDS_TEMPORARY User Features

**Authentication:**
- 4-digit PIN (simplified)
- Parent password for recovery

**Security:**
- Kiosk mode restrictions
- No system access
- Supervised environment

**System Access:**
- Approved apps only (Flatpak)
- No terminal
- No settings
- No system changes
- No AI facilitator

**Automation:**
- Hourly automated backups
- Automatic home directory protection

**Default Allowed Apps:**
- Firefox (web browsing)
- LibreOffice (documents)
- GNOME Games (entertainment)

## Permission Matrix

| Permission | PRIMARY | LESS_TECHNICAL | KIDS_TEMPORARY |
|------------|---------|----------------|----------------|
| Flatpak Install | ✓ | ✓ (AI approval) | ✗ |
| Flatpak Uninstall | ✓ | ✓ (AI approval) | ✗ |
| rpm-ostree Install | ✓ | ✗ | ✗ |
| rpm-ostree Rollback | ✓ | ✓ (AI approval) | ✗ |
| Distrobox Create | ✓ | ✗ | ✗ |
| Distrobox Delete | ✓ | ✗ | ✗ |
| System Settings | ✓ | ✗ | ✗ |
| Network Settings | ✓ | ✗ | ✗ |
| User Management | ✓ | ✗ | ✗ |
| Security Settings | ✓ | ✗ | ✗ |
| AI Facilitator | ✓ | ✓ | ✗ |

## Kiosk Mode

### How It Works

Kiosk mode creates a restricted desktop environment:
- Only approved apps visible in launcher
- No access to system settings
- No terminal access
- Simplified interface
- Session timeout (1 hour default)

### Configuration

Kiosk mode uses:
- GNOME Shell restrictions
- dconf profiles
- Custom desktop entries
- Application filtering

### Managing Allowed Apps

```bash
# Add an app
profile-cli kiosk
# Select: Add allowed app
# Enter Flatpak app ID

# Remove an app
profile-cli kiosk
# Select: Remove allowed app
# Enter Flatpak app ID
```

### Finding App IDs

```bash
# Search for apps
flatpak search <app name>

# List installed apps
flatpak list --app
```

## Backup Automation

### Backup Schedules

- **PRIMARY:** Daily backups, keep 7
- **LESS_TECHNICAL:** Daily backups, keep 7
- **KIDS_TEMPORARY:** Hourly backups, keep 24

### What Gets Backed Up

**Included:**
- Home directory
- User documents
- Application data
- Desktop settings

**Excluded:**
- Cache directories
- Trash
- Downloads
- Steam library
- Flatpak caches

### Manual Backup

```bash
profile-cli backup
# Select: Perform backup now
```

### Restore from Backup

```bash
profile-cli backup
# Select: Restore backup
# Choose backup to restore
```

**Warning:** Restore will overwrite current files.

## AI Approval Workflow

For LESS_TECHNICAL users, system changes require AI approval:

1. User requests system change
2. AI Facilitator intercepts request
3. Notification sent to user
4. User approves/rejects via notification
5. Action executed if approved

**Example:**
```
User: "Install Steam"
  ↓
AI: "Allow installation of Steam? [Yes] [No]"
  ↓
User: [Yes]
  ↓
AI: Installs Steam via Flatpak
```

## Auto-Rollback Safety Net

For LESS_TECHNICAL users, daily health check:

1. Check system health on boot
2. If issues detected:
   - Automatic rpm-ostree rollback
   - Reboot to previous deployment
   - User notified of rollback

**Prevents:**
- Broken system states
- Failed updates
- Configuration errors

## Integration with Other Systems

### PIN Authentication

```python
from ai_facilitator.profiles import ProfileManager

# Get PIN length for user
profile_manager = ProfileManager()
profile = profile_manager.get_profile(username)
pin_length = profile.get('pin_length', 6)
```

### AI Facilitator

```python
# Check if AI approval required
if profile_manager.check_permission(username, 'flatpak_install'):
    if profile.get('ai_approval_required'):
        # Request approval
        pass
```

### Security Systems

```python
# Check if duress PIN enabled
if profile.get('duress_pin_enabled'):
    # Configure duress protection
    pass
```

## Configuration Files

```
~/.local/share/profiles/
├── profiles.json               # Profile definitions

~/.local/share/kiosk/
├── username_kiosk.json         # Kiosk configuration

~/.local/share/backups/
├── username/
│   ├── username_20260314_150000.tar.gz
│   └── username_20260313_150000.tar.gz

~/.local/share/backup_config/
└── username_backup.json        # Backup configuration
```

## Examples

### Create Primary User Profile

```bash
profile-cli create
# Username: alice
# Profile type: 1 (Primary)
# Display name: Alice (Admin)
```

### Create Kids Profile

```bash
profile-cli create
# Username: timmy
# Profile type: 3 (Kids/Temporary)
# Display name: Timmy
# Customize apps: y
# App IDs:
#   org.mozilla.firefox
#   org.gnome.Games
#   org.tuxpaint.Tuxpaint
```

### Add App to Kiosk

```bash
profile-cli kiosk
# Username: timmy
# Action: 2 (Add allowed app)
# App ID: org.kde.gcompris
```

### Perform Manual Backup

```bash
profile-cli backup
# Username: alice
# Action: 2 (Perform backup now)
```

## Troubleshooting

### Kiosk mode not working

```bash
# Check kiosk configuration
profile-cli show
# Username: <user>

# Verify dconf profile
cat /etc/dconf/profile/<user>
```

### Backups failing

```bash
# Check backup status
profile-cli backup
# Username: <user>
# Action: 1 (Show status)

# Check disk space
df -h ~/.local/share/backups
```

### Permission denied errors

```bash
# Verify profile permissions
profile-cli show
# Username: <user>

# Check if AI approval required
# Look for "AI approval required: Yes"
```

## Security Considerations

### Profile Separation

- Each profile has isolated configuration
- Permissions enforced at system level
- No privilege escalation between profiles

### Backup Security

- Backups stored with user permissions
- No encryption by default (home directory encryption recommended)
- Rotation prevents disk filling

### Kiosk Security

- GNOME Shell restrictions
- No terminal access
- No settings access
- Session timeout

## Best Practices

1. **Use appropriate profiles** - Don't give kids PRIMARY access
2. **Regular backups** - Verify backups work before needed
3. **Test kiosk mode** - Ensure allowed apps are sufficient
4. **Monitor AI approvals** - Review what LESS_TECHNICAL users request
5. **Update allowed apps** - Add educational/appropriate apps as needed

## Next Steps - Milestone 5

- Integrate with Shut The Front Door installer
- Network security coordination
- Unified logging across systems
- Cross-system profile management

## License

MIT License - Part of the LemonKaijuOS project
