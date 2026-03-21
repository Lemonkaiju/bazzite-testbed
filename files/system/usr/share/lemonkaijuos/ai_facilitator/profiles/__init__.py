"""
Security Profiles System for LemonKaijuOS
Different security and access levels for different user types
"""

__version__ = "0.1.0"

from .profile_manager import ProfileManager
from .kiosk_mode import KioskMode
from .backup_automation import BackupAutomation

__all__ = [
    "ProfileManager",
    "KioskMode",
    "BackupAutomation"
]
