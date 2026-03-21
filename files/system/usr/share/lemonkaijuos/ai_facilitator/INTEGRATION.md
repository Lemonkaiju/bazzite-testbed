# AI Facilitator Integration Guide

## Integration with Shut The Front Door

The AI Facilitator can be integrated with the Shut The Front Door installer to provide AI-assisted network setup and maintenance.

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│           Shut The Front Door Installer                      │
│                  (Flask Web App)                             │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────┐         ┌──────────────────┐          │
│  │  Installer UI    │◄────────┤  AI Facilitator  │          │
│  │  (Browser)       │         │     Server       │          │
│  └──────────────────┘         └──────────────────┘          │
│                                        │                     │
│                                        ▼                     │
│                          ┌──────────────────────┐           │
│                          │  System Commands     │           │
│                          │  (Flatpak, etc.)     │           │
│                          └──────────────────────┘           │
└─────────────────────────────────────────────────────────────┘
```

### Integration Steps

#### 1. Import AI Facilitator in STFD Server

Edit `/home/LemonKaiju/projects/Linux testbed/shut-the-front-door/installer/server.py`:

```python
from ai_facilitator import AIFacilitatorServer

# Initialize AI Facilitator
ai_facilitator = AIFacilitatorServer()
ai_facilitator.start()

# Add API endpoint for AI commands
@app.route('/api/ai/execute', methods=['POST'])
def ai_execute():
    data = request.json
    command = data.get('command')
    args = data.get('args', {})
    
    result = ai_facilitator.execute_command(command, args)
    return jsonify(result)

@app.route('/api/ai/status', methods=['GET'])
def ai_status():
    status = ai_facilitator.get_status()
    return jsonify(status)

@app.route('/api/ai/history', methods=['GET'])
def ai_history():
    limit = request.args.get('limit', 50, type=int)
    history = ai_facilitator.get_history(limit)
    return jsonify(history)

@app.route('/api/ai/undo', methods=['POST'])
def ai_undo():
    result = ai_facilitator.undo_last_action()
    return jsonify(result)
```

#### 2. Add AI Facilitator to Web UI

Create a new tab in the STFD web interface:

```html
<!-- AI Assistant Tab -->
<div class="tab-pane" id="ai-assistant">
    <h3>AI Assistant</h3>
    
    <div class="ai-status">
        <span id="user-present-indicator"></span>
        <span id="ai-status-text"></span>
    </div>
    
    <div class="ai-history">
        <h4>Recent Actions</h4>
        <ul id="ai-history-list"></ul>
    </div>
    
    <button onclick="undoLastAction()">Undo Last Action</button>
</div>

<script>
async function checkAIStatus() {
    const response = await fetch('/api/ai/status');
    const status = await response.json();
    
    const indicator = document.getElementById('user-present-indicator');
    if (status.user_present) {
        indicator.className = 'status-active';
        indicator.textContent = '● AI Active';
    } else {
        indicator.className = 'status-inactive';
        indicator.textContent = '○ AI Inactive (Insert USB Sentinel)';
    }
}

async function loadAIHistory() {
    const response = await fetch('/api/ai/history?limit=10');
    const history = await response.json();
    
    const list = document.getElementById('ai-history-list');
    list.innerHTML = history.map(tx => `
        <li class="tx-${tx.status}">
            <span class="tx-time">${new Date(tx.timestamp).toLocaleString()}</span>
            <span class="tx-command">${tx.command}</span>
            <span class="tx-status">${tx.status}</span>
        </li>
    `).join('');
}

async function undoLastAction() {
    if (!confirm('Undo the last AI action?')) return;
    
    const response = await fetch('/api/ai/undo', { method: 'POST' });
    const result = await response.json();
    
    if (result.status === 'success') {
        alert('Action undone successfully!');
        loadAIHistory();
    } else {
        alert(`Failed to undo: ${result.error}`);
    }
}

// Update status every 5 seconds
setInterval(checkAIStatus, 5000);
setInterval(loadAIHistory, 10000);
</script>
```

#### 3. Use AI Facilitator in Deployment Modules

Example: Installing Docker via Distrobox for network tools

```python
# In shut-the-front-door/installer/modules/docker_setup.py

from ai_facilitator import AIFacilitatorServer

def setup_docker_environment():
    """Set up Docker in a Distrobox container"""
    ai = AIFacilitatorServer()
    ai.start()
    
    # Create Distrobox with Docker
    result = ai.execute_command("distrobox_create", {
        "name": "network-tools",
        "distro": "ubuntu:24.04",
        "additional_packages": ["docker.io", "docker-compose"]
    })
    
    if result['status'] == 'success':
        return {
            "success": True,
            "container": "network-tools",
            "message": "Docker environment ready"
        }
    else:
        return {
            "success": False,
            "error": result.get('error', 'Unknown error')
        }
```

## Integration with MCP Servers

The AI Facilitator can be exposed as an MCP server for use with Windsurf and other MCP clients.

### MCP Server Implementation

Create `/home/LemonKaiju/projects/Linux testbed/ai_facilitator/mcp_server.py`:

```python
#!/usr/bin/env python3
"""
MCP Server for AI Facilitator
Exposes AI Facilitator functionality via Model Context Protocol
"""

import json
import sys
from typing import Any, Dict

from ai_facilitator import AIFacilitatorServer

# Initialize server
facilitator = AIFacilitatorServer()
facilitator.start()


def handle_tool_call(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Handle MCP tool calls"""
    
    if tool_name == "ai_facilitator_execute":
        command = arguments.get("command")
        args = arguments.get("args", {})
        return facilitator.execute_command(command, args)
    
    elif tool_name == "ai_facilitator_status":
        return facilitator.get_status()
    
    elif tool_name == "ai_facilitator_history":
        limit = arguments.get("limit", 50)
        return {"history": facilitator.get_history(limit)}
    
    elif tool_name == "ai_facilitator_undo":
        return facilitator.undo_last_action()
    
    else:
        return {"error": f"Unknown tool: {tool_name}"}


def main():
    """MCP server main loop"""
    # Read MCP protocol messages from stdin
    for line in sys.stdin:
        try:
            message = json.loads(line)
            
            if message.get("method") == "tools/call":
                params = message.get("params", {})
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                result = handle_tool_call(tool_name, arguments)
                
                response = {
                    "jsonrpc": "2.0",
                    "id": message.get("id"),
                    "result": result
                }
                
                print(json.dumps(response))
                sys.stdout.flush()
                
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": message.get("id") if "message" in locals() else None,
                "error": {
                    "code": -32603,
                    "message": str(e)
                }
            }
            print(json.dumps(error_response))
            sys.stdout.flush()


if __name__ == "__main__":
    main()
```

### Update MCP Configuration

Add to `/home/LemonKaiju/projects/Linux testbed/mcp_config.json`:

```json
{
  "mcpServers": {
    "ai-facilitator": {
      "command": "python3",
      "args": [
        "/home/LemonKaiju/projects/Linux testbed/ai_facilitator/mcp_server.py"
      ],
      "env": {}
    }
  }
}
```

## Security Considerations

### 1. User Presence Enforcement
- AI Facilitator ONLY operates when user is present
- USB sentinel or mobile dashboard must be active
- All operations disabled when user leaves

### 2. Authorization Flow
```
User Request → AI Facilitator → Authorization Manager → User Approval → Execution
                     ↓
              User Not Present?
                     ↓
                  REJECT
```

### 3. Audit Trail
- Every command logged with timestamp
- User approval decisions recorded
- Full undo history maintained
- Logs exportable for review

### 4. Scoped Permissions
- No sudo access required
- PolicyKit handles specific permissions
- Cannot execute arbitrary commands
- Cannot modify system files directly

## Testing Integration

### Test 1: Basic Command Execution
```python
from ai_facilitator import AIFacilitatorServer

ai = AIFacilitatorServer()
ai.start()

result = ai.execute_command("flatpak_install", {
    "app_name": "org.mozilla.firefox"
})

assert result['status'] in ['success', 'rejected', 'error']
```

### Test 2: User Presence Check
```python
status = ai.get_status()
assert 'user_present' in status
assert 'running' in status
```

### Test 3: Transaction Logging
```python
history = ai.get_history(limit=10)
assert isinstance(history, list)
```

### Test 4: Undo Functionality
```python
# Execute a command
result = ai.execute_command("distrobox_create", {
    "name": "test-container",
    "distro": "fedora:39"
})

if result['status'] == 'success':
    # Undo it
    undo_result = ai.undo_last_action()
    assert undo_result['status'] == 'success'
```

## Troubleshooting Integration

### Issue: AI Facilitator not responding
**Solution:** Check user presence status and ensure USB sentinel is connected or mobile dashboard is enabled.

### Issue: Commands failing with permission errors
**Solution:** Verify PolicyKit rules are installed: `ls /etc/polkit-1/rules.d/`

### Issue: Approval notifications not showing
**Solution:** Install zenity: `flatpak install org.gnome.Zenity`

### Issue: MCP server not connecting
**Solution:** Check Python path and ensure ai_facilitator module is importable.

## Next Steps

1. Complete Milestone 2: 6-digit PIN authentication
2. Integrate PIN system with AI Facilitator
3. Add duress protection mechanisms
4. Create security profiles for different users
5. Full STFD integration testing
