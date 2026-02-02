"""
Login Window
PyQt5 login dialog with responsive layout for Windows high-DPI screens.
Supports both Sign In and Sign Up modes.
"""
import sys
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QSpacerItem, QSizePolicy, QApplication
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QPalette, QColor

from api import api


class LoginWindow(QWidget):
    """Responsive login window with centered card layout and signup support."""

    login_successful = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.is_signup_mode = False
        self._setup_window()
        self._build_ui()
        self._apply_styles()

    def _setup_window(self):
        """Configure window properties."""
        self.setWindowTitle("Chemical Equipment Visualizer - Login")
        self.setMinimumSize(400, 520)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def _build_ui(self):
        """Build the UI with proper layouts."""
        # Root layout
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)

        # Top spacer for vertical centering
        root.addSpacerItem(QSpacerItem(1, 1, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Horizontal layout for centering card
        center_h = QHBoxLayout()
        center_h.addSpacerItem(QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum))

        # Card frame
        self.card = QFrame()
        self.card.setObjectName("loginCard")
        self.card.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(32, 36, 32, 36)
        card_layout.setSpacing(0)

        # Logo
        self.logo = QLabel("🧪")
        self.logo.setAlignment(Qt.AlignCenter)
        self.logo.setFont(QFont("Segoe UI Emoji", 36))
        card_layout.addWidget(self.logo)

        card_layout.addSpacing(8)

        # Title
        self.title = QLabel("Chemical Equipment\nVisualizer")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setObjectName("titleLabel")
        self.title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        card_layout.addWidget(self.title)

        card_layout.addSpacing(24)

        # Form layout for inputs
        form = QFormLayout()
        form.setContentsMargins(0, 0, 0, 0)
        form.setSpacing(6)
        form.setLabelAlignment(Qt.AlignLeft)
        form.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)

        # Username
        self.username_label = QLabel("Username")
        self.username_label.setFont(QFont("Segoe UI", 10, QFont.DemiBold))
        self.username_label.setObjectName("fieldLabel")

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setFont(QFont("Segoe UI", 11))
        self.username_input.setObjectName("inputField")
        self.username_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        form.addRow(self.username_label)
        form.addRow(self.username_input)

        # Spacer between fields
        form.addItem(QSpacerItem(1, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # Password
        self.password_label = QLabel("Password")
        self.password_label.setFont(QFont("Segoe UI", 10, QFont.DemiBold))
        self.password_label.setObjectName("fieldLabel")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFont(QFont("Segoe UI", 11))
        self.password_input.setObjectName("inputField")
        self.password_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        form.addRow(self.password_label)
        form.addRow(self.password_input)

        # Spacer between fields
        form.addItem(QSpacerItem(1, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))

        # Confirm Password (signup only)
        self.confirm_password_label = QLabel("Confirm Password")
        self.confirm_password_label.setFont(QFont("Segoe UI", 10, QFont.DemiBold))
        self.confirm_password_label.setObjectName("fieldLabel")
        self.confirm_password_label.setVisible(False)

        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("Confirm your password")
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        self.confirm_password_input.setFont(QFont("Segoe UI", 11))
        self.confirm_password_input.setObjectName("inputField")
        self.confirm_password_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.confirm_password_input.setVisible(False)

        form.addRow(self.confirm_password_label)
        form.addRow(self.confirm_password_input)

        # Spacer between fields (signup only)
        self.email_spacer = QSpacerItem(1, 10, QSizePolicy.Minimum, QSizePolicy.Fixed)
        form.addItem(self.email_spacer)

        # Email (signup only, optional)
        self.email_label = QLabel("Email (optional)")
        self.email_label.setFont(QFont("Segoe UI", 10, QFont.DemiBold))
        self.email_label.setObjectName("fieldLabel")
        self.email_label.setVisible(False)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter your email")
        self.email_input.setFont(QFont("Segoe UI", 11))
        self.email_input.setObjectName("inputField")
        self.email_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.email_input.setVisible(False)

        form.addRow(self.email_label)
        form.addRow(self.email_input)

        card_layout.addLayout(form)

        card_layout.addSpacing(20)

        # Login/Signup button
        self.login_btn = QPushButton("Sign In")
        self.login_btn.setObjectName("loginBtn")
        self.login_btn.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.login_btn.setCursor(Qt.PointingHandCursor)
        self.login_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.login_btn.clicked.connect(self._handle_submit)
        card_layout.addWidget(self.login_btn)

        card_layout.addSpacing(10)

        # Toggle mode button
        self.toggle_btn = QPushButton("Don't have an account? Sign Up")
        self.toggle_btn.setObjectName("toggleBtn")
        self.toggle_btn.setFont(QFont("Segoe UI", 9))
        self.toggle_btn.setCursor(Qt.PointingHandCursor)
        self.toggle_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.toggle_btn.clicked.connect(self._toggle_mode)
        card_layout.addWidget(self.toggle_btn)

        card_layout.addSpacing(12)

        # Message label (for errors and success)
        self.message_label = QLabel("")
        self.message_label.setObjectName("errorLabel")
        self.message_label.setAlignment(Qt.AlignCenter)
        self.message_label.setWordWrap(True)
        self.message_label.setFont(QFont("Segoe UI", 9))
        self.message_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        card_layout.addWidget(self.message_label)

        # Add card to horizontal center layout
        center_h.addWidget(self.card)
        center_h.addSpacerItem(QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum))

        root.addLayout(center_h)

        # Bottom spacer for vertical centering
        root.addSpacerItem(QSpacerItem(1, 1, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Keyboard navigation
        self.username_input.returnPressed.connect(lambda: self.password_input.setFocus())
        self.password_input.returnPressed.connect(self._on_password_enter)
        self.confirm_password_input.returnPressed.connect(lambda: self.email_input.setFocus())
        self.email_input.returnPressed.connect(self._handle_submit)

    def _on_password_enter(self):
        """Handle Enter key on password field."""
        if self.is_signup_mode:
            self.confirm_password_input.setFocus()
        else:
            self._handle_submit()

    def _toggle_mode(self):
        """Toggle between login and signup modes."""
        self.is_signup_mode = not self.is_signup_mode
        self._clear_form()
        
        # Update visibility
        self.confirm_password_label.setVisible(self.is_signup_mode)
        self.confirm_password_input.setVisible(self.is_signup_mode)
        self.email_label.setVisible(self.is_signup_mode)
        self.email_input.setVisible(self.is_signup_mode)
        
        # Update button texts
        if self.is_signup_mode:
            self.login_btn.setText("Sign Up")
            self.toggle_btn.setText("Already have an account? Sign In")
            self.password_input.setPlaceholderText("Create password (min 8 chars)")
        else:
            self.login_btn.setText("Sign In")
            self.toggle_btn.setText("Don't have an account? Sign Up")
            self.password_input.setPlaceholderText("Enter your password")

    def _clear_form(self):
        """Clear all input fields."""
        self.username_input.clear()
        self.password_input.clear()
        self.confirm_password_input.clear()
        self.email_input.clear()
        self.message_label.clear()
        self.message_label.setObjectName("errorLabel")
        self._apply_styles()

    def _apply_styles(self):
        """Apply stylesheet."""
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #e0f7fa, stop:0.5 #f3e5f5, stop:1 #e8f5e9
                );
            }
            #loginCard {
                background-color: rgba(255, 255, 255, 0.97);
                border-radius: 14px;
                border: 1px solid rgba(0, 0, 0, 0.06);
                min-width: 280px;
                max-width: 340px;
            }
            #titleLabel {
                color: #5c6bc0;
            }
            #fieldLabel {
                color: #555;
                padding-bottom: 2px;
            }
            #inputField {
                padding: 10px 12px;
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                background-color: #fafafa;
                color: #333;
                min-height: 18px;
            }
            #inputField:focus {
                border-color: #7c4dff;
                background-color: #fff;
            }
            #loginBtn {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #7c4dff, stop:1 #448aff
                );
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 20px;
                min-height: 20px;
            }
            #loginBtn:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #651fff, stop:1 #2979ff
                );
            }
            #loginBtn:pressed {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #6200ea, stop:1 #2962ff
                );
            }
            #loginBtn:disabled {
                background: #bdbdbd;
            }
            #toggleBtn {
                background: transparent;
                border: none;
                color: #6366f1;
                padding: 8px;
            }
            #toggleBtn:hover {
                color: #4f46e5;
                text-decoration: underline;
            }
            #errorLabel {
                color: #e53935;
                min-height: 16px;
            }
            #successLabel {
                color: #059669;
                min-height: 16px;
            }
        """)

    def _handle_submit(self):
        """Process login or signup request."""
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if not username:
            self._show_error("Please enter your username")
            self.username_input.setFocus()
            return

        if len(username) < 3 and self.is_signup_mode:
            self._show_error("Username must be at least 3 characters")
            self.username_input.setFocus()
            return

        if not password:
            self._show_error("Please enter your password")
            self.password_input.setFocus()
            return

        if self.is_signup_mode:
            # Signup validation
            if len(password) < 8:
                self._show_error("Password must be at least 8 characters")
                self.password_input.setFocus()
                return

            confirm_password = self.confirm_password_input.text()
            if not confirm_password:
                self._show_error("Please confirm your password")
                self.confirm_password_input.setFocus()
                return

            if password != confirm_password:
                self._show_error("Passwords do not match")
                self.confirm_password_input.setFocus()
                return

            email = self.email_input.text().strip()

            self.login_btn.setEnabled(False)
            self.login_btn.setText("Creating account...")
            self.message_label.clear()
            QApplication.processEvents()

            result = api.register(username, password, confirm_password, email)

            self.login_btn.setEnabled(True)
            self.login_btn.setText("Sign Up")

            if result["success"]:
                self._show_success(result["message"])
                # Auto switch to login after 2 seconds
                QTimer.singleShot(2000, self._toggle_mode)
            else:
                self._show_error(result["message"])
        else:
            # Login
            self.login_btn.setEnabled(False)
            self.login_btn.setText("Signing in...")
            self.message_label.clear()
            QApplication.processEvents()

            result = api.login(username, password)

            self.login_btn.setEnabled(True)
            self.login_btn.setText("Sign In")

            if result["success"]:
                self.login_successful.emit()
            else:
                # Add hint to sign up if login fails
                error_msg = result["message"]
                if "Invalid" in error_msg or "password" in error_msg.lower():
                    error_msg += " Don't have an account? Sign up first!"
                self._show_error(error_msg)

    def _show_error(self, msg: str):
        """Display error message."""
        self.message_label.setObjectName("errorLabel")
        self._apply_styles()
        self.message_label.setText(msg)

    def _show_success(self, msg: str):
        """Display success message."""
        self.message_label.setObjectName("successLabel")
        self._apply_styles()
        self.message_label.setText(msg)


# Standalone test
if __name__ == "__main__":
    # High-DPI scaling (must be before QApplication)
    if hasattr(Qt, "AA_EnableHighDpiScaling"):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, "AA_UseHighDpiPixmaps"):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Mock api for testing
    class MockAPI:
        def login(self, u, p):
            return {"success": False, "message": "Test mode - no backend"}
        def register(self, u, p, cp, e=""):
            return {"success": True, "message": "Test registration successful!"}
    
    import login
    login.api = MockAPI()

    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())
