"""
Login Window
PyQt5 login dialog with responsive layout for Windows high-DPI screens.
"""
import sys
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QSpacerItem, QSizePolicy, QApplication
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor

from api import api


class LoginWindow(QWidget):
    """Responsive login window with centered card layout."""

    login_successful = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._setup_window()
        self._build_ui()
        self._apply_styles()

    def _setup_window(self):
        """Configure window properties."""
        self.setWindowTitle("Chemical Equipment Visualizer - Login")
        self.setMinimumSize(400, 500)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def _build_ui(self):
        """Build the UI with proper layouts."""
        # Root layout
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)

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
        card_layout.setContentsMargins(36, 44, 36, 44)
        card_layout.setSpacing(0)

        # Logo
        self.logo = QLabel("🧪")
        self.logo.setAlignment(Qt.AlignCenter)
        self.logo.setFont(QFont("Segoe UI Emoji", 36))
        card_layout.addWidget(self.logo)

        card_layout.addSpacing(12)

        # Title
        self.title = QLabel("Chemical Equipment\nVisualizer")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setObjectName("titleLabel")
        self.title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        card_layout.addWidget(self.title)

        card_layout.addSpacing(32)

        # Form layout for inputs
        form = QFormLayout()
        form.setContentsMargins(0, 0, 0, 0)
        form.setSpacing(8)
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
        form.addItem(QSpacerItem(1, 16, QSizePolicy.Minimum, QSizePolicy.Fixed))

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

        card_layout.addLayout(form)

        card_layout.addSpacing(28)

        # Login button
        self.login_btn = QPushButton("Sign In")
        self.login_btn.setObjectName("loginBtn")
        self.login_btn.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.login_btn.setCursor(Qt.PointingHandCursor)
        self.login_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.login_btn.clicked.connect(self._handle_login)
        card_layout.addWidget(self.login_btn)

        card_layout.addSpacing(16)

        # Error label
        self.error_label = QLabel("")
        self.error_label.setObjectName("errorLabel")
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setWordWrap(True)
        self.error_label.setFont(QFont("Segoe UI", 9))
        self.error_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        card_layout.addWidget(self.error_label)

        # Add card to horizontal center layout
        center_h.addWidget(self.card)
        center_h.addSpacerItem(QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum))

        root.addLayout(center_h)

        # Bottom spacer for vertical centering
        root.addSpacerItem(QSpacerItem(1, 1, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Keyboard navigation
        self.username_input.returnPressed.connect(lambda: self.password_input.setFocus())
        self.password_input.returnPressed.connect(self._handle_login)

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
            #errorLabel {
                color: #e53935;
                min-height: 16px;
            }
        """)

    def _handle_login(self):
        """Process login request."""
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if not username:
            self._show_error("Please enter your username")
            self.username_input.setFocus()
            return

        if not password:
            self._show_error("Please enter your password")
            self.password_input.setFocus()
            return

        self.login_btn.setEnabled(False)
        self.login_btn.setText("Signing in...")
        self.error_label.clear()

        QApplication.processEvents()

        result = api.login(username, password)

        self.login_btn.setEnabled(True)
        self.login_btn.setText("Sign In")

        if result["success"]:
            self.login_successful.emit()
        else:
            self._show_error(result["message"])

    def _show_error(self, msg: str):
        """Display error message."""
        self.error_label.setText(msg)


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
    
    import login
    login.api = MockAPI()

    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())
