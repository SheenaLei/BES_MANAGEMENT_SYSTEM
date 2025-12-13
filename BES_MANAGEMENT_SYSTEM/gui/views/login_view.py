# gui/views/login_view.py
from PyQt5 import uic, QtWidgets, QtCore, QtGui
from pathlib import Path
from app.controllers.auth_controllers import AuthController
from gui.widgets.notification_bar import NotificationBar
from gui.window_state import save_window_state, apply_window_state

# Import compiled resources for background images
try:
    from gui.ui.loginUi4 import res_rc
except ImportError:
    pass  # Resources not compiled yet

UI_PATH = Path(__file__).resolve().parent.parent / "ui" / "loginUi3_revised_1.ui"

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

        # Stretch content to fill when maximized (similar to welcome screen)
        self._container = self.findChild(QtWidgets.QWidget, "widget")
        self._bg = self.findChild(QtWidgets.QLabel, "label_5")
        self._overlay = self.findChild(QtWidgets.QLabel, "label_7")
        self._footer = self.findChild(QtWidgets.QLabel, "label_8")
        self._topbar = self.findChild(QtWidgets.QLabel, "label_9")

        # Ensure background scales properly if present
        if self._bg:
            ss = self._bg.styleSheet()
            if "image:" in ss and "border-image:" not in ss:
                self._bg.setStyleSheet(ss.replace("image:", "border-image:"))
            self._bg.setScaledContents(True)

        # Design reference size (fallback if needed)
        self._base_w, self._base_h = 1305, 879

        def _resize_all(event=None):
            # Use full dialog size
            w, h = self.width(), self.height()

            # Container fills window
            if self._container:
                self._container.setGeometry(0, 0, w, h)

            # Background and overlay fill
            if self._bg:
                self._bg.setGeometry(0, 0, w, h)
            if self._overlay:
                self._overlay.setGeometry(0, 0, w, h)

            # Bars stick to edges
            if self._footer and self._footer.height():
                fh = max(30, int(self._footer.height() * (h / self._base_h)))
                self._footer.setGeometry(0, h - fh, w, fh)
            if self._topbar and self._topbar.height():
                th = max(30, int(self._topbar.height() * (h / self._base_h)))
                self._topbar.setGeometry(0, 0, w, th)

            if event:
                QtWidgets.QDialog.resizeEvent(self, event)

        # Hook resize to keep layout responsive
        self.resizeEvent = _resize_all
        QtCore.QTimer.singleShot(0, _resize_all)
        
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
            pass

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
            self.notification.show_info(f"OTP Code: {otp_code}", duration=300000)
        else:
            self.notification.show_info("OTP sent! Check your email or console", duration=300000)
            
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
            
            # Save current window state before closing
            save_window_state(self)
            
            # Check role and open appropriate dashboard
            if account.user_role in ['Admin', 'Staff']:
                # ADMIN DASHBOARD
                from gui.views.sidebar_home_view import SidebarHomeWindow
                self.dashboard = SidebarHomeWindow()
                apply_window_state(self.dashboard)

            else:
                # USER DASHBOARD (Resident)
                from gui.views.sidebar_home_user_view import SidebarHomeUserWindow
                self.dashboard = SidebarHomeUserWindow(username=self.current_username)
                apply_window_state(self.dashboard)

            self.close()
            
        except Exception as e:
            self.notification.show_error(f"Error opening dashboard: {e}")

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
        """Handle forgot password - show reset dialog"""
        from app.db import SessionLocal
        from app.models import Account, OTP, Resident
        from datetime import datetime, timedelta
        import random
        import string
        
        # Create forgot password dialog
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Forgot Password")
        dialog.setFixedSize(400, 300)
        dialog.setStyleSheet("background-color: #f5f5f5;")
        
        layout = QtWidgets.QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 25, 30, 25)
        
        # Title
        title = QtWidgets.QLabel("🔐 Reset Password")
        title.setStyleSheet("font-size: 16pt; font-weight: bold; color: #1976d2;")
        title.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title)
        
        # Instructions
        instructions = QtWidgets.QLabel("Enter your username to receive a password reset code.")
        instructions.setStyleSheet("font-size: 10pt; color: #666;")
        instructions.setWordWrap(True)
        instructions.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(instructions)
        
        # Username input
        username_label = QtWidgets.QLabel("Username:")
        username_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(username_label)
        
        username_input = QtWidgets.QLineEdit()
        username_input.setPlaceholderText("Enter your username")
        username_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 5px;
                font-size: 11pt;
            }
        """)
        layout.addWidget(username_input)
        
        # Buttons
        btn_layout = QtWidgets.QHBoxLayout()
        
        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 25px;
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #7f8c8d; }
        """)
        cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(cancel_btn)
        
        send_btn = QtWidgets.QPushButton("Send Reset Code")
        send_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 25px;
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #2980b9; }
        """)
        btn_layout.addWidget(send_btn)
        
        layout.addLayout(btn_layout)
        
        def send_reset_code():
            username = username_input.text().strip()
            if not username:
                self.notification.show_warning("Please enter your username")
                return
            
            db = SessionLocal()
            try:
                # Find account
                account = db.query(Account).filter(Account.username == username).first()
                if not account:
                    self.notification.show_error("Username not found")
                    return
                
                # Generate 6-digit OTP code
                otp_code = ''.join(random.choices(string.digits, k=6))
                
                # Create OTP record
                otp = OTP(
                    account_id=account.account_id,
                    code=otp_code,
                    purpose='password_reset',
                    expires_at=datetime.now() + timedelta(minutes=10),
                    is_used=False
                )
                db.add(otp)
                db.commit()
                
                # Get resident info for email
                resident = db.query(Resident).filter(Resident.resident_id == account.resident_id).first()
                resident_name = resident.full_name() if resident else username
                
                dialog.accept()
                
                # Show reset code dialog
                self.show_reset_code_dialog(account.account_id, otp_code, resident_name)
                
            except Exception as e:
                db.rollback()
                self.notification.show_error(f"Error: {e}")
            finally:
                db.close()
        
        send_btn.clicked.connect(send_reset_code)
        username_input.returnPressed.connect(send_reset_code)
        
        dialog.exec_()
    
    def show_reset_code_dialog(self, account_id, otp_code, resident_name):
        """Show dialog to enter reset code and new password"""
        from app.db import SessionLocal
        from app.models import Account, OTP
        
        # Create reset dialog
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Reset Password")
        dialog.setFixedSize(500, 580)
        dialog.setStyleSheet("background-color: #f5f5f5;")
        
        layout = QtWidgets.QVBoxLayout(dialog)
        layout.setSpacing(12)
        layout.setContentsMargins(35, 25, 35, 25)
        
        # Title
        title = QtWidgets.QLabel("🔑 Enter Reset Code")
        title.setStyleSheet("font-size: 18pt; font-weight: bold; color: #1976d2;")
        title.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title)
        
        # Show the code (in production, this would be sent via email/SMS)
        code_info = QtWidgets.QLabel(f"Your reset code is:")
        code_info.setStyleSheet("font-size: 12pt; color: #333;")
        code_info.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(code_info)
        
        code_display = QtWidgets.QLabel(otp_code)
        code_display.setStyleSheet("font-size: 28pt; font-weight: bold; color: #27ae60; background-color: #e8f5e9; padding: 15px; border-radius: 8px; letter-spacing: 8px;")
        code_display.setAlignment(QtCore.Qt.AlignCenter)
        code_display.setFixedHeight(70)
        layout.addWidget(code_display)
        
        note = QtWidgets.QLabel("(In production, this would be sent to your email/phone)")
        note.setStyleSheet("font-size: 9pt; color: #888; font-style: italic;")
        note.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(note)
        
        # Code input
        code_label = QtWidgets.QLabel("Enter Code:")
        code_label.setStyleSheet("font-weight: bold; font-size: 11pt;")
        layout.addWidget(code_label)
        
        code_input = QtWidgets.QLineEdit()
        code_input.setPlaceholderText("Enter 6-digit code")
        code_input.setMaxLength(6)
        code_input.setFixedHeight(50)
        code_input.setStyleSheet("""
            QLineEdit {
                padding: 8px 10px;
                border: 2px solid #ccc;
                border-radius: 6px;
                font-size: 14pt;
                letter-spacing: 8px;
            }
        """)
        layout.addWidget(code_input)
        
        # New password input
        password_label = QtWidgets.QLabel("New Password:")
        password_label.setStyleSheet("font-weight: bold; font-size: 11pt;")
        layout.addWidget(password_label)
        
        password_input = QtWidgets.QLineEdit()
        password_input.setPlaceholderText("Enter new password")
        password_input.setEchoMode(QtWidgets.QLineEdit.Password)
        password_input.setFixedHeight(45)
        password_input.setStyleSheet("""
            QLineEdit {
                padding: 8px 10px;
                border: 2px solid #ccc;
                border-radius: 6px;
                font-size: 11pt;
            }
        """)
        layout.addWidget(password_input)
        
        # Confirm password input
        confirm_label = QtWidgets.QLabel("Confirm Password:")
        confirm_label.setStyleSheet("font-weight: bold; font-size: 11pt;")
        layout.addWidget(confirm_label)
        
        confirm_input = QtWidgets.QLineEdit()
        confirm_input.setPlaceholderText("Confirm new password")
        confirm_input.setEchoMode(QtWidgets.QLineEdit.Password)
        confirm_input.setFixedHeight(45)
        confirm_input.setStyleSheet("""
            QLineEdit {
                padding: 8px 10px;
                border: 2px solid #ccc;
                border-radius: 6px;
                font-size: 11pt;
            }
        """)
        layout.addWidget(confirm_input)
        
        # Buttons
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.setSpacing(15)
        
        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.setFixedHeight(42)
        cancel_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 30px;
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 11pt;
            }
            QPushButton:hover { background-color: #7f8c8d; }
        """)
        cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(cancel_btn)
        
        reset_btn = QtWidgets.QPushButton("Reset Password")
        reset_btn.setFixedHeight(42)
        reset_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 30px;
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 11pt;
            }
            QPushButton:hover { background-color: #219a52; }
        """)
        btn_layout.addWidget(reset_btn)
        
        layout.addLayout(btn_layout)
        
        def reset_password():
            code = code_input.text().strip()
            new_password = password_input.text()
            confirm_password = confirm_input.text()
            
            if not code:
                self.notification.show_warning("Please enter the reset code")
                return
            
            if not new_password:
                self.notification.show_warning("Please enter a new password")
                return
            
            if new_password != confirm_password:
                self.notification.show_error("Passwords do not match")
                return
            
            if len(new_password) < 6:
                self.notification.show_warning("Password must be at least 6 characters")
                return
            
            db = SessionLocal()
            try:
                # Verify OTP
                otp = db.query(OTP).filter(
                    OTP.account_id == account_id,
                    OTP.code == code,
                    OTP.purpose == 'password_reset',
                    OTP.is_used == False
                ).first()
                
                if not otp:
                    self.notification.show_error("Invalid or expired reset code")
                    return
                
                if not otp.is_valid():
                    self.notification.show_error("Reset code has expired. Please request a new one.")
                    return
                
                # Mark OTP as used
                otp.is_used = True
                
                # Update password
                account = db.query(Account).filter(Account.account_id == account_id).first()
                if account:
                    account.set_password(new_password)
                    db.commit()
                    
                    self.notification.show_success(f"✅ Password reset successfully for {resident_name}!")
                    dialog.accept()
                else:
                    self.notification.show_error("Account not found")
                    
            except Exception as e:
                db.rollback()
                self.notification.show_error(f"Error: {e}")
            finally:
                db.close()
        
        reset_btn.clicked.connect(reset_password)
        
        dialog.exec_()


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = LoginWindow()
    window.showMaximized()  # Start maximized/fullscreen
    sys.exit(app.exec_())