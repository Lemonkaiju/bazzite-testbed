"""
Transaction Logging System
Logs all AI actions with undo functionality
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


class TransactionLogger:
    """
    Logs all AI facilitator transactions
    
    Features:
    - Human-readable history
    - Undo functionality
    - Transaction replay
    - Export/import capabilities
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize transaction logger"""
        self.config = config
        self.log_dir = Path(config.get(
            "log_dir",
            Path.home() / ".local" / "share" / "ai_facilitator" / "logs"
        ))
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.max_history = config.get("max_history", 1000)
        self.log_file = self.log_dir / "transactions.json"
        
        # Load existing log
        self.transactions = self._load_log()
        
        logger.info("Transaction Logger initialized")
    
    def _load_log(self) -> List[Dict[str, Any]]:
        """Load transaction log from disk"""
        if self.log_file.exists():
            try:
                with open(self.log_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load transaction log: {e}")
                return []
        return []
    
    def _save_log(self):
        """Save transaction log to disk"""
        try:
            # Keep only max_history entries
            if len(self.transactions) > self.max_history:
                self.transactions = self.transactions[-self.max_history:]
            
            with open(self.log_file, 'w') as f:
                json.dump(self.transactions, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save transaction log: {e}")
    
    def log_action(
        self,
        command: str,
        args: Dict[str, Any],
        status: str,
        result: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        reason: Optional[str] = None
    ) -> str:
        """
        Log an action
        
        Args:
            command: Command name
            args: Command arguments
            status: Status (success, error, rejected)
            result: Command result (if successful)
            error: Error message (if failed)
            reason: Rejection reason (if rejected)
            
        Returns:
            Transaction ID
        """
        transaction_id = str(uuid.uuid4())
        
        transaction = {
            "id": transaction_id,
            "timestamp": datetime.now().isoformat(),
            "command": command,
            "args": args,
            "status": status,
            "result": result,
            "error": error,
            "reason": reason,
            "undone": False
        }
        
        self.transactions.append(transaction)
        self._save_log()
        
        logger.info(f"Logged transaction {transaction_id}: {command} - {status}")
        
        return transaction_id
    
    def get_last_transaction_id(self) -> Optional[str]:
        """Get the ID of the last transaction"""
        if self.transactions:
            return self.transactions[-1].get("id")
        return None
    
    def get_transaction(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific transaction by ID"""
        for transaction in self.transactions:
            if transaction.get("id") == transaction_id:
                return transaction
        return None
    
    def get_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get transaction history
        
        Args:
            limit: Maximum number of transactions to return
            
        Returns:
            List of transactions (most recent first)
        """
        return list(reversed(self.transactions[-limit:]))
    
    def undo_last(self) -> Dict[str, Any]:
        """
        Undo the last successful transaction
        
        Returns:
            Result of undo operation
        """
        # Find last successful, non-undone transaction
        for transaction in reversed(self.transactions):
            if transaction.get("status") == "success" and not transaction.get("undone", False):
                return self._undo_transaction(transaction)
        
        raise ValueError("No transaction to undo")
    
    def undo_transaction(self, transaction_id: str) -> Dict[str, Any]:
        """
        Undo a specific transaction
        
        Args:
            transaction_id: Transaction ID to undo
            
        Returns:
            Result of undo operation
        """
        transaction = self.get_transaction(transaction_id)
        
        if not transaction:
            raise ValueError(f"Transaction {transaction_id} not found")
        
        if transaction.get("undone", False):
            raise ValueError(f"Transaction {transaction_id} already undone")
        
        if transaction.get("status") != "success":
            raise ValueError(f"Cannot undo failed transaction")
        
        return self._undo_transaction(transaction)
    
    def _undo_transaction(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform undo operation for a transaction
        
        Args:
            transaction: Transaction to undo
            
        Returns:
            Result of undo operation
        """
        command = transaction.get("command")
        args = transaction.get("args", {})
        
        logger.info(f"Undoing transaction: {command}")
        
        try:
            if command == "flatpak_install":
                result = self._undo_flatpak_install(args)
            elif command == "rpm_ostree_rollback":
                result = self._undo_rpm_ostree_rollback(args)
            elif command == "distrobox_create":
                result = self._undo_distrobox_create(args)
            elif command == "ujust_setup_gaming":
                result = {"success": False, "message": "Cannot undo gaming setup automatically"}
            else:
                result = {"success": False, "message": f"No undo handler for {command}"}
            
            # Mark transaction as undone
            transaction["undone"] = True
            transaction["undo_timestamp"] = datetime.now().isoformat()
            self._save_log()
            
            return result
            
        except Exception as e:
            logger.error(f"Undo failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _undo_flatpak_install(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Undo Flatpak installation by uninstalling"""
        import subprocess
        
        app_name = args.get("app_name")
        system = args.get("system", False)
        
        cmd = ["flatpak", "uninstall", "-y"]
        
        if system:
            cmd.append("--system")
        else:
            cmd.append("--user")
        
        cmd.append(app_name)
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "message": f"Successfully uninstalled {app_name}"
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr,
                    "message": f"Failed to uninstall {app_name}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _undo_rpm_ostree_rollback(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Undo rpm-ostree rollback by rolling back again"""
        import subprocess
        
        cmd = ["rpm-ostree", "rollback"]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "message": "Rolled back to previous deployment",
                    "requires_reboot": True
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _undo_distrobox_create(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Undo Distrobox creation by removing container"""
        import subprocess
        
        name = args.get("name")
        
        cmd = ["distrobox", "rm", "-f", name]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "message": f"Successfully removed Distrobox '{name}'"
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr,
                    "message": f"Failed to remove Distrobox '{name}'"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def export_history(self, output_file: Path) -> bool:
        """Export transaction history to file"""
        try:
            with open(output_file, 'w') as f:
                json.dump(self.transactions, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Failed to export history: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get transaction statistics"""
        total = len(self.transactions)
        successful = sum(1 for t in self.transactions if t.get("status") == "success")
        failed = sum(1 for t in self.transactions if t.get("status") == "error")
        rejected = sum(1 for t in self.transactions if t.get("status") == "rejected")
        undone = sum(1 for t in self.transactions if t.get("undone", False))
        
        # Command breakdown
        commands = {}
        for t in self.transactions:
            cmd = t.get("command")
            commands[cmd] = commands.get(cmd, 0) + 1
        
        return {
            "total_transactions": total,
            "successful": successful,
            "failed": failed,
            "rejected": rejected,
            "undone": undone,
            "command_breakdown": commands,
            "last_transaction": self.transactions[-1].get("timestamp") if self.transactions else None
        }
