# gui/views/register_view.py
from PyQt5 import uic, QtWidgets
from pathlib import Path
from app.controllers.auth_controller import AuthController

UI_PATH = Path(__file__).resolve().parent.parent / "ui" / "register.ui"

class RegisterDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(str(UI_PATH), self)
        # Expected widgets: inputFirstName, inputLastName, inputBirthdate, inputEmail, btnUploadPSA, btnUploadID, btnSubmit
        try:
            self.btnUploadPSA.clicked.connect(self.upload_psa)
            self.btnUploadID.clicked.connect(self.upload_id)
            self.btnSubmit.clicked.connect(self.submit)
        except Exception:
            pass
        self.psa_path = None
        self.id_path = None

    def upload_psa(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select PSA / Birth Certificate", "", "Images (*.png *.jpg *.jpeg *.pdf)")
        if path:
            self.psa_path = path
            self.lblPSAPath.setText(path)

    def upload_id(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select ID", "", "Images (*.png *.jpg *.jpeg *.pdf)")
        if path:
            self.id_path = path
            self.lblIDPath.setText(path)

    def submit(self):
        info = {
            "first_name": self.inputFirstName.text().strip(),
            "middle_name": self.inputMiddleName.text().strip(),
            "last_name": self.inputLastName.text().strip(),
            "birthdate": self.inputBirthdate.text().strip(),  # expecting YYYY-MM-DD
            "gender": self.comboGender.currentText() if hasattr(self, "comboGender") else "Other",
            "email": self.inputEmail.text().strip(),
            "phone_number": self.inputPhone.text().strip(),
        }
        files = []
        if self.psa_path:
            files.append({"path": self.psa_path, "doc_type": "PSA"})
        if self.id_path:
            files.append({"path": self.id_path, "doc_type": "ID", "id_type": self.comboIDType.currentText() if hasattr(self, "comboIDType") else None})
        res = AuthController.register_resident(info, files)
        if res.get("success"):
            QtWidgets.QMessageBox.information(self, "Success", "Registration submitted. Please wait for admin verification.")
            self.accept()
        else:
            QtWidgets.QMessageBox.warning(self, "Error", res.get("error", "Registration failed"))