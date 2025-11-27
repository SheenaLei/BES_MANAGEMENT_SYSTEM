# gui/run_app.py
import sys
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

from PyQt5 import QtWidgets, uic
from gui.views.login_view import LoginWindow

UI_DIR = Path(__file__).resolve().parent / "ui"

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()