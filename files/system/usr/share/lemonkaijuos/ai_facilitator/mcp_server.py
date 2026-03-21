#!/usr/bin/env python3
"""
MCP Server for AI Facilitator
Exposes AI Facilitator functionality via Model Context Protocol
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

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
