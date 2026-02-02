"""
Chemical Equipment Visualizer - Desktop Application
Entry point with authentication flow.
"""
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

from login import LoginWindow
from dashboard import DashboardWindow


# Enable high DPI scaling BEFORE creating QApplication
if hasattr(Qt, 'AA_EnableHighDpiScaling'):
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)


class Application:
    """Main application controller managing windows and auth flow."""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setStyle("Fusion")
        
        self.login_window = None
        self.dashboard_window = None
    
    def show_login(self):
        """Show the login window."""
        # Close dashboard if open
        if self.dashboard_window:
            self.dashboard_window.close()
            self.dashboard_window = None
        
        # Create and show login window
        self.login_window = LoginWindow()
        self.login_window.login_successful.connect(self.on_login_success)
        self.login_window.show()
    
    def on_login_success(self):
        """Handle successful login."""
        # Close login window
        if self.login_window:
            self.login_window.close()
            self.login_window = None
        
        # Create and show dashboard
        self.dashboard_window = DashboardWindow()
        self.dashboard_window.logout_requested.connect(self.on_logout)
        self.dashboard_window.show()
    
    def on_logout(self):
        """Handle logout request."""
        self.show_login()
    
    def run(self):
        """Start the application."""
        self.show_login()
        return self.app.exec_()


if __name__ == "__main__":
    app = Application()
    sys.exit(app.run())
