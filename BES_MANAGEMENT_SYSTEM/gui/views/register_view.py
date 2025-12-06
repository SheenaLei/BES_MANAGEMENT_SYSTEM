# gui/views/register_view.py
from PyQt5 import uic, QtWidgets, QtCore, QtGui
from pathlib import Path
from app.controllers.auth_controllers import AuthController
from gui.widgets.notification_bar import NotificationBar
from app.db import SessionLocal
from app.models import Resident, Account

UI_PATH = Path(__file__).resolve().parent.parent / "ui" / "loginUi4_sign_in.ui"

class RegisterDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(str(UI_PATH), self)
        
        # Set window properties
        self.setWindowTitle("Barangay E-Services - Register")
        
        # Create notification bar (using universal widget)
        self.notification = NotificationBar(self)
        
        # Widget mapping from loginUi4_sign_in.ui:
        # lineEdit = Last Name
        # lineEdit_6 = First Name
        # lineEdit_5 = Middle Name
        # lineEdit_2 = Suffix
        # lineEdit_7 = Username
        # lineEdit_9 = Password
        # lineEdit_10 = Confirm Password
        # pushButton = Register button
        # pushButton_2 = "Already have an account?" button
        
        # Connect buttons
        try:
            self.pushButton.clicked.connect(self.handle_register)
            self.pushButton_2.clicked.connect(self.back_to_login)
            
            # Setup password visibility toggles
            self.setup_password_visibility()
            
        except Exception as e:

    def setup_password_visibility(self):
        """Add eye icon to password fields to toggle visibility"""
        # Create icons
        self.icon_eye_open = self._create_eye_icon(open_eye=True)
        self.icon_eye_closed = self._create_eye_icon(open_eye=False)
        
        # Password field (lineEdit_9)
        self.password_visible = False
        self.lineEdit_9.setEchoMode(QtWidgets.QLineEdit.Password)
        self.toggle_password_action = self.lineEdit_9.addAction(
            self.icon_eye_closed,
            QtWidgets.QLineEdit.TrailingPosition
        )
        self.toggle_password_action.triggered.connect(self.toggle_password)
        
        # Confirm Password field (lineEdit_10)
        self.confirm_password_visible = False
        self.lineEdit_10.setEchoMode(QtWidgets.QLineEdit.Password)
        self.toggle_confirm_password_action = self.lineEdit_10.addAction(
            self.icon_eye_closed,
            QtWidgets.QLineEdit.TrailingPosition
        )
        self.toggle_confirm_password_action.triggered.connect(self.toggle_confirm_password)
    
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
            painter.drawLine(4, 20, 20, 4)     # Slash
            
        painter.end()
        return QtGui.QIcon(pixmap)
    
    def toggle_password(self):
        """Toggle password visibility"""
        self.password_visible = not self.password_visible
        
        if self.password_visible:
            self.lineEdit_9.setEchoMode(QtWidgets.QLineEdit.Normal)
            self.toggle_password_action.setIcon(self.icon_eye_open)
        else:
            self.lineEdit_9.setEchoMode(QtWidgets.QLineEdit.Password)
            self.toggle_password_action.setIcon(self.icon_eye_closed)
    
    def toggle_confirm_password(self):
        """Toggle confirm password visibility"""
        self.confirm_password_visible = not self.confirm_password_visible
        
        if self.confirm_password_visible:
            self.lineEdit_10.setEchoMode(QtWidgets.QLineEdit.Normal)
            self.toggle_confirm_password_action.setIcon(self.icon_eye_open)
        else:
            self.lineEdit_10.setEchoMode(QtWidgets.QLineEdit.Password)
            self.toggle_confirm_password_action.setIcon(self.icon_eye_closed)
    
    def validate_resident_exists(self, first_name, last_name, middle_name=None):
        """
        Validate that the person is registered as a resident in the barangay.
        Returns (is_valid, resident_id, message)
        """
        db = SessionLocal()
        try:
            # Search for matching resident
            query = db.query(Resident).filter(
                Resident.first_name == first_name,
                Resident.last_name == last_name
            )
            
            # Add middle name filter if provided
            if middle_name:
                query = query.filter(Resident.middle_name == middle_name)
            
            residents = query.all()
            
            if not residents:
                return (
                    False, 
                    None, 
                    "You must be registered at the Barangay Hall first before creating an account. "
                    "Please visit the Barangay Hall to register as a resident."
                )
            
            # If multiple matches, use the first one or ask user to visit barangay
            if len(residents) > 1:
                return (
                    False,
                    None,
                    "Multiple residents found with this name. Please visit the Barangay Hall "
                    "to verify your identity and complete account creation."
                )
            
            # Valid - exactly one resident found (allow multiple accounts per resident)
            return (True, residents[0].resident_id, "Resident verified!")
            
        except Exception as e:

            return (False, None, f"Error validating resident: {str(e)}")
        finally:
            db.close()
    
    def handle_register(self):
        """Handle registration form submission"""
        # Get form data
        last_name = self.lineEdit.text().strip()
        first_name = self.lineEdit_6.text().strip()
        middle_name = self.lineEdit_5.text().strip() or None
        suffix = self.lineEdit_2.text().strip()
        username = self.lineEdit_7.text().strip()
        password = self.lineEdit_9.text().strip()
        confirm_password = self.lineEdit_10.text().strip()
        
        # Validation
        if not all([last_name, first_name, username, password, confirm_password]):
            self.notification.show_warning("Please fill in all required fields")
            return
        
        if len(username) < 4:
            self.notification.show_warning("Username must be at least 4 characters")
            return
        
        if len(password) < 8:
            self.notification.show_warning("Password must be at least 8 characters")
            return
        
        if password != confirm_password:
            self.notification.show_error("Passwords do not match!")
            return
        
        # Show processing notification
        self.notification.show_info("Validating resident information...")
        QtWidgets.QApplication.processEvents()
        
        # VALIDATE RESIDENT EXISTS IN DATABASE
        is_valid, resident_id, message = self.validate_resident_exists(
            first_name, last_name, middle_name
        )
        
        if not is_valid:
            self.notification.show_error(f"{message}")
            return
        
        # Resident validated - proceed with account creation
        self.notification.show_info("Creating your account...")
        QtWidgets.QApplication.processEvents()
        
        # Create account linked to existing resident
        db = SessionLocal()
        try:
            # Create account with PENDING status
            account = Account(
                resident_id=resident_id,
                username=username,
                user_role='Resident',
                account_status='Active'  # Immediately active since they're already registered
            )
            account.set_password(password)
            db.add(account)
            db.commit()
            
            # Success
            self.notification.show_success(
                "Account created successfully! You can now login with your username and password."
            )
            
            # Wait for user to read notification
            QtCore.QTimer.singleShot(3000, lambda: self.accept())
            
        except Exception as e:
            db.rollback()
            error_msg = str(e)
            
            # Check for specific errors
            if "duplicate" in error_msg.lower() or "unique" in error_msg.lower():
                self.notification.show_error("Username already taken. Please choose another.")
            else:
                self.notification.show_error(f"Error creating account: {error_msg}")
        finally:
            db.close()
    
    def back_to_login(self):
        """Close registration dialog and return to login"""
        self.reject()
    
    def clear_form(self):
        """Clear all form fields"""
        self.lineEdit.clear()
        self.lineEdit_6.clear()
        self.lineEdit_5.clear()
        self.lineEdit_2.clear()
        self.lineEdit_7.clear()
        self.lineEdit_9.clear()
        self.lineEdit_10.clear()


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    dialog = RegisterDialog()
    dialog.show()
    sys.exit(app.exec_())