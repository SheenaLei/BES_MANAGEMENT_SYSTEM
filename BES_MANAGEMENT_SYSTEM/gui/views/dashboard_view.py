# gui/views/dashboard_view.py
from PyQt5 import uic, QtWidgets, QtCore
from pathlib import Path

UI_PATH = Path(__file__).resolve().parent.parent / "ui" / "dashboard.ui"

class DashboardWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(str(UI_PATH), self)
        # Ensure the dashboard always opens as a full window with system controls
        self.setWindowTitle("Dashboard — Barangay E-Services")
        self.setWindowFlags(
            QtCore.Qt.Window |
            QtCore.Qt.WindowMinimizeButtonHint |
            QtCore.Qt.WindowMaximizeButtonHint |
            QtCore.Qt.WindowCloseButtonHint
        )
        # Show maximized by default
        self.showMaximized()
        # Allow central widget to expand fully
        if self.centralWidget():
            self.centralWidget().setMinimumSize(0, 0)
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