# gui/run_app.py
import sys
import os
import re
from datetime import datetime
try:
    from zoneinfo import ZoneInfo
except ImportError:  # Python < 3.9 fallback
    ZoneInfo = None
from pathlib import Path

# Suppress Qt font warnings (cosmetic only, doesn't affect functionality)
os.environ["QT_LOGGING_RULES"] = "qt.qpa.fonts=false"

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

from PyQt5 import QtWidgets, QtCore, uic
from gui.views.login_view import LoginWindow
from gui.window_state import save_window_state, apply_window_state

UI_DIR = Path(__file__).resolve().parent / "ui"
WELCOME_UI = UI_DIR / "loginUi3_revised_2.ui"


def main():
    app = QtWidgets.QApplication(sys.argv)

    # Load welcome/landing UI first
    welcome = QtWidgets.QDialog()
    uic.loadUi(str(WELCOME_UI), welcome)
    welcome.setWindowTitle("Barangay E-Services - Welcome")
    welcome.setWindowFlags(QtCore.Qt.Window |
                           QtCore.Qt.WindowMinimizeButtonHint |
                           QtCore.Qt.WindowMaximizeButtonHint |
                           QtCore.Qt.WindowCloseButtonHint)

    # Get the container widget (should now expand due to layout in .ui file)
    container = welcome.findChild(QtWidgets.QWidget, "widget")
    
    # Get all the labels and button
    label_bg = welcome.findChild(QtWidgets.QLabel, "label_5")      # background image
    label_overlay = welcome.findChild(QtWidgets.QLabel, "label_7") # gradient overlay + text
    label_footer = welcome.findChild(QtWidgets.QLabel, "label_8")  # footer bar
    label_topbar = welcome.findChild(QtWidgets.QLabel, "label_9")  # top bar (left)
    label_datetime = welcome.findChild(QtWidgets.QLabel, "label_10")  # top bar (right)
    top_bar_container = welcome.findChild(QtWidgets.QWidget, "top_bar_container")  # top bar container
    btn = welcome.findChild(QtWidgets.QPushButton, "pushButton")

    # Design base size
    base_w, base_h = 1305, 879
    
    # Store original positions/sizes for scaling
    btn_orig = btn.geometry() if btn else None
    footer_orig_h = label_footer.height() if label_footer else 51
    topbar_orig_h = 51  # Same height as footer
    
    # Store original text for overlay
    overlay_orig_text = label_overlay.text() if label_overlay else ""

    def resize_all(event=None):
        # Get the actual size of the container (which fills the window due to layout)
        if container:
            w = container.width()
            h = container.height()
        else:
            w = welcome.width()
            h = welcome.height()
        
        # Calculate scale factors
        scale_x = w / base_w
        scale_y = h / base_h
        
        # 1. Background image - fill entire container
        if label_bg:
            label_bg.setGeometry(0, 0, w, h)
        
        # 2. Gradient overlay - fill entire container
        if label_overlay:
            label_overlay.setGeometry(0, 0, w, h)
            # Scale font sizes in the text
            if overlay_orig_text:
                def scale_font(match):
                    orig_size = int(match.group(1))
                    new_size = max(8, int(orig_size * min(scale_x, scale_y)))
                    return f"font-size:{new_size}pt"
                scaled_text = re.sub(r"font-size:(\d+)pt", scale_font, overlay_orig_text)
                label_overlay.setText(scaled_text)
        
        # 3. Top bar container - full width, scaled height, at top
        if top_bar_container:
            new_h = max(30, int(topbar_orig_h * scale_y))
            top_bar_container.setGeometry(0, 0, w, new_h)
        
        # 4. Footer bar - full width, scaled height, at bottom
        if label_footer:
            new_h = max(30, int(footer_orig_h * scale_y))
            label_footer.setGeometry(0, h - new_h, w, new_h)
        
        # 5. Button - centered horizontally, scaled size and position
        if btn and btn_orig:
            new_bw = max(150, int(btn_orig.width() * scale_x))
            new_bh = max(40, int(btn_orig.height() * scale_y))
            new_bx = (w - new_bw) // 2
            new_by = int(btn_orig.y() * scale_y)
            btn.setGeometry(new_bx, new_by, new_bw, new_bh)
            # Scale font
            font = btn.font()
            font.setPointSize(max(8, int(12 * min(scale_x, scale_y))))
            btn.setFont(font)
        
        if event:
            QtWidgets.QDialog.resizeEvent(welcome, event)

    # Attach resize handler to the container (which expands with window)
    if container:
        container.resizeEvent = resize_all
    else:
        welcome.resizeEvent = resize_all

    # Show maximized and trigger initial resize
    welcome.showMaximized()
    QtCore.QTimer.singleShot(50, resize_all)

    # Live Philippine time updater for the right top bar
    def update_datetime_label():
        if not label_datetime:
            return
        try:
            if ZoneInfo:
                now = datetime.now(ZoneInfo("Asia/Manila"))
            else:
                now = datetime.now()
            label_datetime.setText(now.strftime("%b %d, %Y  %I:%M %p"))
        except Exception:
            # fallback to system time on any error
            label_datetime.setText(datetime.now().strftime("%b %d, %Y  %I:%M %p"))

    update_datetime_label()
    dt_timer = QtCore.QTimer(welcome)
    dt_timer.timeout.connect(update_datetime_label)
    dt_timer.start(1000)

    # Wire the BEGIN JOURNEY button to open the actual login
    def open_login():
        # Save window state from welcome screen
        save_window_state(welcome)
        
        welcome.login_window = LoginWindow()
        apply_window_state(welcome.login_window)
        welcome.close()

    btn = welcome.findChild(QtWidgets.QPushButton, "pushButton")
    if btn:
        btn.clicked.connect(open_login)

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()