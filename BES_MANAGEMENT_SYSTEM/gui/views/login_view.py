# gui/views/login_view.py
from PyQt5 import uic, QtWidgets, QtCore, QtGui
from pathlib import Path
from app.controllers.auth_controllers import AuthController
from gui.widgets.notification_bar import NotificationBar

# Import compiled resources for background images
try:
    from gui.ui.loginUi4 import res_rc
except ImportError:
    pass  # Resources not compiled yet

UI_PATH = Path(__file__).resolve().parent.parent / "ui" / "loginUi3_revised.ui"

class LoginWindow(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi(str(UI_PATH), self)
        
        # Set window properties - FULLSCREEN CAPABLE
        self.setWindowTitle("Barangay E-Services - Login")
        # Enable minimize, maximize, and close buttons  
        self.setWindowFlags(QtCore.Qt.Window | 
                           QtCore.Qt.WindowMinimizeButtonHint | 
                           QtCore.Qt.WindowMaximizeButtonHint | 
                           QtCore.Qt.WindowCloseButtonHint)
        
        # Create notification bar (Universal)
        self.notification = NotificationBar(self)
        
        # Initialize current_username
        self.current_username = None
        
        # Connect buttons
        try:
            self.pushButton.clicked.connect(self.handle_login)
            self.pushButton_2.clicked.connect(self.open_register)
            if hasattr(self, 'pushButton_3'):
                self.pushButton_3.clicked.connect(self.forgot_password)
            
            # Enable Enter key to login
            self.lineEdit.returnPressed.connect(self.handle_login)
            self.lineEdit_2.returnPressed.connect(self.handle_login)
            
            # Setup password visibility toggle (Eye Icon)
            self.setup_password_visibility()
            
        except Exception as e:
            print(f"Error connecting buttons: {e}")
    
    def setup_password_visibility(self):
        """Add eye icon to password field to toggle visibility"""
        self.password_visible = False
        self.lineEdit_2.setEchoMode(QtWidgets.QLineEdit.Password)
        
        # Create icons programmatically
        self.icon_eye_open = self._create_eye_icon(open_eye=True)
        self.icon_eye_closed = self._create_eye_icon(open_eye=False)
        
        # Initial state: Hidden (Dots) -> Show CLOSED eye icon
        self.toggle_password_action = self.lineEdit_2.addAction(
            self.icon_eye_closed, 
            QtWidgets.QLineEdit.TrailingPosition
        )
        self.toggle_password_action.triggered.connect(self.toggle_password)
    
    def _create_eye_icon(self, open_eye=True):
        """Draw a simple eye icon programmatically"""
        pixmap = QtGui.QPixmap(24, 24)
        pixmap.fill(QtCore.Qt.transparent)
        painter = QtGui.QPainter(pixmap)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        # Set color (dark gray)
        color = QtGui.QColor(80, 80, 80)
        painter.setPen(QtGui.QPen(color, 2))
        
        if open_eye:
            painter.drawEllipse(2, 6, 20, 12)  # Eye outline
            painter.setBrush(color)
            painter.drawEllipse(9, 9, 6, 6)    # Pupil
        else:
            painter.drawEllipse(2, 6, 20, 12)  # Eye outline
            painter.setBrush(color)
            painter.drawEllipse(9, 9, 6, 6)    # Pupil
            pen = QtGui.QPen(color, 3)
            painter.setPen(pen)
            painter.drawLine(4, 20, 20, 4) # Slash
            
        painter.end()
        return QtGui.QIcon(pixmap)

    def toggle_password(self):
        """Toggle password visibility"""
        self.password_visible = not self.password_visible
        
        if self.password_visible:
            self.lineEdit_2.setEchoMode(QtWidgets.QLineEdit.Normal)
            # Visible -> Show OPEN eye
            self.toggle_password_action.setIcon(self.icon_eye_open)
        else:
            self.lineEdit_2.setEchoMode(QtWidgets.QLineEdit.Password)
            # Hidden -> Show CLOSED eye
            self.toggle_password_action.setIcon(self.icon_eye_closed)

    def handle_login(self):
        username = self.lineEdit.text().strip()
        password = self.lineEdit_2.text().strip()
        
        if not username or not password:
            self.notification.show_warning("Please enter both username and password")
            return
        
        # Store username for role-based routing after OTP
        self.current_username = username
        
        # Start login process
        res = AuthController.start_login(username, password)
        
        if not res.get("success"):
            error_msg = res.get("error", "Login failed")
            
            if "not found" in error_msg.lower() or "does not exist" in error_msg.lower():
                self.notification.show_error("Account not found. Please register first!")
            else:
                self.notification.show_error(f"{error_msg}")
            return
        
        # Show OTP prompt
        otp_code = res.get("otp_code")
        if otp_code:
            self.notification.show_info(f"OTP Code: {otp_code}", duration=60000)
        else:
            self.notification.show_info("OTP sent! Check your email or console", duration=60000)
            
        # Force UI to update so notification appears BEFORE the dialog blocks it
        QtWidgets.QApplication.processEvents()

        # Prompt for OTP with Custom Styling
        dialog = QtWidgets.QInputDialog(self)
        dialog.setWindowTitle("Enter OTP")
        dialog.setLabelText("Enter the 6-digit OTP code:")
        dialog.setInputMode(QtWidgets.QInputDialog.TextInput)
        dialog.setTextEchoMode(QtWidgets.QLineEdit.Normal)
        
        # Apply Custom Stylesheet
        dialog.setStyleSheet("""
            QInputDialog {
                background-color: #D6EAF8;
            }
            QLabel {
                color: #2c3e50;
                font-size: 11pt;
                font-weight: bold;
                font-family: 'Segoe UI';
            }
            QLineEdit {
                background-color: white;
                color: black;
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                padding: 8px;
                font-size: 12pt;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
            QPushButton {
                background-color: white;
                color: #2c3e50;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 6px 20px;
                font-size: 10pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ecf0f1;
                border: 1px solid #3498db;
            }
            QPushButton:pressed {
                background-color: #bdc3c7;
            }
        """)
        
        ok = dialog.exec_() == QtWidgets.QDialog.Accepted
        code = dialog.textValue()
        
        if not ok or not code:
            self.notification.show_info("Login cancelled")
            return

        # Verify OTP
        verify = AuthController.verify_login_otp(username, code.strip())
        
        if not verify.get("success"):
            self.notification.show_error(f"{verify.get('error', 'Invalid OTP')}")
            return
        
        # Success!
        self.notification.show_success("Login successful! Welcome back!")
        
        # Wait a moment for user to see the success message, then check role
        QtCore.QTimer.singleShot(1500, self.open_dashboard_by_role)
    
    def open_dashboard_by_role(self):
        """Open appropriate dashboard based on user role"""
        try:
            from app.db import SessionLocal
            from app.models import Account
            
            # Get user's role
            db = SessionLocal()
            account = db.query(Account).filter(Account.username == self.current_username).first()
            db.close()
            
            if not account:
                self.notification.show_error("Account not found!")
                return
            
            # Check role and open appropriate dashboard
            if account.user_role in ['Admin', 'Staff']:
                # ADMIN DASHBOARD
                from gui.views.sidebar_home_view import SidebarHomeWindow
                self.dashboard = SidebarHomeWindow()
                self.dashboard.show()
                print(f"Opening ADMIN dashboard for {account.user_role}: {account.username}")
            else:
                # USER DASHBOARD (Resident)
                from gui.views.sidebar_home_user_view import SidebarHomeUserWindow
                self.dashboard = SidebarHomeUserWindow(username=self.current_username)
                self.dashboard.show()
                print(f"Opening USER dashboard for: {account.username}")
            
            self.close()
            
        except Exception as e:
            self.notification.show_error(f"Error opening dashboard: {e}")
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
    
    def open_register(self):
        """Open registration dialog"""
        from gui.views.register_view import RegisterDialog
        dlg = RegisterDialog(parent=self)
        result = dlg.exec_()
        
        if result == QtWidgets.QDialog.Accepted:
            self.notification.show_success("Account created! Visit the Barangay Hall to complete registration before logging in.")
    
    def forgot_password(self):
        """Handle forgot password"""
        self.notification.show_info("Password recovery feature coming soon!")


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = LoginWindow()
    window.showMaximized()  # Start maximized/fullscreen
    sys.exit(app.exec_())