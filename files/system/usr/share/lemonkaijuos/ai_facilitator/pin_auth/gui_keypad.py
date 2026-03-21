"""
GUI Keypad - Phone-style PIN entry for touchscreen and desktop
"""

import sys
import logging
from pathlib import Path
from typing import Optional, Callable

try:
    from PyQt5.QtWidgets import (
        QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
        QGridLayout, QPushButton, QLabel, QLineEdit
    )
    from PyQt5.QtCore import Qt, QSize
    from PyQt5.QtGui import QFont, QPalette, QColor
    HAVE_QT = True
except ImportError:
    HAVE_QT = False

logger = logging.getLogger(__name__)


class PINKeypad(QWidget):
    """
    Phone-style PIN keypad for touchscreen-friendly PIN entry
    
    Features:
    - Large touch-friendly buttons (80x80px minimum)
    - Phone-style layout (1-9, 0 centered)
    - Visual feedback on button press
    - Masked PIN display (dots)
    - Backspace and clear functions
    - Enter/submit button
    - Works on touchscreen, laptop, desktop
    """
    
    def __init__(self, 
                 title: str = "Enter PIN",
                 max_length: int = 6,
                 on_submit: Optional[Callable] = None,
                 on_cancel: Optional[Callable] = None):
        """
        Initialize PIN keypad
        
        Args:
            title: Window title
            max_length: Maximum PIN length (default 6)
            on_submit: Callback when PIN is submitted
            on_cancel: Callback when cancelled
        """
        super().__init__()
        
        self.max_length = max_length
        self.on_submit = on_submit
        self.on_cancel = on_cancel
        self.pin_value = ""
        
        self.init_ui(title)
    
    def init_ui(self, title: str):
        """Initialize user interface"""
        self.setWindowTitle(title)
        self.setFixedSize(400, 600)
        
        # Main layout
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title label
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # PIN display (masked)
        self.pin_display = QLineEdit()
        self.pin_display.setReadOnly(True)
        self.pin_display.setAlignment(Qt.AlignCenter)
        self.pin_display.setEchoMode(QLineEdit.Password)
        self.pin_display.setPlaceholderText("••••••")
        display_font = QFont()
        display_font.setPointSize(24)
        self.pin_display.setFont(display_font)
        self.pin_display.setMinimumHeight(60)
        self.pin_display.setStyleSheet("""
            QLineEdit {
                border: 2px solid #4ecdc4;
                border-radius: 10px;
                padding: 10px;
                background: white;
            }
        """)
        layout.addWidget(self.pin_display)
        
        # Keypad grid (phone-style layout)
        keypad_layout = QGridLayout()
        keypad_layout.setSpacing(15)
        
        # Number buttons (1-9)
        button_positions = [
            ('1', 0, 0), ('2', 0, 1), ('3', 0, 2),
            ('4', 1, 0), ('5', 1, 1), ('6', 1, 2),
            ('7', 2, 0), ('8', 2, 1), ('9', 2, 2),
        ]
        
        for text, row, col in button_positions:
            btn = self.create_number_button(text)
            keypad_layout.addWidget(btn, row, col)
        
        # Bottom row: Backspace, 0, Enter
        backspace_btn = self.create_action_button("⌫", self.backspace)
        keypad_layout.addWidget(backspace_btn, 3, 0)
        
        zero_btn = self.create_number_button('0')
        keypad_layout.addWidget(zero_btn, 3, 1)
        
        enter_btn = self.create_action_button("✓", self.submit_pin, primary=True)
        keypad_layout.addWidget(enter_btn, 3, 2)
        
        layout.addLayout(keypad_layout)
        
        # Cancel button
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setMinimumHeight(50)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff6b6b;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff5252;
            }
            QPushButton:pressed {
                background-color: #ff3838;
            }
        """)
        cancel_btn.clicked.connect(self.cancel)
        layout.addWidget(cancel_btn)
        
        # Attempt counter (hidden by default)
        self.attempt_label = QLabel("")
        self.attempt_label.setAlignment(Qt.AlignCenter)
        self.attempt_label.setStyleSheet("color: #ff6b6b; font-size: 14px;")
        self.attempt_label.hide()
        layout.addWidget(self.attempt_label)
        
        self.setLayout(layout)
        
        # Apply modern styling
        self.setStyleSheet("""
            QWidget {
                background-color: #f7f7f7;
            }
        """)
    
    def create_number_button(self, number: str) -> QPushButton:
        """Create a number button"""
        btn = QPushButton(number)
        btn.setMinimumSize(QSize(80, 80))
        btn.setMaximumSize(QSize(100, 100))
        btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: 2px solid #e0e0e0;
                border-radius: 10px;
                font-size: 28px;
                font-weight: bold;
                color: #2c3e50;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
                border-color: #4ecdc4;
            }
            QPushButton:pressed {
                background-color: #4ecdc4;
                color: white;
            }
        """)
        btn.clicked.connect(lambda: self.add_digit(number))
        return btn
    
    def create_action_button(self, text: str, callback: Callable, primary: bool = False) -> QPushButton:
        """Create an action button (backspace, enter, etc.)"""
        btn = QPushButton(text)
        btn.setMinimumSize(QSize(80, 80))
        btn.setMaximumSize(QSize(100, 100))
        
        if primary:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #4ecdc4;
                    border: none;
                    border-radius: 10px;
                    font-size: 32px;
                    font-weight: bold;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #3db9b0;
                }
                QPushButton:pressed {
                    background-color: #2ca59c;
                }
            """)
        else:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #556270;
                    border: none;
                    border-radius: 10px;
                    font-size: 28px;
                    font-weight: bold;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #465161;
                }
                QPushButton:pressed {
                    background-color: #374152;
                }
            """)
        
        btn.clicked.connect(callback)
        return btn
    
    def add_digit(self, digit: str):
        """Add a digit to the PIN"""
        if len(self.pin_value) < self.max_length:
            self.pin_value += digit
            self.pin_display.setText(self.pin_value)
    
    def backspace(self):
        """Remove last digit"""
        if self.pin_value:
            self.pin_value = self.pin_value[:-1]
            self.pin_display.setText(self.pin_value)
    
    def submit_pin(self):
        """Submit the PIN"""
        if len(self.pin_value) == self.max_length:
            if self.on_submit:
                self.on_submit(self.pin_value)
            self.close()
        else:
            self.show_error(f"PIN must be {self.max_length} digits")
    
    def cancel(self):
        """Cancel PIN entry"""
        if self.on_cancel:
            self.on_cancel()
        self.close()
    
    def show_error(self, message: str):
        """Show error message"""
        self.attempt_label.setText(message)
        self.attempt_label.show()
        # Clear PIN on error
        self.pin_value = ""
        self.pin_display.setText("")
    
    def show_attempts(self, attempts_left: int):
        """Show remaining attempts"""
        if attempts_left <= 3:
            self.attempt_label.setText(f"⚠️ {attempts_left} attempts remaining")
            self.attempt_label.show()
    
    def get_pin(self) -> str:
        """Get the entered PIN"""
        return self.pin_value


def show_pin_dialog(title: str = "Enter PIN",
                    max_length: int = 6,
                    attempts_left: Optional[int] = None) -> Optional[str]:
    """
    Show PIN entry dialog and return entered PIN
    
    Args:
        title: Dialog title
        max_length: Maximum PIN length
        attempts_left: Number of attempts remaining (shows warning)
        
    Returns:
        Entered PIN or None if cancelled
    """
    if not HAVE_QT:
        logger.error("PyQt5 not available, cannot show GUI keypad")
        return None
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    result = {'pin': None}
    
    def on_submit(pin: str):
        result['pin'] = pin
    
    keypad = PINKeypad(title=title, max_length=max_length, on_submit=on_submit)
    
    if attempts_left is not None:
        keypad.show_attempts(attempts_left)
    
    keypad.show()
    app.exec_()
    
    return result['pin']


def show_lockscreen_keypad(username: str, attempts_left: int = 5) -> Optional[str]:
    """
    Show lockscreen-style PIN keypad
    
    Args:
        username: Username for display
        attempts_left: Number of attempts remaining
        
    Returns:
        Entered PIN or None if cancelled
    """
    title = f"🔒 Unlock - {username}"
    return show_pin_dialog(title=title, attempts_left=attempts_left)


if __name__ == "__main__":
    # Test the keypad
    if HAVE_QT:
        pin = show_lockscreen_keypad("testuser", attempts_left=3)
        if pin:
            print(f"Entered PIN: {pin}")
        else:
            print("Cancelled")
    else:
        print("PyQt5 not installed. Install with: pip install PyQt5")
