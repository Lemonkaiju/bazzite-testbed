"""
Security Protection Systems for LemonKaijuOS
Duress codes, intrusion protection, and physical theft protection
"""

__version__ = "0.1.0"

from .duress import DuressManager
from .intrusion import IntrusionProtection
from .physical_security import PhysicalSecurityManager

__all__ = [
    "DuressManager",
    "IntrusionProtection",
    "PhysicalSecurityManager"
]
