# gui/views/dashboard_view.py
from PyQt5 import uic, QtWidgets
from pathlib import Path

UI_PATH = Path(__file__).resolve().parent.parent / "ui" / "dashboard.ui"

class DashboardWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(str(UI_PATH), self)
        # Wire up widgets (example: btnServices, btnAnnouncements)
        try:
            self.btnServices.clicked.connect(self.show_services)
            self.btnAnnouncements.clicked.connect(self.show_announcements)
        except Exception:
            pass

    def show_services(self):
        QtWidgets.QMessageBox.information(self, "Services", "Show services list (to be implemented)")

    def show_announcements(self):
        QtWidgets.QMessageBox.information(self, "Announcements", "Show announcements (to be implemented)")