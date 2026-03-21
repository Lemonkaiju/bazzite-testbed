# Security Protection Systems

**Duress codes, intrusion protection, and physical security for LemonKaijuOS**

Comprehensive security mechanisms to protect against coercion, unauthorized access, and physical theft.

## Features

### Duress Protection
- **Duress PIN** - Silent protective measures when coerced
- **Silent alerts** - Encrypted notifications to other devices
- **Container unmounting** - Instant protection of sensitive data
- **Houdini mode** - Fake authentication failure

### Intrusion Protection
- **Failed attempt monitoring** - Automatic response to unauthorized access
- **Family-safe lockout** - System shutdown (non-destructive)
- **Long password requirement** - Forces full password after lockout
- **Auto-rollback** - Atomic OS rollback on tamper detection

### Physical Security
- **USB Sentinel** - Dead man's switch
- **Instant lockdown** - Immediate response to USB removal
- **Cold boot protection** - Optional RAM wipe
- **Tamper detection** - Physical security monitoring

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              Security Protection Systems                     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Duress     │  │  Intrusion   │  │  Physical    │      │
│  │   Manager    │  │  Protection  │  │  Security    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         │                  │                  │              │
│         └──────────────────┴──────────────────┘              │
│                            │                                 │
├────────────────────────────┼─────────────────────────────────┤
│                            │                                 │
│  ┌─────────────┬───────────▼───────────┬─────────────┐      │
│  │ Silent      │  System Shutdown      │  USB        │      │
│  │ Alerts      │  Container Unmount    │  Sentinel   │      │
│  └─────────────┴───────────────────────┴─────────────┘      │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Installation

```bash
cd /home/LemonKaiju/projects/Linux\ testbed/ai_facilitator/security
./install_security.sh
```

Or with sudo for full installation:
```bash
sudo ./install_security.sh
```

## Usage

### Create Duress PIN

```bash
security-cli duress
```

Creates a separate PIN that triggers protective measures when entered under coercion.

**What happens when duress PIN is used:**
1. Silent encrypted alert sent to your other devices
2. All sensitive containers unmounted immediately
3. "Houdini" - appears to fail authentication
4. No visible indication to the attacker

### Configure USB Sentinel

```bash
security-cli sentinel
```

Set up a USB device as a physical "dead man's switch".

**What happens when USB is removed:**
1. System locks immediately
2. All containers unmounted
3. Optional RAM wipe (cold boot protection)
4. Security event logged

### Check Security Status

```bash
security-cli status
```

Shows:
- Duress PIN configuration
- Intrusion protection status
- Physical security status
- Recent security events

### View Security Logs

```bash
security-cli logs
```

View logs for:
- Duress activations
- Intrusion attempts
- Physical security events

### Start Monitoring

```bash
security-cli monitor
```

Starts continuous monitoring of:
- USB sentinel presence
- Failed login attempts
- Physical tamper detection

## Duress Protection Details

### How It Works

1. **Normal PIN**: Regular authentication
2. **Duress PIN**: Triggers protective measures

Both PINs work for authentication, but the duress PIN silently activates security responses.

### Silent Alert System

When duress PIN is entered:
- Encrypted message sent to configured devices
- Alert includes timestamp and location
- No visible indication on the device
- Attacker sees normal authentication flow

### Container Protection

Sensitive Distrobox containers are:
- Stopped immediately
- Data remains intact (family-safe)
- Can be restarted after threat passes

### Houdini Mode

Two options:
1. **Fake failure** - Shows "Authentication failed" message
2. **Power off** - Immediate system shutdown

Configurable per user preference.

## Intrusion Protection Details

### Failed Attempt Response

**Threshold:** 5 failed attempts (configurable)

**Response:**
1. Unmount all containers
2. Set long password requirement flag
3. System shutdown (family-safe)
4. Log intrusion attempt

**Why shutdown?**
- Forces physical restart
- Prevents remote brute force
- Family-safe (no data loss)
- Requires physical presence to continue

### Long Password Requirement

After lockout:
- PIN authentication disabled
- Must use full privacy password
- Resets after successful password login
- Prevents continued PIN guessing

### Auto-Rollback

On physical tamper detection:
- Automatic rpm-ostree rollback
- Returns to last known-good state
- Atomic OS feature
- Prevents persistent compromise

## Physical Security Details

### USB Sentinel Configuration

**Method 1: Vendor/Product ID**
```bash
# Find your USB device
lsusb

# Note the ID (e.g., 1234:5678)
# Configure via security-cli sentinel
```

**Method 2: Volume Label**
```bash
# Label your USB device
# Configure via security-cli sentinel
```

### Dead Man's Switch

Continuous monitoring (2-second intervals):
- Checks USB sentinel presence
- Triggers on removal
- Instant response (< 1 second)

### Cold Boot Protection

Optional RAM wipe on USB removal:
- Prevents cold boot attacks
- **WARNING:** Crashes system
- Only enable if you understand risks
- Disabled by default

## Integration with Other Systems

### PIN Authentication Integration

```python
from ai_facilitator.security import DuressManager
from ai_facilitator.pin_auth import PINManager

# Check if PIN is duress code
duress = DuressManager()
result = duress.check_duress(username, pin)

if result['is_duress']:
    # Trigger duress response
    duress.trigger_duress_response(username, result['duress_data'])
```

### AI Facilitator Integration

```python
from ai_facilitator.security import IntrusionProtection

# Monitor failed attempts
intrusion = IntrusionProtection()
status = intrusion.monitor_failed_attempts(username)

if status.get('response_triggered'):
    # Intrusion response activated
    pass
```

### User-Present Detection Integration

Physical security already integrates with the AI Facilitator's user-present detection:
- Same USB sentinel can serve both purposes
- Unified monitoring
- Coordinated responses

## Security Profiles

### Profile A: Kids/Temporary Users

- No duress PIN (simplified)
- Intrusion protection active
- No physical security (supervised use)

### Profile B: Less Technical Users

- Duress PIN available
- Full intrusion protection
- Optional USB sentinel

### Primary User

- Full duress protection
- All intrusion features
- Physical security enabled
- Multiple alert devices

## Configuration Files

```
~/.local/share/security/
├── duress/
│   ├── username.json           # Duress PIN configuration
│   ├── alerts/                 # Queued alerts
│   └── activations.log         # Activation history
│
├── intrusion/
│   ├── intrusion_log.json      # Intrusion attempts
│   └── username_long_password_required  # Lockout flags
│
└── physical/
    ├── sentinel_config.json    # USB sentinel config
    └── security_events.json    # Physical security events
```

## Testing

### Test Duress PIN

1. Create duress PIN
2. Enter duress PIN at login/sudo
3. Verify silent alert sent
4. Verify containers unmounted
5. Verify Houdini executed

### Test Intrusion Protection

1. Attempt 5+ failed logins
2. Verify system shutdown
3. Verify long password required
4. Verify containers unmounted

### Test USB Sentinel

1. Configure sentinel
2. Start monitoring
3. Remove USB device
4. Verify immediate lock
5. Verify containers unmounted

## Troubleshooting

### Duress PIN not triggering

```bash
# Check duress configuration
security-cli status

# Verify duress PIN exists
ls ~/.local/share/security/duress/
```

### USB Sentinel not detected

```bash
# Check USB device
lsusb

# Verify configuration
cat ~/.local/share/security/physical/sentinel_config.json

# Test detection
security-cli status
```

### Intrusion protection not activating

```bash
# Check faillock status
faillock --user $USER

# View intrusion logs
security-cli logs
```

## Security Considerations

### What This Protects Against

- ✓ Coercion (duress PIN)
- ✓ Brute force attacks (intrusion protection)
- ✓ Physical theft (USB sentinel)
- ✓ Cold boot attacks (optional RAM wipe)
- ✓ Unauthorized physical access

### What This Doesn't Protect Against

- ✗ Sophisticated attackers who know about duress codes
- ✗ Remote attacks before physical security activates
- ✗ Attacks while system is powered off
- ✗ Disk encryption bypass (separate protection)

### Best Practices

1. **Keep duress PIN secret** - Don't tell anyone
2. **Test regularly** - Verify systems work
3. **Multiple alert devices** - Redundancy
4. **Physical security** - Lock your devices
5. **Regular updates** - Keep system current

## Family Safety

All protection mechanisms are **non-destructive**:
- No data deletion
- No permanent changes
- Reversible actions
- System shutdown (not wipe)

This ensures family members aren't locked out permanently if they forget their PIN.

## Emergency Procedures

### Disable Duress Protection

```bash
# Remove duress PIN
rm ~/.local/share/security/duress/$USER.json
```

### Disable Physical Security

```bash
# Stop monitoring
systemctl --user stop security-monitor

# Remove configuration
rm ~/.local/share/security/physical/sentinel_config.json
```

### Reset After Intrusion

```bash
# Clear long password requirement
rm ~/.local/share/security/intrusion/${USER}_long_password_required

# Reset faillock
sudo faillock --user $USER --reset
```

## Next Steps - Milestone 4

- Security profile implementation
- Automated profile switching
- Profile-specific restrictions
- Backup automation per profile

## License

MIT License - Part of the LemonKaijuOS project
