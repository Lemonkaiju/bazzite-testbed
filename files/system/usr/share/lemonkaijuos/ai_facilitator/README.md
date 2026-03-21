# AI Facilitator Framework

**Safety-First AI Command Server for LemonKaijuOS**

The AI Facilitator is a secure command execution system that allows AI assistants to help manage your Bazzite-based atomic Linux system while maintaining strict safety controls.

## Core Principles

1. **User-Present Flag**: AI only operates when you're physically present (USB key or mobile dashboard)
2. **No Sudo Access**: Uses PolicyKit delegation for specific, safe commands only
3. **Declarative Authorization**: Every action requires your explicit approval
4. **No Raw Scripts**: Only pre-defined, safe command wrappers
5. **Full Audit Trail**: Every action is logged and reversible

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AI Facilitator Server                     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ User-Present │  │Authorization │  │ Transaction  │      │
│  │  Detector    │  │   Manager    │  │   Logger     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         │                  │                  │              │
│         └──────────────────┴──────────────────┘              │
│                            │                                 │
│                   ┌────────▼────────┐                        │
│                   │   MCP Tools     │                        │
│                   │    Wrapper      │                        │
│                   └────────┬────────┘                        │
│                            │                                 │
├────────────────────────────┼─────────────────────────────────┤
│                            │                                 │
│  ┌─────────────┬───────────┴───────────┬─────────────┐      │
│  │  Flatpak    │   rpm-ostree          │  Distrobox  │      │
│  │  Install    │   Rollback            │  Create     │      │
│  └─────────────┴───────────────────────┴─────────────┘      │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Components

### 1. User-Present Detector (`user_present.py`)
- Monitors USB sentinel key
- Checks mobile dashboard flag
- Disables AI when user not present

### 2. Authorization Manager (`authorization.py`)
- Desktop notifications with Yes/No
- Mobile dashboard approval
- CLI fallback
- 5-minute approval timeout

### 3. MCP Tool Wrapper (`mcp_tools.py`)
Safe command wrappers for:
- `flatpak install [App]`
- `rpm-ostree rollback`
- `distrobox create -n [Env]`
- `ujust setup-gaming`

### 4. Transaction Logger (`transaction_log.py`)
- Logs all actions
- Undo functionality
- Human-readable history
- Export capabilities

## Installation

### 1. Install Dependencies

```bash
# Using Homebrew (preferred for Bazzite)
brew install python@3.10

# Install Python packages
cd /home/LemonKaiju/projects/Linux\ testbed/ai_facilitator
pip install -r requirements.txt
```

### 2. Install PolicyKit Rules

```bash
# Copy PolicyKit rules
sudo mkdir -p /etc/polkit-1/rules.d/

# Create Flatpak rule
sudo tee /etc/polkit-1/rules.d/50-ai-facilitator-flatpak.rules << 'EOF'
polkit.addRule(function(action, subject) {
    if (action.id == "org.freedesktop.Flatpak.app-install" ||
        action.id == "org.freedesktop.Flatpak.app-uninstall" ||
        action.id == "org.freedesktop.Flatpak.runtime-install" ||
        action.id == "org.freedesktop.Flatpak.runtime-uninstall") {
        if (subject.isInGroup("wheel")) {
            return polkit.Result.YES;
        }
    }
});
EOF

# Create rpm-ostree rule
sudo tee /etc/polkit-1/rules.d/50-ai-facilitator-rpm-ostree.rules << 'EOF'
polkit.addRule(function(action, subject) {
    if (action.id == "org.projectatomic.rpmostree1.rollback") {
        if (subject.isInGroup("wheel")) {
            return polkit.Result.YES;
        }
    }
});
EOF

# Reload PolicyKit
sudo systemctl restart polkit
```

### 3. Configure USB Sentinel (Optional)

```bash
# Find your USB device
lsusb

# Note the vendor:product ID (e.g., 1234:5678)
# Update config at ~/.config/ai_facilitator/config.json
```

### 4. Start the Server

```bash
python -m ai_facilitator.server
```

## Usage

### Basic Command Execution

```python
from ai_facilitator import AIFacilitatorServer

server = AIFacilitatorServer()
server.start()

# Install a Flatpak
result = server.execute_command("flatpak_install", {
    "app_name": "org.mozilla.firefox"
})

print(result)
# User will receive approval notification
# After approval, installation proceeds
```

### Check Status

```python
status = server.get_status()
print(f"User present: {status['user_present']}")
print(f"Pending commands: {status['pending_commands']}")
```

### View History

```python
history = server.get_history(limit=10)
for transaction in history:
    print(f"{transaction['timestamp']}: {transaction['command']} - {transaction['status']}")
```

### Undo Last Action

```python
result = server.undo_last_action()
print(result)
```

## Configuration

Configuration file: `~/.config/ai_facilitator/config.json`

```json
{
  "user_present": {
    "usb_sentinel_enabled": true,
    "sentinel_vendor_id": "1234",
    "sentinel_product_id": "5678",
    "sentinel_label": "AI_SENTINEL",
    "mobile_dashboard_enabled": false,
    "check_interval": 5
  },
  "authorization": {
    "require_approval": true,
    "approval_timeout": 300,
    "notification_method": "desktop"
  },
  "mcp_tools": {
    "allowed_commands": [
      "flatpak install",
      "rpm-ostree rollback",
      "distrobox create",
      "ujust setup-gaming"
    ]
  },
  "transaction_log": {
    "log_dir": "~/.local/share/ai_facilitator/logs",
    "max_history": 1000
  }
}
```

## Security Features

### Kill Switch
- AI disabled when USB sentinel removed
- Instant shutdown of all pending operations
- No commands execute without user presence

### Scoped Permissions
- No sudo access required
- PolicyKit handles specific permissions
- Cannot execute arbitrary commands
- Cannot modify system files directly

### Audit Trail
- Every command logged with timestamp
- User approval decisions recorded
- Full undo history maintained
- Export logs for review

## Integration with Shut The Front Door

The AI Facilitator integrates with the Shut The Front Door installer:

```python
# In STFD installer
from ai_facilitator import AIFacilitatorServer

# Use AI to help with network setup
ai = AIFacilitatorServer()
result = ai.execute_command("distrobox_create", {
    "name": "network-tools",
    "distro": "ubuntu:24.04"
})
```

## Troubleshooting

### AI Not Responding
1. Check user-present status: `python -c "from ai_facilitator.user_present import UserPresentDetector; d = UserPresentDetector({}); print(d._check_presence())"`
2. Verify USB sentinel is connected
3. Check logs: `~/.local/share/ai_facilitator/logs/`

### Approval Notifications Not Showing
1. Install zenity: `flatpak install org.gnome.Zenity`
2. Check notification daemon is running
3. Try CLI approval method

### PolicyKit Errors
1. Verify rules installed: `ls /etc/polkit-1/rules.d/`
2. Check user in wheel group: `groups`
3. Restart PolicyKit: `sudo systemctl restart polkit`

## Development

### Running Tests
```bash
pytest tests/
```

### Adding New Commands
1. Add command to `mcp_tools.py`
2. Add undo handler to `transaction_log.py`
3. Update `allowed_commands` in config
4. Add PolicyKit rule if needed

## License

MIT License - Part of the LemonKaijuOS project

## Next Steps

- [ ] Milestone 2: Implement 6-digit PIN authentication
- [ ] Milestone 3: Add duress and intrusion protection
- [ ] Milestone 4: Create security profiles
- [ ] Milestone 5: Integrate with Shut The Front Door
- [ ] Milestone 6: Testing and deployment
