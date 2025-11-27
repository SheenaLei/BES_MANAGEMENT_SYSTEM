# gui/views/login_view.py
from PyQt5 import uic, QtWidgets
from pathlib import Path
from app.controllers.auth_controllers import AuthController

UI_PATH = Path(__file__).resolve().parent.parent / "ui" / "login.ui"

class LoginWindow(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi(str(UI_PATH), self)
        # Expected widgets in login.ui: inputUsername, inputPassword, btnLogin, btnRegister
        try:
            self.btnLogin.clicked.connect(self.handle_login)
            self.btnRegister.clicked.connect(self.open_register)
        except Exception:
            pass

    def handle_login(self):
        username = self.inputUsername.text().strip()
        password = self.inputPassword.text().strip()
        if not username or not password:
            QtWidgets.QMessageBox.warning(self, "Error", "Enter username and password")
            return
        res = AuthController.start_login(username, password)
        if not res.get("success"):
            QtWidgets.QMessageBox.warning(self, "Error", res.get("error", "Login failed"))
            return
        # prompt for OTP
        code, ok = QtWidgets.QInputDialog.getText(self, "OTP", "Enter OTP code sent to your email:")
        if not ok:
            return
        verify = AuthController.verify_login_otp(username, code)
        if not verify.get("success"):
            QtWidgets.QMessageBox.warning(self, "Error", verify.get("error", "OTP failed"))
            return
        QtWidgets.QMessageBox.information(self, "Success", "Logged in successfully")
        
        # Open Dashboard
        from gui.views.dashboard_view import DashboardWindow
        self.dashboard = DashboardWindow()
        self.dashboard.show()
        self.close()

    def open_register(self):
        from gui.views.register_view import RegisterDialog
        dlg = RegisterDialog(parent=self)
        dlg.exec_()