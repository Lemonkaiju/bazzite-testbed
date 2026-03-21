"""
PIN Authentication System for LemonKaijuOS
6-digit PIN system that replaces password prompts for daily tasks
"""

__version__ = "0.1.0"

from .pin_manager import PINManager
from .pam_config import PAMConfigurator
from .recovery import RecoveryManager

__all__ = [
    "PINManager",
    "PAMConfigurator",
    "RecoveryManager"
]
