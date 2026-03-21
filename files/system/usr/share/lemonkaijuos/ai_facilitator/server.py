"""
AI Facilitator Server - Main Command Server
Handles AI command execution with safety-first red team logic
"""

import os
import sys
import json
import logging
import threading
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

from .user_present import UserPresentDetector
from .authorization import AuthorizationManager
from .mcp_tools import MCPToolWrapper
from .transaction_log import TransactionLogger

logger = logging.getLogger(__name__)


class AIFacilitatorServer:
    """
    Main AI Facilitator Server
    
    Safety Rules:
    1. Only executes when User-Present flag is active
    2. No sudo access - uses PolicyKit delegation only
    3. All changes are declarative - requires user approval
    4. No raw shell script execution
    5. All actions are logged and reversible
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize the AI Facilitator Server"""
        self.config_path = config_path or Path.home() / ".config" / "ai_facilitator" / "config.json"
        self.config = self._load_config()
        
        # Initialize components
        self.user_present = UserPresentDetector(self.config.get("user_present", {}))
        self.authorization = AuthorizationManager(self.config.get("authorization", {}))
        self.mcp_tools = MCPToolWrapper(self.config.get("mcp_tools", {}))
        self.transaction_log = TransactionLogger(self.config.get("transaction_log", {}))
        
        # Server state
        self.running = False
        self.command_queue: List[Dict[str, Any]] = []
        self._lock = threading.Lock()
        
        logger.info("AI Facilitator Server initialized")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load server configuration"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                return {}
        
        # Default configuration
        default_config = {
            "user_present": {
                "usb_sentinel_enabled": True,
                "mobile_dashboard_enabled": False,
                "check_interval": 5
            },
            "authorization": {
                "require_approval": True,
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
                "log_dir": str(Path.home() / ".local" / "share" / "ai_facilitator" / "logs"),
                "max_history": 1000
            }
        }
        
        # Create config directory and save default
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save default config: {e}")
        
        return default_config
    
    def start(self):
        """Start the AI Facilitator Server"""
        if self.running:
            logger.warning("Server already running")
            return
        
        self.running = True
        logger.info("AI Facilitator Server started")
        
        # Start user presence monitoring
        self.user_present.start_monitoring()
        
        # Start command processing loop
        self._processing_thread = threading.Thread(target=self._process_commands, daemon=True)
        self._processing_thread.start()
    
    def stop(self):
        """Stop the AI Facilitator Server"""
        if not self.running:
            return
        
        self.running = False
        self.user_present.stop_monitoring()
        logger.info("AI Facilitator Server stopped")
    
    def execute_command(self, command: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a command through the AI Facilitator
        
        Args:
            command: Command name (e.g., "flatpak_install")
            args: Command arguments
            
        Returns:
            Result dictionary with status and output
        """
        # Safety check: User must be present
        if not self.user_present.is_user_present():
            return {
                "status": "error",
                "error": "User-Present flag not active. Insert security USB or enable mobile dashboard.",
                "timestamp": datetime.now().isoformat()
            }
        
        # Create command proposal
        proposal = {
            "id": self._generate_command_id(),
            "command": command,
            "args": args,
            "timestamp": datetime.now().isoformat(),
            "status": "pending_approval"
        }
        
        # Add to queue
        with self._lock:
            self.command_queue.append(proposal)
        
        # Request authorization
        approval_result = self.authorization.request_approval(proposal)
        
        if not approval_result.get("approved", False):
            self.transaction_log.log_action(
                command=command,
                args=args,
                status="rejected",
                reason=approval_result.get("reason", "User rejected")
            )
            return {
                "status": "rejected",
                "reason": approval_result.get("reason", "User rejected"),
                "timestamp": datetime.now().isoformat()
            }
        
        # Execute through MCP tools
        try:
            result = self.mcp_tools.execute(command, args)
            
            # Log transaction
            self.transaction_log.log_action(
                command=command,
                args=args,
                status="success",
                result=result
            )
            
            return {
                "status": "success",
                "result": result,
                "timestamp": datetime.now().isoformat(),
                "transaction_id": self.transaction_log.get_last_transaction_id()
            }
            
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            self.transaction_log.log_action(
                command=command,
                args=args,
                status="error",
                error=str(e)
            )
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def undo_last_action(self) -> Dict[str, Any]:
        """Undo the last executed action"""
        if not self.user_present.is_user_present():
            return {
                "status": "error",
                "error": "User-Present flag not active"
            }
        
        try:
            result = self.transaction_log.undo_last()
            return {
                "status": "success",
                "result": result
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def get_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get command execution history"""
        return self.transaction_log.get_history(limit)
    
    def _process_commands(self):
        """Background command processing loop"""
        while self.running:
            time.sleep(1)
            # Process any queued commands
            # This is a placeholder for future async command handling
    
    def _generate_command_id(self) -> str:
        """Generate unique command ID"""
        import uuid
        return str(uuid.uuid4())
    
    def get_status(self) -> Dict[str, Any]:
        """Get server status"""
        return {
            "running": self.running,
            "user_present": self.user_present.is_user_present(),
            "pending_commands": len(self.command_queue),
            "last_transaction": self.transaction_log.get_last_transaction_id()
        }


def main():
    """Main entry point for AI Facilitator Server"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    server = AIFacilitatorServer()
    
    try:
        server.start()
        logger.info("AI Facilitator Server running. Press Ctrl+C to stop.")
        
        # Keep running
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        server.stop()
        sys.exit(0)


if __name__ == "__main__":
    main()
