# PIN Authentication System

**6-digit PIN authentication for LemonKaijuOS**

Replace password prompts with a simple 6-digit PIN for daily tasks while keeping your long privacy password secure.

## Features

- **6-digit PIN** for sudo and login
- **Separate from password** - Long password remains hidden
- **Failed attempt limiting** - 5 attempts before lockout
- **Recovery options** - Reset with password or recovery code
- **Family-safe** - Non-destructive lockout (system shutdown)
- **Audit trail** - All PIN changes logged

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  PIN Authentication System                   │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ PIN Manager  │  │ PAM Config   │  │  Recovery    │      │
│  │              │  │              │  │   Manager    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         │                  │                  │              │
│         └──────────────────┴──────────────────┘              │
│                            │                                 │
├────────────────────────────┼─────────────────────────────────┤
│                            │                                 │
│  ┌─────────────┬───────────▼───────────┬─────────────┐      │
│  │  /etc/pam.d │   /etc/pinlock        │  faillock   │      │
│  │  (sudo/gdm) │   (PIN database)      │  (attempts) │      │
│  └─────────────┴───────────────────────┴─────────────┘      │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Installation

### Prerequisites

- LemonKaijuOS (Bazzite-based)
- Python 3.10+
- Root access for PAM configuration

### Quick Install

```bash
cd /home/LemonKaiju/projects/Linux\ testbed/ai_facilitator/pin_auth
sudo ./install_pin_auth.sh
```

### Manual Installation

```bash
# Create PIN database directory
sudo mkdir -p /etc/pinlock
sudo chmod 755 /etc/pinlock

# Install CLI tool
sudo ln -s $(pwd)/cli.py /usr/local/bin/pin-auth
sudo chmod +x /usr/local/bin/pin-auth

# Configure PAM
sudo pin-auth configure
```

## Usage

### Create a PIN

```bash
pin-auth create
```

You'll be prompted for:
- Username
- 6-digit PIN
- PIN verification

### Change PIN

```bash
pin-auth change
```

Requires:
- Current PIN
- New 6-digit PIN
- New PIN verification

### Reset PIN (Forgot PIN)

```bash
pin-auth reset
```

Requires:
- Long privacy password
- New 6-digit PIN

### Generate Recovery Code

```bash
pin-auth recovery
```

Generates a one-time recovery code (format: XXXX-XXXX-XXXX-XXXX)

**Important:** Store this code securely. It can be used once to reset your PIN.

### Unlock After Failed Attempts

```bash
pin-auth unlock
```

If you exceed the maximum failed attempts (5), your account will be locked.
Use this command with your long password to unlock.

### Check Status

```bash
pin-auth status
```

Shows:
- System configuration status
- User PIN status
- Faillock status
- Recent PIN changes

## Security Features

### PIN Validation

PINs must:
- Be exactly 6 digits
- Not be all the same digit (e.g., 111111)
- Not be sequential (e.g., 123456)
- Not be common PINs (e.g., 000000, 123123)

### Failed Attempt Protection

- **Maximum attempts:** 5
- **Lockout action:** System shutdown (family-safe)
- **Unlock method:** Long password required
- **Reset counter:** Automatic after successful login

### Storage Security

- PINs hashed with SHA-512 via crypt(3)
- PIN database at `/etc/pinlock` (mode 600)
- Separate from system password database
- All changes logged with timestamps

### Recovery Options

1. **Long Password:** Reset PIN anytime with your privacy password
2. **Recovery Code:** One-time code for emergency reset
3. **Emergency Disable:** Remove PIN, fall back to password-only

## PAM Configuration

The system modifies two PAM files:

### /etc/pam.d/sudo

```
auth       required   pam_faillock.so preauth
auth       sufficient pam_unix.so try_first_pass nullok_secure pinfile=/etc/pinlock
auth       required   pam_unix.so
auth       required   pam_faillock.so authfail
account    required   pam_unix.so
account    required   pam_faillock.so
```

### /etc/pam.d/gdm-password

```
auth       required   pam_faillock.so preauth silent
auth       sufficient pam_unix.so try_first_pass nullok_secure pinfile=/etc/pinlock
auth       required   pam_unix.so
auth       required   pam_faillock.so authfail
account    required   pam_unix.so
account    required   pam_faillock.so
```

**Backups:** Original files backed up to `~/.local/share/pin_auth/pam_backups/`

## Integration with AI Facilitator

The PIN system integrates with the AI Facilitator for automated PIN management:

```python
from ai_facilitator.pin_auth import PINManager

pin_manager = PINManager()

# AI can help create PINs
result = pin_manager.create_pin("username", "123456", "123456")

# AI can check PIN status
has_pin = pin_manager.has_pin("username")

# AI can assist with recovery
from ai_facilitator.pin_auth import RecoveryManager
recovery = RecoveryManager()
recovery.generate_recovery_code("username")
```

## Duress Protection Integration

The PIN system is designed to work with duress codes (Milestone 3):

- **Normal PIN:** Regular authentication
- **Duress PIN:** Silent alert + container unmount
- **Failed attempts:** System shutdown (theft protection)

## Family Profiles

### Profile A: Kids/Temporary (4-digit PIN)
- Simplified PIN (4 digits instead of 6)
- Restricted to approved applications
- Automatic backups

### Profile B: Less Technical (6-digit PIN)
- Full 6-digit PIN
- AI approval required for system changes
- Daily rollback safety net

## Troubleshooting

### PIN not working for sudo

```bash
# Check PAM configuration
sudo pin-auth status

# Verify PIN database
ls -la /etc/pinlock/

# Check faillock status
faillock --user $USER
```

### Account locked after failed attempts

```bash
# Unlock with long password
pin-auth unlock

# Or reset faillock manually
sudo faillock --user $USER --reset
```

### Forgot PIN

```bash
# Reset with long password
pin-auth reset

# Or use recovery code
pin-auth reset --recovery-code XXXX-XXXX-XXXX-XXXX
```

### Emergency: Disable PIN authentication

```bash
# Remove PIN file
sudo rm /etc/pinlock/$USER

# Restore original PAM config
sudo cp ~/.local/share/pin_auth/pam_backups/sudo.* /etc/pam.d/sudo
sudo cp ~/.local/share/pin_auth/pam_backups/gdm-password.* /etc/pam.d/gdm-password
```

## Files and Directories

```
/etc/pinlock/                           # PIN database
  └── username                          # User PIN hash

/etc/pam.d/
  ├── sudo                              # sudo PAM config
  └── gdm-password                      # GDM PAM config

/etc/security/faillock.conf             # Faillock configuration

~/.local/share/pin_auth/
  ├── pam_backups/                      # PAM config backups
  ├── recovery/                         # Recovery codes
  └── pin_history.json                  # PIN change history
```

## Testing

```bash
# Test PIN creation
pin-auth create

# Test sudo with PIN
sudo -v

# Test PIN change
pin-auth change

# Test recovery code
pin-auth recovery

# Test status check
pin-auth status
```

## Security Considerations

### What PIN Protects

- ✓ Daily sudo operations
- ✓ System login (GDM)
- ✓ Quick authentication tasks

### What PIN Doesn't Protect

- ✗ Disk encryption (uses long password)
- ✗ SSH keys (separate authentication)
- ✗ GPG keys (separate passphrase)

### Best Practices

1. **Use a unique PIN** - Don't reuse PINs from other devices
2. **Generate recovery code** - Store it securely offline
3. **Remember your long password** - Required for PIN reset
4. **Don't share your PIN** - Even with family members
5. **Change PIN regularly** - Every 3-6 months

## Next Steps - Milestone 3

- Duress PIN implementation
- Physical theft protection
- Dead man's switch (USB sentinel)
- Intrusion detection

## License

MIT License - Part of the LemonKaijuOS project
