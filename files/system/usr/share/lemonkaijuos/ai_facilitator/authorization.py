"""
Declarative Authorization System
All AI actions require single-tap user approval
"""

import logging
import time
import json
from pathlib import Path
from typing import Dict, Any, Optional, Callable
from datetime import datetime
import subprocess

logger = logging.getLogger(__name__)


class AuthorizationManager:
    """
    Manages declarative authorization for AI actions
    
    Features:
    - Single-tap approval via desktop notification
    - Approval timeout (default 5 minutes)
    - Command proposal queue
    - Approval history
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize authorization manager"""
        self.config = config
        self.require_approval = config.get("require_approval", True)
        self.approval_timeout = config.get("approval_timeout", 300)
        self.notification_method = config.get("notification_method", "desktop")
        
        # History file
        self.history_file = Path(config.get(
            "history_file",
            Path.home() / ".local" / "share" / "ai_facilitator" / "approval_history.json"
        ))
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Pending approvals
        self.pending_approvals: Dict[str, Dict[str, Any]] = {}
        
        logger.info("Authorization Manager initialized")
    
    def request_approval(self, proposal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Request user approval for a command
        
        Args:
            proposal: Command proposal with id, command, args
            
        Returns:
            Result dict with approved: bool and optional reason
        """
        if not self.require_approval:
            # Auto-approve if approval not required
            return {"approved": True, "reason": "Auto-approved (approval disabled)"}
        
        proposal_id = proposal.get("id")
        command = proposal.get("command")
        args = proposal.get("args", {})
        
        # Create human-readable description
        description = self._format_proposal(command, args)
        
        # Store pending approval
        self.pending_approvals[proposal_id] = {
            "proposal": proposal,
            "timestamp": time.time(),
            "status": "pending"
        }
        
        # Send notification and wait for response
        if self.notification_method == "desktop":
            result = self._request_desktop_approval(proposal_id, description)
        elif self.notification_method == "mobile":
            result = self._request_mobile_approval(proposal_id, description)
        else:
            result = self._request_cli_approval(proposal_id, description)
        
        # Log approval decision
        self._log_approval(proposal_id, result)
        
        # Clean up pending
        if proposal_id in self.pending_approvals:
            del self.pending_approvals[proposal_id]
        
        return result
    
    def _format_proposal(self, command: str, args: Dict[str, Any]) -> str:
        """Format command proposal for human readability"""
        if command == "flatpak_install":
            app = args.get("app_name", "unknown app")
            return f"Install {app} via Flatpak"
        
        elif command == "rpm_ostree_rollback":
            return "Roll back system to previous deployment"
        
        elif command == "distrobox_create":
            name = args.get("name", "unnamed")
            distro = args.get("distro", "fedora")
            return f"Create Distrobox container '{name}' ({distro})"
        
        elif command == "ujust_setup_gaming":
            return "Set up gaming environment"
        
        else:
            return f"Execute: {command} with {args}"
    
    def _request_desktop_approval(self, proposal_id: str, description: str) -> Dict[str, Any]:
        """
        Request approval via desktop notification
        Uses notify-send with actions (requires notification daemon that supports actions)
        """
        try:
            # Create notification with Yes/No actions
            # Format: notify-send with urgency critical to ensure it's visible
            notification_title = "AI Facilitator - Approval Required"
            notification_body = f"{description}\n\nAllow AI to execute this action?"
            
            # Try using zenity for graphical approval (more reliable than notify-send actions)
            result = subprocess.run(
                [
                    "zenity",
                    "--question",
                    "--title", notification_title,
                    "--text", notification_body,
                    "--ok-label", "Yes, Allow",
                    "--cancel-label", "No, Reject",
                    "--width", "400",
                    "--timeout", str(self.approval_timeout)
                ],
                capture_output=True,
                timeout=self.approval_timeout + 5
            )
            
            if result.returncode == 0:
                # User clicked Yes
                return {"approved": True, "reason": "User approved via desktop"}
            elif result.returncode == 1:
                # User clicked No
                return {"approved": False, "reason": "User rejected via desktop"}
            else:
                # Timeout or error
                return {"approved": False, "reason": "Approval timeout"}
                
        except FileNotFoundError:
            # zenity not available, fallback to notify-send
            logger.warning("zenity not available, using notify-send fallback")
            try:
                subprocess.run(
                    [
                        "notify-send",
                        "-u", "critical",
                        "-t", "10000",
                        notification_title,
                        notification_body
                    ],
                    timeout=5
                )
                
                # Since notify-send doesn't support actions reliably, use CLI fallback
                return self._request_cli_approval(proposal_id, description)
                
            except Exception as e:
                logger.error(f"Desktop notification failed: {e}")
                return {"approved": False, "reason": f"Notification failed: {e}"}
        
        except Exception as e:
            logger.error(f"Desktop approval failed: {e}")
            return {"approved": False, "reason": f"Approval failed: {e}"}
    
    def _request_mobile_approval(self, proposal_id: str, description: str) -> Dict[str, Any]:
        """
        Request approval via mobile dashboard
        Creates a pending approval that the mobile app can respond to
        """
        # Create approval request file
        approval_file = Path.home() / ".local" / "share" / "ai_facilitator" / "pending_approvals" / f"{proposal_id}.json"
        approval_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(approval_file, 'w') as f:
                json.dump({
                    "id": proposal_id,
                    "description": description,
                    "timestamp": time.time(),
                    "status": "pending"
                }, f, indent=2)
            
            # Wait for response (check every second)
            start_time = time.time()
            while time.time() - start_time < self.approval_timeout:
                if approval_file.exists():
                    try:
                        with open(approval_file, 'r') as f:
                            data = json.load(f)
                            status = data.get("status")
                            
                            if status == "approved":
                                approval_file.unlink()
                                return {"approved": True, "reason": "User approved via mobile"}
                            elif status == "rejected":
                                approval_file.unlink()
                                return {"approved": False, "reason": "User rejected via mobile"}
                    except Exception:
                        pass
                
                time.sleep(1)
            
            # Timeout
            if approval_file.exists():
                approval_file.unlink()
            return {"approved": False, "reason": "Mobile approval timeout"}
            
        except Exception as e:
            logger.error(f"Mobile approval failed: {e}")
            return {"approved": False, "reason": f"Mobile approval failed: {e}"}
    
    def _request_cli_approval(self, proposal_id: str, description: str) -> Dict[str, Any]:
        """
        Request approval via CLI prompt
        Fallback method when GUI not available
        """
        print("\n" + "="*60)
        print("AI FACILITATOR - APPROVAL REQUIRED")
        print("="*60)
        print(f"\n{description}\n")
        print("Allow AI to execute this action?")
        print("  [Y] Yes, Allow")
        print("  [N] No, Reject")
        print("="*60)
        
        try:
            # Use timeout for input
            import select
            import sys
            
            print("Your choice (Y/N): ", end='', flush=True)
            
            # Wait for input with timeout
            ready, _, _ = select.select([sys.stdin], [], [], self.approval_timeout)
            
            if ready:
                response = sys.stdin.readline().strip().lower()
                if response in ['y', 'yes']:
                    return {"approved": True, "reason": "User approved via CLI"}
                else:
                    return {"approved": False, "reason": "User rejected via CLI"}
            else:
                print("\nTimeout - request rejected")
                return {"approved": False, "reason": "CLI approval timeout"}
                
        except Exception as e:
            logger.error(f"CLI approval failed: {e}")
            return {"approved": False, "reason": f"CLI approval failed: {e}"}
    
    def _log_approval(self, proposal_id: str, result: Dict[str, Any]):
        """Log approval decision to history"""
        try:
            # Load existing history
            history = []
            if self.history_file.exists():
                with open(self.history_file, 'r') as f:
                    history = json.load(f)
            
            # Add new entry
            history.append({
                "proposal_id": proposal_id,
                "timestamp": datetime.now().isoformat(),
                "approved": result.get("approved", False),
                "reason": result.get("reason", "Unknown")
            })
            
            # Keep only last 1000 entries
            history = history[-1000:]
            
            # Save
            with open(self.history_file, 'w') as f:
                json.dump(history, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to log approval: {e}")
    
    def get_pending_approvals(self) -> Dict[str, Dict[str, Any]]:
        """Get all pending approvals"""
        return self.pending_approvals.copy()
    
    def get_approval_history(self, limit: int = 50) -> list:
        """Get approval history"""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r') as f:
                    history = json.load(f)
                    return history[-limit:]
        except Exception as e:
            logger.error(f"Failed to load approval history: {e}")
        
        return []
