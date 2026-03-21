# STFD Integration

**Integration between AI Facilitator and Shut The Front Door network maintenance system**

Bridges local security systems (AI Facilitator) with network-level security (STFD) for comprehensive protection.

## Features

### Security Bridge
- Expose AI Facilitator security status to STFD
- Coordinate security events across systems
- Unified security logging
- Cross-system alerts

### Unified Dashboard
- Single pane of glass for all security systems
- Real-time status monitoring
- Alert aggregation
- HTML dashboard generation

### Network Coordinator
- Coordinate local and network security responses
- Trigger network-level protections on local threats
- Monitor network security status
- Unified security policy enforcement

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    STFD Integration                          │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Security Bridge                         │   │
│  │  • Status Exposure                                   │   │
│  │  • Event Coordination                                │   │
│  │  • Unified Logging                                   │   │
│  └──────────────────────────────────────────────────────┘   │
│                            │                                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │           Unified Dashboard                          │   │
│  │  • Single View                                       │   │
│  │  • Real-time Monitoring                              │   │
│  │  • HTML Generation                                   │   │
│  └──────────────────────────────────────────────────────┘   │
│                            │                                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │          Network Coordinator                         │   │
│  │  • Threat Response                                   │   │
│  │  • Network Lockdown                                  │   │
│  │  • Policy Sync                                       │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Installation

```bash
cd /home/LemonKaiju/projects/Linux\ testbed/ai_facilitator/stfd_integration
./install_stfd_integration.sh
```

Or with sudo for full installation:
```bash
sudo ./install_stfd_integration.sh
```

## Usage

### View Unified Dashboard

```bash
stfd-cli dashboard
```

Shows terminal-based dashboard with:
- Local security systems status
- Network security status
- System health metrics
- Recent alerts
- Recent activity

### Generate HTML Dashboard

```bash
stfd-cli html
```

Creates interactive HTML dashboard at:
`~/.local/share/unified_dashboard/dashboard.html`

**Features:**
- Auto-refreshes every 30 seconds
- Color-coded status indicators
- Real-time metrics
- Alert history

### Check Security Status

```bash
stfd-cli security
```

Shows detailed status of all AI Facilitator systems:
- PIN Authentication
- Duress Protection
- Intrusion Protection
- Physical Security
- User Profiles

### Check Network Status

```bash
stfd-cli network
```

Shows STFD network security status:
- WireGuard VPN
- OPNsense Firewall
- AdGuard DNS
- Network lockdown status
- Connectivity health

### View Unified Logs

```bash
stfd-cli logs
```

Shows combined logs from:
- AI Facilitator (local actions)
- STFD installer (network actions)

### Register with STFD

```bash
stfd-cli register
```

Registers AI Facilitator with STFD installer for integration.

### Clear Network Lockdown

```bash
stfd-cli lockdown-clear
```

Clears active network lockdown (requires authorization).

### Sync Security Policies

```bash
stfd-cli sync-policies
```

Synchronizes security policies between local and network systems.

## Integration Points

### Security Event Coordination

When a security event occurs locally (duress, intrusion, physical threat), the integration:

1. **Local Response** (AI Facilitator)
   - Unmount containers
   - Lock system
   - Log event

2. **Network Response** (STFD Coordination)
   - Send encrypted alert
   - Trigger network lockdown (if critical)
   - Update STFD logs

3. **Unified Logging**
   - Event logged in both systems
   - Accessible via unified dashboard

### Example: Duress Code Activation

```
User enters duress PIN
    ↓
AI Facilitator detects duress
    ↓
Security Bridge coordinates response
    ↓
Local: Containers unmounted, Houdini executed
    ↓
Network: Alert sent, Lockdown triggered (if critical)
    ↓
Dashboard: Alert displayed, Logs updated
```

### Example: Failed Login Attempts

```
5 failed login attempts
    ↓
Intrusion Protection triggers
    ↓
Security Bridge coordinates response
    ↓
Local: System shutdown initiated
    ↓
Network: External access blocked
    ↓
Dashboard: Intrusion alert displayed
```

## Configuration Files

```
~/.local/share/stfd_bridge/
├── security_state.json         # Current security status
├── security_alerts.json        # Security alerts
└── integration_config.json     # Integration configuration

~/.local/share/unified_dashboard/
└── dashboard.html              # HTML dashboard

~/.local/share/network_coordinator/
├── network_lockdown.json       # Active lockdown state
├── lockdown_history.json       # Lockdown history
├── synced_policies.json        # Synced security policies
└── coordination_log.json       # Coordination events
```

## Dashboard Features

### Terminal Dashboard

**Local Security:**
- 🔐 PIN Authentication
- 🛡️ Duress Protection
- 🛡️ Intrusion Protection
- 🔑 Physical Security
- 👥 User Profiles

**Network Security:**
- WireGuard VPN status
- OPNsense Firewall status
- AdGuard DNS status

**System Health:**
- CPU usage
- Memory usage
- Disk usage

**Recent Alerts:**
- Last 5 security alerts
- Severity indicators
- Timestamps

### HTML Dashboard

**Features:**
- Modern dark theme
- Color-coded status indicators
- Real-time metrics
- Auto-refresh (30 seconds)
- Responsive design

**Status Colors:**
- 🟢 Green: Active/Healthy
- 🟡 Yellow: Warning
- 🔴 Red: Alert/Critical
- ⚪ Gray: Inactive/Unavailable

## Network Lockdown

### What Triggers Lockdown

Lockdown is triggered on **high** or **critical** severity threats:
- Duress code activation
- Multiple intrusion attempts
- Physical security breach

### Lockdown Actions

1. **Flag Set:** Lockdown state file created
2. **Network Actions:** (In production)
   - Disable WireGuard VPN
   - Enable strict firewall rules
   - Block external access
3. **Alerts:** Notifications sent to administrators

### Clearing Lockdown

```bash
stfd-cli lockdown-clear
# Enter username for authorization
# Confirm clearance
```

**Requirements:**
- Valid username
- Confirmation
- Logged for audit

## Security Policy Sync

### What Gets Synced

**Local Policies:**
- User profile types
- Permission matrices
- Security settings

**Network Policies:**
- Access rules
- Firewall configurations
- VPN settings

### Sync Process

```bash
stfd-cli sync-policies
```

1. Collect local policies from profiles
2. Read network policies from STFD
3. Create unified policy document
4. Save to synced_policies.json

## Integration with STFD Modules

### WireGuard (The Front Door)
- Monitor VPN status
- Coordinate VPN lockdown
- Alert on VPN failures

### OPNsense (The Gatekeeper)
- Monitor firewall status
- Coordinate firewall rules
- Alert on intrusions

### AdGuard (The Filter)
- Monitor DNS filtering
- Coordinate DNS blocks
- Alert on threats

## Troubleshooting

### Dashboard not showing data

```bash
# Check security status
stfd-cli security

# Verify STFD path
ls ~/projects/Linux\ testbed/shut-the-front-door/installer/

# Re-register
stfd-cli register
```

### Network status unavailable

```bash
# Check STFD configuration
cat ~/projects/Linux\ testbed/shut-the-front-door/installer/install_config.json

# Verify network connectivity
ping 8.8.8.8
```

### Logs not appearing

```bash
# Check AI Facilitator logs
ls ~/.local/share/ai_facilitator/logs/

# Check STFD logs
ls ~/projects/Linux\ testbed/shut-the-front-door/installer/install_log.json

# Check bridge directory
ls ~/.local/share/stfd_bridge/
```

## API Integration

### Python API

```python
from ai_facilitator.stfd_integration import SecurityBridge, UnifiedDashboard

# Get security status
bridge = SecurityBridge()
status = bridge.get_security_status()

# Send alert
bridge.send_security_alert(
    "intrusion",
    "critical",
    "Failed login attempts exceeded",
    {"username": "user", "attempts": 5}
)

# Generate dashboard
dashboard = UnifiedDashboard()
html = dashboard.generate_dashboard_html()
```

### STFD Integration

STFD installer can read integration data from:
- `~/.local/share/stfd_bridge/security_state.json`
- `~/.local/share/stfd_bridge/security_alerts.json`
- `~/.local/share/stfd_bridge/integration_config.json`

## Best Practices

1. **Regular Monitoring:** Check dashboard daily
2. **Alert Review:** Investigate all critical alerts
3. **Policy Sync:** Sync policies after profile changes
4. **Lockdown Testing:** Test lockdown in safe environment
5. **Log Review:** Review unified logs weekly

## Security Considerations

### Data Sharing

- Security state shared via local files
- No network transmission of sensitive data
- File permissions: 600 (owner only)

### Alert Privacy

- Alerts stored locally
- Encrypted transmission (if network alerts enabled)
- Automatic rotation (last 100 alerts)

### Lockdown Safety

- Non-destructive actions
- Reversible with authorization
- Logged for audit
- Requires confirmation

## Next Steps - Milestone 6

- Comprehensive testing
- Security validation
- Performance optimization
- Production deployment
- User training materials

## License

MIT License - Part of the LemonKaijuOS project
