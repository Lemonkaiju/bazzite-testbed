"""
Bazzite-Architect AI Facilitator Framework
A safety-first AI command server for LemonKaijuOS and Shut The Front Door

This module provides:
- User-Present flag detection (USB key/mobile dashboard)
- PolicyKit-based scoped permissions
- MCP tool wrappers for safe command execution
- Transaction logging and undo functionality
- Declarative authorization system
"""

__version__ = "0.1.0"
__author__ = "LemonKaiju"

from .server import AIFacilitatorServer
from .authorization import AuthorizationManager
from .mcp_tools import MCPToolWrapper
from .transaction_log import TransactionLogger

__all__ = [
    "AIFacilitatorServer",
    "AuthorizationManager", 
    "MCPToolWrapper",
    "TransactionLogger"
]
