# gui/run_app.py
import sys
from PyQt5 import QtWidgets, uic
from pathlib import Path
from gui.views.login_view import LoginWindow

UI_DIR = Path(__file__).resolve().parent / "ui"

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()