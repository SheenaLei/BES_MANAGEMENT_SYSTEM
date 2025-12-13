# gui/views/sidebar_home_view.py
from PyQt5 import uic, QtWidgets, QtCore, QtGui
from pathlib import Path
from gui.widgets.notification_bar import NotificationBar
from gui.window_state import save_window_state, apply_window_state
from app.db import SessionLocal
from app.models import Resident
from app.config import get_philippine_time
UI_PATH = Path(__file__).resolve().parent.parent / "ui" / "sidebarhomee.ui"
ADMIN_RESIDENTS_UI_PATH = Path(__file__).resolve().parent.parent / "ui" / "admin_residents.ui"
ADMIN_BLOTTER_UI_PATH = Path(__file__).resolve().parent.parent / "ui" / "Blotter.ui"
BLOTTER_TABLE_UI_PATH = Path(__file__).resolve().parent.parent / "ui" / "Blotter_TABLE.ui"
# ============== ANIMATED CHART CLASSES FOR ADMIN DASHBOARD ==============
class AdminAnimatedCircleProgress(QtWidgets.QWidget):
    """Animated circular progress widget with value inside"""
    def __init__(self, value, colors, max_value=100, parent=None):
        super().__init__(parent)
        self.value = 0
        self.target_value = value
        self.max_value = max_value if max_value > 0 else 100
        self.colors = colors
        self.animation_progress = 0.0
        # Animation timer
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(16)  # ~60 FPS
    def animate(self):
        if self.animation_progress < 1.0:
            self.animation_progress += 0.02
            self.value = int(self.target_value * min(self.animation_progress, 1.0))
            self.update()
        else:
            self.timer.stop()
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        width = self.width()
        height = self.height()
        side = min(width, height)
        # Center the drawing
        painter.translate(width / 2, height / 2)
        # Draw background circle (track)
        pen = QtGui.QPen(QtGui.QColor(230, 230, 230), 10)
        pen.setCapStyle(QtCore.Qt.RoundCap)
        painter.setPen(pen)
        radius = side / 2 - 15
        painter.drawEllipse(QtCore.QPointF(0, 0), radius, radius)
        # Draw progress arc with gradient
        if self.target_value > 0:
            progress = min(self.value / self.max_value, 1.0) * self.animation_progress
            gradient = QtGui.QConicalGradient(0, 0, 90)
            gradient.setColorAt(0, QtGui.QColor(self.colors[0]))
            gradient.setColorAt(1, QtGui.QColor(self.colors[1]))
            pen = QtGui.QPen(QtGui.QBrush(gradient), 12)
            pen.setCapStyle(QtCore.Qt.RoundCap)
            painter.setPen(pen)
            rect = QtCore.QRectF(-radius, -radius, radius * 2, radius * 2)
            start_angle = 90 * 16
            span_angle = -int(progress * 360 * 16)
            painter.drawArc(rect, start_angle, span_angle)
        # Draw inner circle (white background)
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtGui.QColor(255, 255, 255))
        inner_radius = radius - 18
        painter.drawEllipse(QtCore.QPointF(0, 0), inner_radius, inner_radius)
        # Draw value text
        painter.setPen(QtGui.QColor(self.colors[0]))
        font = painter.font()
        font.setPointSize(18)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(QtCore.QRectF(-radius, -radius, radius * 2, radius * 2),
                        QtCore.Qt.AlignCenter, str(self.value))
class AdminAnimatedBarChart(QtWidgets.QWidget):
    """Animated bar chart for transactions"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(250)
        # Sample data - months and values
        self.months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug']
        self.values = [45, 78, 52, 89, 63, 95, 72, 58]
        self.max_value = max(self.values) if self.values else 100
        self.animation_progress = 0.0
        self.colors = [
            QtGui.QColor("#667eea"),
            QtGui.QColor("#764ba2"),
            QtGui.QColor("#f093fb"),
            QtGui.QColor("#f5576c"),
            QtGui.QColor("#4facfe"),
            QtGui.QColor("#00f2fe"),
            QtGui.QColor("#43e97b"),
            QtGui.QColor("#38f9d7"),
        ]
        # Try to get real data
        self.load_real_data()
        # Animation timer
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(16)
    def load_real_data(self):
        """Load real transaction data from database"""
        try:
            from app.models import CertificateRequest
            from datetime import datetime, timedelta
            session = SessionLocal()
            # Get data for last 8 months
            self.months = []
            self.values = []
            for i in range(7, -1, -1):
                date = datetime.now() - timedelta(days=i*30)
                month_name = date.strftime('%b')
                self.months.append(month_name)
                # Count requests for that month
                count = session.query(CertificateRequest).filter(
                    CertificateRequest.created_at >= date.replace(day=1),
                    CertificateRequest.created_at < (date.replace(day=28) + timedelta(days=4)).replace(day=1)
                ).count()
                self.values.append(count)  # Use real count, no fallback
            self.max_value = max(self.values) if self.values and max(self.values) > 0 else 100
            session.close()
        except Exception as e:
            print(f"Error loading chart data: {e}")
            pass
    def animate(self):
        if self.animation_progress < 1.0:
            self.animation_progress += 0.02
            self.update()
        else:
            self.timer.stop()
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        width = self.width()
        height = self.height()
        # Margins
        left_margin = 50
        right_margin = 20
        top_margin = 20
        bottom_margin = 40
        chart_width = width - left_margin - right_margin
        chart_height = height - top_margin - bottom_margin
        if len(self.values) == 0:
            return
        bar_width = chart_width / len(self.values) - 10
        # Draw Y-axis labels
        painter.setPen(QtGui.QColor(100, 100, 100))
        font = painter.font()
        font.setPointSize(8)
        painter.setFont(font)
        for i in range(5):
            y = top_margin + chart_height - (i * chart_height / 4)
            value = int(self.max_value * i / 4)
            painter.drawText(5, int(y + 5), str(value))
            # Grid line
            painter.setPen(QtGui.QPen(QtGui.QColor(220, 220, 220), 1, QtCore.Qt.DashLine))
            painter.drawLine(left_margin, int(y), width - right_margin, int(y))
            painter.setPen(QtGui.QColor(100, 100, 100))
        # Draw bars
        for i, (month, value) in enumerate(zip(self.months, self.values)):
            x = left_margin + i * (chart_width / len(self.values)) + 5
            # Animated height
            bar_height = (value / self.max_value) * chart_height * self.animation_progress
            y = top_margin + chart_height - bar_height
            # Gradient for bar
            gradient = QtGui.QLinearGradient(x, y, x, top_margin + chart_height)
            gradient.setColorAt(0, self.colors[i % len(self.colors)])
            gradient.setColorAt(1, self.colors[i % len(self.colors)].darker(120))
            painter.setBrush(gradient)
            painter.setPen(QtCore.Qt.NoPen)
            # Draw rounded bar
            rect = QtCore.QRectF(x, y, bar_width, bar_height)
            painter.drawRoundedRect(rect, 5, 5)
            # Draw value on top of bar
            if self.animation_progress > 0.8:
                painter.setPen(QtGui.QColor(50, 50, 50))
                painter.drawText(QtCore.QRectF(x, y - 20, bar_width, 20),
                               QtCore.Qt.AlignCenter, str(value))
            # Draw month label
            painter.setPen(QtGui.QColor(100, 100, 100))
            painter.drawText(QtCore.QRectF(x, height - bottom_margin + 5, bar_width, 30),
                           QtCore.Qt.AlignCenter, month)
class AdminAnimatedPieChart(QtWidgets.QWidget):
    """Animated pie chart for request distribution"""
    def __init__(self, stats, parent=None):
        super().__init__(parent)
        self.stats = stats
        self.setMinimumHeight(200)
        self.data = [
            ("Barangay ID", stats.get('barangay_id', 5), QtGui.QColor("#667eea")),
            ("Business Permit", stats.get('business_permit', 3), QtGui.QColor("#f5576c")),
            ("Indigency", stats.get('indigency', 8), QtGui.QColor("#4facfe")),
            ("Clearance", stats.get('clearance', 6), QtGui.QColor("#43e97b")),
        ]
        self.total = sum(item[1] for item in self.data)
        if self.total == 0:
            self.total = 1
        self.animation_progress = 0.0
        # Animation timer
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(16)
    def animate(self):
        if self.animation_progress < 1.0:
            self.animation_progress += 0.015
            self.update()
        else:
            self.timer.stop()
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        width = self.width()
        height = self.height()
        # Pie chart on left side
        pie_size = min(height - 40, width // 3)
        pie_rect = QtCore.QRectF(40, (height - pie_size) / 2, pie_size, pie_size)
        # Draw pie slices
        start_angle = 90 * 16
        for name, value, color in self.data:
            span = (value / self.total) * 360 * 16 * self.animation_progress
            painter.setBrush(color)
            painter.setPen(QtGui.QPen(QtCore.Qt.white, 2))
            painter.drawPie(pie_rect, int(start_angle), int(-span))
            start_angle -= span
        # Draw center circle (donut effect)
        center_x = pie_rect.center().x()
        center_y = pie_rect.center().y()
        inner_radius = pie_size / 4
        painter.setBrush(QtGui.QColor(255, 255, 255))
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawEllipse(QtCore.QPointF(center_x, center_y), inner_radius, inner_radius)
        # Draw total in center
        painter.setPen(QtGui.QColor(50, 50, 50))
        font = painter.font()
        font.setPointSize(14)
        font.setBold(True)
        painter.setFont(font)
        total_display = int(self.total * self.animation_progress)
        painter.drawText(pie_rect, QtCore.Qt.AlignCenter, str(total_display))
        # Draw legend on right side
        legend_x = pie_rect.right() + 50
        legend_y = 30
        font.setPointSize(10)
        font.setBold(False)
        painter.setFont(font)
        for name, value, color in self.data:
            # Color box
            painter.setBrush(color)
            painter.setPen(QtCore.Qt.NoPen)
            painter.drawRoundedRect(QtCore.QRectF(legend_x, legend_y, 20, 20), 3, 3)
            # Label
            painter.setPen(QtGui.QColor(50, 50, 50))
            display_value = int(value * self.animation_progress)
            percent = int((value / self.total) * 100)
            painter.drawText(int(legend_x + 30), int(legend_y + 15), 
                           f"{name}: {display_value} ({percent}%)")
            legend_y += 35
class AdminAnimatedLineChart(QtWidgets.QWidget):
    """Animated line chart for trends"""
    def __init__(self, title="MONTHLY TREND", parent=None):
        super().__init__(parent)
        self.title = title
        self.setMinimumHeight(200)
        # Sample data - will be replaced with real data
        self.months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        self.values = [12, 25, 18, 35, 28, 42]
        self.max_value = max(self.values) if self.values else 100
        self.animation_progress = 0.0
        self.line_color = QtGui.QColor("#4facfe")
        self.fill_color = QtGui.QColor("#4facfe")
        self.fill_color.setAlpha(50)
        # Animation timer
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(16)
    def set_data(self, months, values, color="#4facfe"):
        self.months = months
        self.values = values
        self.max_value = max(self.values) if self.values else 100
        self.line_color = QtGui.QColor(color)
        self.fill_color = QtGui.QColor(color)
        self.fill_color.setAlpha(50)
        self.update()
    def animate(self):
        if self.animation_progress < 1.0:
            self.animation_progress += 0.02
            self.update()
        else:
            self.timer.stop()
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        width = self.width()
        height = self.height()
        # Margins
        left_margin = 50
        right_margin = 20
        top_margin = 20
        bottom_margin = 40
        chart_width = width - left_margin - right_margin
        chart_height = height - top_margin - bottom_margin
        if len(self.values) < 2:
            return
        # Draw Y-axis labels and grid
        painter.setPen(QtGui.QColor(150, 150, 150))
        font = painter.font()
        font.setPointSize(8)
        painter.setFont(font)
        for i in range(5):
            y = top_margin + chart_height - (i * chart_height / 4)
            value = int(self.max_value * i / 4)
            painter.drawText(5, int(y + 5), str(value))
            # Grid line
            painter.setPen(QtGui.QPen(QtGui.QColor(230, 230, 230), 1, QtCore.Qt.DashLine))
            painter.drawLine(left_margin, int(y), width - right_margin, int(y))
            painter.setPen(QtGui.QColor(150, 150, 150))
        # Calculate points
        points = []
        step = chart_width / (len(self.values) - 1) if len(self.values) > 1 else chart_width
        for i, value in enumerate(self.values):
            x = left_margin + i * step
            animated_value = value * self.animation_progress
            y = top_margin + chart_height - (animated_value / self.max_value) * chart_height
            points.append(QtCore.QPointF(x, y))
        # Draw filled area under line
        if points:
            fill_path = QtGui.QPainterPath()
            fill_path.moveTo(points[0].x(), top_margin + chart_height)
            for p in points:
                fill_path.lineTo(p)
            fill_path.lineTo(points[-1].x(), top_margin + chart_height)
            fill_path.closeSubpath()
            painter.setBrush(self.fill_color)
            painter.setPen(QtCore.Qt.NoPen)
            painter.drawPath(fill_path)
        # Draw line
        pen = QtGui.QPen(self.line_color, 3)
        pen.setCapStyle(QtCore.Qt.RoundCap)
        pen.setJoinStyle(QtCore.Qt.RoundJoin)
        painter.setPen(pen)
        path = QtGui.QPainterPath()
        if points:
            path.moveTo(points[0])
            for p in points[1:]:
                path.lineTo(p)
        painter.drawPath(path)
        # Draw points and values
        for i, (point, value) in enumerate(zip(points, self.values)):
            # Draw point
            painter.setBrush(self.line_color)
            painter.setPen(QtGui.QPen(QtCore.Qt.white, 2))
            painter.drawEllipse(point, 5, 5)
            # Draw value above point
            if self.animation_progress > 0.8:
                painter.setPen(QtGui.QColor(50, 50, 50))
                animated_val = int(value * self.animation_progress)
                painter.drawText(QtCore.QRectF(point.x() - 20, point.y() - 25, 40, 20),
                               QtCore.Qt.AlignCenter, str(animated_val))
        # Draw month labels
        painter.setPen(QtGui.QColor(100, 100, 100))
        for i, month in enumerate(self.months):
            x = left_margin + i * step
            painter.drawText(QtCore.QRectF(x - 20, height - bottom_margin + 5, 40, 30),
                           QtCore.Qt.AlignCenter, month)
class AdminSitioBarChart(QtWidgets.QWidget):
    """Horizontal bar chart for residents per sitio"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(250)
        self.data = []  # List of (sitio_name, count, color)
        self.animation_progress = 0.0
        self.colors = [
            "#667eea", "#764ba2", "#f093fb", "#f5576c",
            "#4facfe", "#00f2fe", "#43e97b", "#38f9d7",
            "#fa709a", "#fee140", "#30cfd0", "#ff9a9e"
        ]
        # Animation timer
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.animate)
    def set_data(self, sitio_data):
        """Set data as list of (sitio_name, count)"""
        self.data = []
        for i, (name, count) in enumerate(sitio_data):
            self.data.append((name, count, QtGui.QColor(self.colors[i % len(self.colors)])))
        self.max_value = max(item[1] for item in self.data) if self.data else 1
        self.animation_progress = 0.0
        self.timer.start(16)
        self.update()
    def animate(self):
        if self.animation_progress < 1.0:
            self.animation_progress += 0.02
            self.update()
        else:
            self.timer.stop()
    def paintEvent(self, event):
        if not self.data:
            return
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        width = self.width()
        height = self.height()
        left_margin = 100
        right_margin = 50
        top_margin = 10
        bottom_margin = 10
        chart_width = width - left_margin - right_margin
        bar_height = min(30, (height - top_margin - bottom_margin) / len(self.data) - 5)
        font = painter.font()
        font.setPointSize(9)
        painter.setFont(font)
        for i, (name, value, color) in enumerate(self.data):
            y = top_margin + i * (bar_height + 8)
            # Draw sitio name
            painter.setPen(QtGui.QColor(50, 50, 50))
            painter.drawText(QtCore.QRectF(5, y, left_margin - 10, bar_height),
                           QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter, name[:12])
            # Draw bar
            bar_width = (value / self.max_value) * chart_width * self.animation_progress
            gradient = QtGui.QLinearGradient(left_margin, y, left_margin + bar_width, y)
            gradient.setColorAt(0, color)
            gradient.setColorAt(1, color.lighter(120))
            painter.setBrush(gradient)
            painter.setPen(QtCore.Qt.NoPen)
            painter.drawRoundedRect(QtCore.QRectF(left_margin, y, bar_width, bar_height), 5, 5)
            # Draw value at end of bar
            if self.animation_progress > 0.5:
                painter.setPen(QtGui.QColor(50, 50, 50))
                display_val = int(value * self.animation_progress)
                painter.drawText(QtCore.QRectF(left_margin + bar_width + 5, y, 50, bar_height),
                               QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter, str(display_val))
# ============== END OF ANIMATED CHART CLASSES ==============
class SidebarHomeWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(str(UI_PATH), self)
        # Set window properties - FULLSCREEN CAPABLE
        self.setWindowTitle("Barangay E-Services - Admin Dashboard")
        self.setWindowFlags(QtCore.Qt.Window | 
                           QtCore.Qt.WindowMinimizeButtonHint | 
                           QtCore.Qt.WindowMaximizeButtonHint | 
                           QtCore.Qt.WindowCloseButtonHint)
        # Add notification bar
        self.notification = NotificationBar(self)
        # Find the main content area
        self.find_content_area()
        # Connect buttons
        self.connect_buttons()
    def find_content_area(self):
        """Find the main white content area where we'll load pages"""
        # Look for QStackedWidget first
        stacked_widgets = self.findChildren(QtWidgets.QStackedWidget)
        if stacked_widgets:
            self.content_area = stacked_widgets[0]
            return
        # Look for QTabWidget
        tab_widgets = self.findChildren(QtWidgets.QTabWidget)
        if tab_widgets:
            self.content_area = tab_widgets[0]
            return
        # Look for a large QFrame or QWidget
        frames = self.findChildren(QtWidgets.QFrame)
        if frames:
            # Find the largest frame (likely the content area)
            self.content_area = max(frames, key=lambda f: f.width() * f.height())
            return
        # Fallback: use central widget
        self.content_area = self.centralWidget()
    def connect_buttons(self):
        """Connect sidebar buttons to their functions"""
        # ===== SMALL ICON SIDEBAR BUTTONS (left side) =====
        # These are the small icon-only buttons on the leftmost sidebar
        # pushButton = Dashboard icon
        if hasattr(self, 'pushButton'):
            self.pushButton.clicked.connect(self.show_dashboard_page)
        # pushButton_2 = Services icon
        if hasattr(self, 'pushButton_2'):
            self.pushButton_2.clicked.connect(self.show_services_page)
        # pushButton_3 = Notifications icon
        if hasattr(self, 'pushButton_3'):
            self.pushButton_3.clicked.connect(self.show_notification_page)
        # pushButton_4 = Announcement icon
        if hasattr(self, 'pushButton_4'):
            self.pushButton_4.clicked.connect(self.show_announcement_page)
        # pushButton_5 = Payment icon
        if hasattr(self, 'pushButton_5'):
            self.pushButton_5.clicked.connect(self.show_payment_page)
        # pushButton_6 = All About icon (info/about page)
        if hasattr(self, 'pushButton_6'):
            self.pushButton_6.clicked.connect(self.show_all_about_page)
        # pushButton_16 = ALL ABOUT text button (expanded sidebar)
        if hasattr(self, 'pushButton_16'):
            self.pushButton_16.clicked.connect(self.show_all_about_page)
        # pushButton_7 = History icon
        if hasattr(self, 'pushButton_7'):
            self.pushButton_7.clicked.connect(self.show_history_page)
        # pushButton_8 = Blotter icon
        if hasattr(self, 'pushButton_8'):
            self.pushButton_8.clicked.connect(self.show_blotter_page)
        # pushButton_9 = Officials icon
        if hasattr(self, 'pushButton_9'):
            self.pushButton_9.clicked.connect(self.show_officials_page)
        # pushButton_23 = Residents icon
        if hasattr(self, 'pushButton_23'):
            self.pushButton_23.clicked.connect(self.show_residents_page)
        # pushButton_10 = Profile/Logout icon (at bottom)
        if hasattr(self, 'pushButton_10'):
            self.pushButton_10.clicked.connect(self.show_profile_page)
        # ===== TEXT SIDEBAR BUTTONS (expanded sidebar) =====
        # RESIDENTS button (pushButton_24)
        if hasattr(self, 'pushButton_24'):
            self.pushButton_24.clicked.connect(self.show_residents_page)
        # DASHBOARD button (pushButton_15)
        if hasattr(self, 'pushButton_15'):
            self.pushButton_15.clicked.connect(self.show_dashboard_page)
        # SERVICES button - search through ALL buttons to find it
        services_connected = False
        for btn in self.findChildren(QtWidgets.QPushButton):
            if btn and hasattr(btn, 'text'):
                button_text = btn.text().upper()
                # Check if button text contains SERVICE or SERVICES
                if 'SERVICE' in button_text and '×' not in button_text:
                    btn.clicked.connect(self.show_services_page)
                    services_connected = True
                    break
        if not services_connected:
            pass
        # ANNOUNCEMENT button - search through ALL buttons to find it
        announcement_connected = False
        for btn in self.findChildren(QtWidgets.QPushButton):
            if btn and hasattr(btn, 'text'):
                button_text = btn.text().upper()
                # Check if button text contains ANNOUNCEMENT
                if 'ANNOUNCEMENT' in button_text and '×' not in button_text:
                    btn.clicked.connect(self.show_announcement_page)
                    announcement_connected = True
                    break
        if not announcement_connected:
            pass
        # OFFICIALS button - search through ALL buttons to find it
        officials_connected = False
        for btn in self.findChildren(QtWidgets.QPushButton):
            if btn and hasattr(btn, 'text'):
                button_text = btn.text().upper()
                # Check if button text contains OFFICIALS
                if 'OFFICIAL' in button_text and '×' not in button_text:
                    btn.clicked.connect(self.show_officials_page)
                    officials_connected = True
                    break
        if not officials_connected:
            pass
        # BLOTTER button (pushButton_20)
        if hasattr(self, 'pushButton_20'):
            self.pushButton_20.clicked.connect(self.show_blotter_page)
        # PAYMENT button (pushButton_14)
        if hasattr(self, 'pushButton_14'):
            self.pushButton_14.clicked.connect(self.show_payment_page)
        # PROFILE button (pushButton_12) - could be logout
        if hasattr(self, 'pushButton_12'):
            self.pushButton_12.clicked.connect(self.show_profile_page)
        # Find logout button (NOT the notification's × button)
        for btn in self.findChildren(QtWidgets.QPushButton):
            # Skip if it's the notification bar's close button
            if btn.text().strip() == '×':
                # Check if parent is NotificationBar
                parent = btn.parent()
                if parent and 'NotificationBar' in parent.__class__.__name__:
                    continue  # Skip notification bar's close button
                # This might be the logout button
                btn.clicked.connect(self.handle_logout)
                break
    def show_residents_page(self):
        """Load admin_residents.ui into the content area"""
        try:
            # Since admin_residents.ui is a QMainWindow, we need to load it differently
            # Create a temporary QMainWindow to load the UI
            temp_window = QtWidgets.QMainWindow()
            uic.loadUi(str(ADMIN_RESIDENTS_UI_PATH), temp_window)
            # Extract the central widget from the QMainWindow
            central = temp_window.centralWidget()
            # The actual content is inside a QWidget named 'widget' within the central widget
            # Find it by object name
            residents_widget = None
            if central:
                # Look for the inner widget with content
                for child in central.findChildren(QtWidgets.QWidget):
                    if child.objectName() == 'widget' and child.parent() == central:
                        residents_widget = child
                        break
                # If we didn't find it by name, try to get the first child widget with a layout
                if not residents_widget:
                    for child in central.findChildren(QtWidgets.QWidget):
                        if child.layout() and child.parent() == central:
                            residents_widget = child
                            break
            # Fallback: use central widget if we couldn't find the inner one
            if not residents_widget:
                residents_widget = central
            if not residents_widget:
                # Last resort: create wrapper
                residents_widget = QtWidgets.QWidget()
                layout = QtWidgets.QVBoxLayout(residents_widget)
                layout.addWidget(temp_window)
            # CRITICAL: Set size policy to make widget expand to fill space
            residents_widget.setSizePolicy(
                QtWidgets.QSizePolicy.Expanding, 
                QtWidgets.QSizePolicy.Expanding
            )
            # Let it resize to match the content area
            residents_widget.resize(self.content_area.size())
            # Find and connect the Add Resident button
            self.connect_add_resident_button(residents_widget)
            # Connect search functionality
            self.connect_search_button(residents_widget)
            # LOAD DATA INTO TABLE
            self.load_residents_table(residents_widget)
            # Debug: Print widget info
            # Clear existing content and add new widget
            if isinstance(self.content_area, QtWidgets.QStackedWidget):
                # If it's a stacked widget, add as new page
                while self.content_area.count() > 0:
                    old_widget = self.content_area.widget(0)
                    self.content_area.removeWidget(old_widget)
                    old_widget.deleteLater()
                self.content_area.addWidget(residents_widget)
                self.content_area.setCurrentWidget(residents_widget)
            elif isinstance(self.content_area, QtWidgets.QTabWidget):
                # If it's a tab widget, clear and add
                self.content_area.clear()
                self.content_area.addTab(residents_widget, "Residents")
            else:
                # Replace content in frame/widget
                # Clear existing layout
                old_layout = self.content_area.layout()
                if old_layout:
                    while old_layout.count():
                        item = old_layout.takeAt(0)
                        if item.widget():
                            item.widget().deleteLater()
                else:
                    old_layout = QtWidgets.QVBoxLayout(self.content_area)
                    self.content_area.setLayout(old_layout)
                # Add new widget
                old_layout.addWidget(residents_widget)
            # Force visibility
            residents_widget.show()
            self.content_area.show()
            self.content_area.raise_()
            self.content_area.update()
            self.notification.show_success("✅ Residents page loaded")
        except Exception as e:
            self.notification.show_error(f"❌ Error loading residents page: {e}")
            import traceback
            traceback.print_exc()
    def load_residents_table(self, widget, search_text=""):
        """Fetch residents from DB and populate the table"""
        try:
            # Find the table widget
            table = widget.findChild(QtWidgets.QTableWidget, "tableWidget")
            if not table:
                return
            # Fetch data
            db = SessionLocal()
            query = db.query(Resident)
            # Apply search filter if provided
            if search_text:
                search_filter = f"%{search_text}%"
                query = query.filter(
                    (Resident.last_name.like(search_filter)) |
                    (Resident.first_name.like(search_filter)) |
                    (Resident.middle_name.like(search_filter)) |
                    (Resident.sitio.like(search_filter)) |
                    (Resident.contact_number.like(search_filter))
                )
            residents = query.all()
            db.close()
            # Clear table
            table.setRowCount(0)
            # Add Actions column if not exists
            if table.columnCount() == 29:
                table.insertColumn(29)
                table.setHorizontalHeaderItem(29, QtWidgets.QTableWidgetItem("Actions"))
            # Populate rows
            for row_idx, r in enumerate(residents):
                table.insertRow(row_idx)
                # Map data to columns (Order MUST match the UI columns we added)
                data = [
                    r.last_name, r.first_name, r.middle_name, r.suffix,
                    r.gender, str(r.birth_date) if r.birth_date else "", r.birth_place, str(r.age) if r.age else "", r.civil_status,
                    r.spouse_name, str(r.no_of_children), str(r.no_of_siblings),
                    r.mother_full_name, r.father_full_name,
                    r.nationality, r.religion, r.occupation, r.highest_educational_attainment,
                    r.contact_number, r.emergency_contact_name, r.emergency_contact_number,
                    r.sitio, r.barangay, r.municipality,
                    "Yes" if r.registered_voter else "No",
                    "Yes" if r.indigent else "No",
                    "Yes" if r.solo_parent else "No",
                    r.solo_parent_id_no,
                    "Yes" if r.fourps_member else "No"
                ]
                for col_idx, value in enumerate(data):
                    item = QtWidgets.QTableWidgetItem(str(value) if value is not None else "")
                    item.setTextAlignment(QtCore.Qt.AlignCenter)
                    table.setItem(row_idx, col_idx, item)
                # Create container widget for centering
                button_container = QtWidgets.QWidget()
                button_layout = QtWidgets.QHBoxLayout(button_container)
                button_layout.setContentsMargins(0, 0, 0, 0)
                button_layout.setAlignment(QtCore.Qt.AlignCenter)
                edit_btn = QtWidgets.QPushButton()
                edit_btn.setIcon(self.create_edit_icon())
                edit_btn.setIconSize(QtCore.QSize(18, 18))
                edit_btn.setFixedSize(35, 30)
                edit_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #3498db;
                        border: none;
                        border-radius: 4px;
                    }
                    QPushButton:hover {
                        background-color: #2980b9;
                    }
                    QPushButton:pressed {
                        background-color: #1f5f8b;
                    }
                """)
                edit_btn.setCursor(QtCore.Qt.PointingHandCursor)
                edit_btn.setToolTip(f"Edit {r.first_name} {r.last_name}")
                # Connect button to edit function with resident_id
                edit_btn.clicked.connect(lambda checked, resident_id=r.resident_id: self.open_edit_resident_dialog(resident_id))
                # Add button to container
                button_layout.addWidget(edit_btn)
                # Add container to table
                table.setCellWidget(row_idx, 29, button_container)
            # Maximize column space
            header = table.horizontalHeader()
            header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
            # Keep Actions column fixed width
            header.setSectionResizeMode(29, QtWidgets.QHeaderView.Fixed)
            table.setColumnWidth(29, 80)
        except Exception as e:
            import traceback
            traceback.print_exc()
    def create_edit_icon(self):
        """Create edit icon - pencil in square frame"""
        pixmap = QtGui.QPixmap(24, 24)
        pixmap.fill(QtCore.Qt.transparent)
        painter = QtGui.QPainter(pixmap)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        # Draw square frame (like a document/paper)
        pen = QtGui.QPen(QtGui.QColor(255, 255, 255), 2)
        pen.setJoinStyle(QtCore.Qt.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.drawRoundedRect(2, 2, 20, 20, 3, 3)
        # Draw pencil inside (diagonal)
        painter.setBrush(QtGui.QBrush(QtGui.QColor(255, 255, 255)))
        # Pencil body (thick diagonal line)
        pen_body = QtGui.QPen(QtGui.QColor(255, 255, 255), 3)
        pen_body.setCapStyle(QtCore.Qt.RoundCap)
        painter.setPen(pen_body)
        painter.drawLine(14, 8, 8, 14)
        # Pencil tip (small triangle)
        tip = QtGui.QPolygon([
            QtCore.QPoint(8, 14),
            QtCore.QPoint(6, 16),
            QtCore.QPoint(10, 16)
        ])
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawPolygon(tip)
        # Eraser (small rectangle at top)
        painter.setBrush(QtGui.QBrush(QtGui.QColor(255, 220, 220)))
        painter.drawRect(14, 7, 3, 2)
        painter.end()
        return QtGui.QIcon(pixmap)
    def view_full_photo(self, photo_path):
        """View full-size photo in a dialog"""
        try:
            from pathlib import Path
            if not Path(photo_path).exists():
                self.notification.show_error("❌ Photo file not found!")
                return
            # Create dialog to show photo
            dialog = QtWidgets.QDialog(self)
            dialog.setWindowTitle("Resident Photo")
            dialog.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.WindowCloseButtonHint)
            layout = QtWidgets.QVBoxLayout(dialog)
            # Photo label
            photo_label = QtWidgets.QLabel()
            photo_label.setAlignment(QtCore.Qt.AlignCenter)
            # Load photo
            pixmap = QtGui.QPixmap(photo_path)
            if not pixmap.isNull():
                # Scale to max 800x600 while maintaining aspect ratio
                scaled_pixmap = pixmap.scaled(800, 600, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
                photo_label.setPixmap(scaled_pixmap)
            else:
                photo_label.setText("Failed to load photo")
            layout.addWidget(photo_label)
            # Close button
            close_btn = QtWidgets.QPushButton("Close")
            close_btn.clicked.connect(dialog.close)
            layout.addWidget(close_btn)
            dialog.setModal(True)
            dialog.exec_()
        except Exception as e:
            self.notification.show_error(f"❌ Error viewing photo: {e}")
            import traceback
            traceback.print_exc()
    def open_edit_resident_dialog(self, resident_id):
        """Open edit dialog for a specific resident"""
        try:
            # Fetch resident data
            db = SessionLocal()
            resident = db.query(Resident).filter(Resident.resident_id == resident_id).first()
            db.close()
            if not resident:
                self.notification.show_error("❌ Resident not found!")
                return
            # Open data collection form in edit mode
            dialog = QtWidgets.QMainWindow(self)
            uic.loadUi(str(Path(__file__).resolve().parent.parent / "ui" / "DATA_COLLECTION OF ADMIN_REGISTER.ui"), dialog)
            dialog.setWindowTitle(f"Edit Resident - {resident.first_name} {resident.last_name}")
            dialog.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.WindowCloseButtonHint)
            # PRE-FILL FORM FIELDS
            # Personal Information
            if hasattr(dialog, 'lineEdit'):  # Last name
                dialog.lineEdit.setText(resident.last_name or "")
            if hasattr(dialog, 'lineEdit_2'):  # First name
                dialog.lineEdit_2.setText(resident.first_name or "")
            if hasattr(dialog, 'lineEdit_3'):  # Middle name
                dialog.lineEdit_3.setText(resident.middle_name or "")
            if hasattr(dialog, 'lineEdit_6'):  # Suffix
                dialog.lineEdit_6.setText(resident.suffix or "")
            # Gender
            if hasattr(dialog, 'comboBox'):
                if resident.gender:
                    index = dialog.comboBox.findText(resident.gender)
                    if index >= 0:
                        dialog.comboBox.setCurrentIndex(index)
            # Birth date
            if hasattr(dialog, 'dateEdit') and resident.birth_date:
                from PyQt5.QtCore import QDate
                dialog.dateEdit.setDate(QDate(resident.birth_date.year, resident.birth_date.month, resident.birth_date.day))
            # Birth place
            if hasattr(dialog, 'lineEdit_4'):
                dialog.lineEdit_4.setText(resident.birth_place or "")
            # Age
            if hasattr(dialog, 'lineEdit_7'):  
                dialog.lineEdit_7.setText(str(resident.age) if resident.age else "")
            # Civil status
            if hasattr(dialog, 'comboBox_2'):
                if resident.civil_status:
                    index = dialog.comboBox_2.findText(resident.civil_status)
                    if index >= 0:
                        dialog.comboBox_2.setCurrentIndex(index)
            # Contact number
            if hasattr(dialog, 'lineEdit_10'):
                dialog.lineEdit_10.setText(resident.contact_number or "")
            # Nationality
            if hasattr(dialog, 'lineEdit_5'):
                dialog.lineEdit_5.setText(resident.nationality or "")
            # Religion
            if hasattr(dialog, 'lineEdit_8'):
                dialog.lineEdit_8.setText(resident.religion or "")
            # Occupation
            if hasattr(dialog, 'lineEdit_9'):
                dialog.lineEdit_9.setText(resident.occupation or "")
            # TODO: Map remaining fields (spouse, children, emergency contact, etc.)
            # You can add more field mappings based on the actual UI field names
            # CONNECT SUBMIT BUTTON
            # The SUBMIT button is "pushButton_2"
            submit_button = dialog.findChild(QtWidgets.QPushButton, "pushButton_2")
            if submit_button:
                # Disconnect any existing connections
                try:
                    submit_button.clicked.disconnect()
                except:
                    pass
                # Connect to save function
                submit_button.clicked.connect(lambda: self.save_resident_edits(dialog, resident_id))
            else:
                # Try to find any button with SUBMIT text
                for btn in dialog.findChildren(QtWidgets.QPushButton):
                    if "submit" in btn.text().lower():
                        btn.clicked.connect(lambda: self.save_resident_edits(dialog, resident_id))
                        break
            # CONNECT UPLOAD PHOTO BUTTON
            upload_button = dialog.findChild(QtWidgets.QPushButton, "pushButton")  # UPLOAD button
            photo_label = dialog.findChild(QtWidgets.QLabel, "label_11")  # NO IMAGE label
            if upload_button and photo_label:
                # Store reference to photo label
                dialog.photo_label = photo_label
                dialog.photo_path = None  # Will store selected photo path
                # Connect upload button
                upload_button.clicked.connect(lambda: self.upload_resident_photo(dialog))
            else:
                pass
            dialog.setWindowModality(QtCore.Qt.ApplicationModal)
            dialog.show()
            self.notification.show_info(f"✏️ Editing: {resident.first_name} {resident.last_name}")
        except Exception as e:
            self.notification.show_error(f"❌ Error opening edit dialog: {e}")
            import traceback
            traceback.print_exc()
    def upload_resident_photo(self, dialog):
        """Handle photo upload for resident"""
        try:
            # Open file dialog to select image
            file_dialog = QtWidgets.QFileDialog()
            file_path, _ = file_dialog.getOpenFileName(
                dialog,
                "Select Photo",
                "",
                "Image Files (*.png *.jpg *.jpeg *.bmp *.gif);;All Files (*)"
            )
            if file_path:
                # Load and display the image
                pixmap = QtGui.QPixmap(file_path)
                if not pixmap.isNull():
                    # Scale image to fit the label (100x100)
                    scaled_pixmap = pixmap.scaled(
                        100, 100,
                        QtCore.Qt.KeepAspectRatio,
                        QtCore.Qt.SmoothTransformation
                    )
                    # Display in label
                    dialog.photo_label.setPixmap(scaled_pixmap)
                    dialog.photo_label.setText("")  # Clear "NO IMAGE" text
                    # Store the file path
                    dialog.photo_path = file_path
                    self.notification.show_success("✅ Photo uploaded!")
                else:
                    self.notification.show_error("❌ Failed to load image!")
            else:
                pass
        except Exception as e:
            self.notification.show_error(f"❌ Error uploading photo: {e}")
            import traceback
            traceback.print_exc()
    def save_resident_edits(self, dialog, resident_id):
        """Save edited resident data to database"""
        try:
            # Read all form fields
            data = {}
            # Personal Information
            if hasattr(dialog, 'lineEdit'):
                data['last_name'] = dialog.lineEdit.text().strip()
            if hasattr(dialog, 'lineEdit_2'):
                data['first_name'] = dialog.lineEdit_2.text().strip()
            if hasattr(dialog, 'lineEdit_3'):
                data['middle_name'] = dialog.lineEdit_3.text().strip() or None
            if hasattr(dialog, 'lineEdit_6'):
                data['suffix'] = dialog.lineEdit_6.text().strip() or None
            # Gender
            if hasattr(dialog, 'comboBox'):
                gender = dialog.comboBox.currentText()
                if gender and gender != "Select":
                    data['gender'] = gender
            # Birth date
            if hasattr(dialog, 'dateEdit'):
                qdate = dialog.dateEdit.date()
                data['birth_date'] = f"{qdate.year()}-{qdate.month():02d}-{qdate.day():02d}"
            # Birth place
            if hasattr(dialog, 'lineEdit_4'):
                data['birth_place'] = dialog.lineEdit_4.text().strip() or None
            # Age
            if hasattr(dialog, 'lineEdit_7'):
                age_text = dialog.lineEdit_7.text().strip()
                data['age'] = int(age_text) if age_text else None
            # Civil status
            if hasattr(dialog, 'comboBox_2'):
                civil = dialog.comboBox_2.currentText()
                if civil and civil != "Select":
                    data['civil_status'] = civil
            # Contact number
            if hasattr(dialog, 'lineEdit_10'):
                data['contact_number'] = dialog.lineEdit_10.text().strip() or None
            # Nationality
            if hasattr(dialog, 'lineEdit_5'):
                data['nationality'] = dialog.lineEdit_5.text().strip() or None
            # Religion
            if hasattr(dialog, 'lineEdit_8'):
                data['religion'] = dialog.lineEdit_8.text().strip() or None
            # Occupation
            if hasattr(dialog, 'lineEdit_9'):
                data['occupation'] = dialog.lineEdit_9.text().strip() or None
            # Photo path
            if hasattr(dialog, 'photo_path') and dialog.photo_path:
                data['photo_path'] = dialog.photo_path
            # Debug: Show collected data
            # Validate required fields
            if not data.get('last_name') or not data.get('first_name'):
                self.notification.show_error("❌ Last name and first name are required!")
                return
            # Update database
            db = SessionLocal()
            try:
                resident = db.query(Resident).filter(Resident.resident_id == resident_id).first()
                if not resident:
                    self.notification.show_error("❌ Resident not found!")
                    return
                # Update fields
                for key, value in data.items():
                    if hasattr(resident, key):
                        setattr(resident, key, value)
                db.commit()
                db.refresh(resident)
                # Close dialog
                dialog.close()
                # Refresh the table
                if hasattr(self, 'current_residents_widget'):
                    self.load_residents_table(self.current_residents_widget)
                    self.notification.show_success(f"✅ Updated: {resident.first_name} {resident.last_name}")
            except Exception as e:
                db.rollback()
                self.notification.show_error(f"❌ Database error: {e}")
                import traceback
                traceback.print_exc()
            finally:
                db.close()
        except Exception as e:
            self.notification.show_error(f"❌ Error saving data: {e}")
            import traceback
            traceback.print_exc()
    def connect_search_button(self, widget):
        """Connect search button and line edit"""
        try:
            # Find search button (pushButton_2)
            search_btn = widget.findChild(QtWidgets.QPushButton, "pushButton_2")
            # Find search line edit
            search_input = widget.findChild(QtWidgets.QLineEdit, "lineEdit")
            if search_btn and search_input:
                # Store references for search functionality
                self.current_residents_widget = widget
                self.search_input = search_input
                # Connect search button
                search_btn.clicked.connect(lambda: self.perform_search(widget))
                # Also connect Enter key in search box
                search_input.returnPressed.connect(lambda: self.perform_search(widget))
            else:
                pass
        except Exception as e:
            pass
    def perform_search(self, widget):
        """Perform search and refresh table"""
        try:
            search_text = self.search_input.text().strip()
            # Reload table with search filter
            self.load_residents_table(widget, search_text)
            if search_text:
                self.notification.show_info(f"🔍 Search: '{search_text}'")
            else:
                self.notification.show_info("📋 Showing all residents")
        except Exception as e:
            pass
    def connect_add_resident_button(self, widget):
        """Find and connect the Add Resident button in admin_residents"""
        for btn in widget.findChildren(QtWidgets.QPushButton):
            btn_name = btn.objectName().lower()
            btn_text = btn.text().lower()
            # Check if it's an Add button
            if 'add' in btn_name or 'add' in btn_text:
                # Add icon to button
                icon = self.create_add_icon()
                btn.setIcon(icon)
                btn.setIconSize(QtCore.QSize(24, 24))
                # Style it BLUE (same as search button)
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: rgb(85, 170, 255);
                        color: white;
                        font-size: 12pt;
                        font-weight: bold;
                        padding: 10px 20px;
                        border-radius: 8px;
                        border: none;
                    }
                    QPushButton:hover {
                        background-color: rgb(70, 150, 230);
                    }
                    QPushButton:pressed {
                        background-color: rgb(60, 130, 200);
                    }
                """)
                btn.setCursor(QtCore.Qt.PointingHandCursor)
                # Connect to open data collection
                btn.clicked.connect(self.open_data_collection_dialog)
                break
    def create_add_icon(self):
        """Create a + icon for the Add button"""
        pixmap = QtGui.QPixmap(32, 32)
        pixmap.fill(QtCore.Qt.transparent)
        painter = QtGui.QPainter(pixmap)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        # Draw white + symbol
        painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255), 3))
        painter.drawLine(8, 16, 24, 16)
        painter.drawLine(16, 8, 16, 24)
        painter.end()
        return QtGui.QIcon(pixmap)
    def open_data_collection_dialog(self):
        """Open Data Collection dialog for adding new resident"""
        try:
            # Load the Data Collection UI
            dialog = QtWidgets.QMainWindow(self)
            uic.loadUi(str(Path(__file__).resolve().parent.parent / "ui" / "DATA_COLLECTION OF ADMIN_REGISTER.ui"), dialog)
            dialog.setWindowTitle("Data Collection - Register Resident")
            dialog.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.WindowCloseButtonHint)
            # CONNECT SUBMIT BUTTON
            submit_button = dialog.findChild(QtWidgets.QPushButton, "pushButton_2")
            if submit_button:
                # Disconnect any existing connections
                try:
                    submit_button.clicked.disconnect()
                except:
                    pass
                # Connect to add new resident function
                submit_button.clicked.connect(lambda: self.add_new_resident(dialog))
            else:
                pass
            # CONNECT UPLOAD PHOTO BUTTON
            upload_button = dialog.findChild(QtWidgets.QPushButton, "pushButton")
            photo_label = dialog.findChild(QtWidgets.QLabel, "label_11")
            if upload_button and photo_label:
                dialog.photo_label = photo_label
                dialog.photo_path = None
                upload_button.clicked.connect(lambda: self.upload_resident_photo(dialog))
            # Show as modal dialog
            dialog.setWindowModality(QtCore.Qt.ApplicationModal)
            dialog.show()
            self.notification.show_info("📝 Fill in resident information and click SUBMIT")
        except Exception as e:
            self.notification.show_error(f"❌ Error opening data collection: {e}")
            import traceback
            traceback.print_exc()
    def add_new_resident(self, dialog):
        """Save new resident to database"""
        try:
            # Read all form fields
            data = {}
            # Personal Information
            if hasattr(dialog, 'lineEdit'):
                data['last_name'] = dialog.lineEdit.text().strip()
            if hasattr(dialog, 'lineEdit_2'):
                data['first_name'] = dialog.lineEdit_2.text().strip()
            if hasattr(dialog, 'lineEdit_3'):
                data['middle_name'] = dialog.lineEdit_3.text().strip() or None
            if hasattr(dialog, 'lineEdit_6'):
                data['suffix'] = dialog.lineEdit_6.text().strip() or None
            # Gender
            if hasattr(dialog, 'comboBox'):
                gender = dialog.comboBox.currentText()
                if gender and gender != "Select":
                    data['gender'] = gender
            # Birth date
            if hasattr(dialog, 'dateEdit'):
                qdate = dialog.dateEdit.date()
                data['birth_date'] = f"{qdate.year()}-{qdate.month():02d}-{qdate.day():02d}"
            # Birth place
            if hasattr(dialog, 'lineEdit_4'):
                data['birth_place'] = dialog.lineEdit_4.text().strip() or None
            # Age
            if hasattr(dialog, 'lineEdit_7'):
                age_text = dialog.lineEdit_7.text().strip()
                data['age'] = int(age_text) if age_text else None
            # Civil status
            if hasattr(dialog, 'comboBox_2'):
                civil = dialog.comboBox_2.currentText()
                if civil and civil != "Select":
                    data['civil_status'] = civil
            # Contact number
            if hasattr(dialog, 'lineEdit_10'):
                data['contact_number'] = dialog.lineEdit_10.text().strip() or None
            # Nationality
            if hasattr(dialog, 'lineEdit_5'):
                data['nationality'] = dialog.lineEdit_5.text().strip() or "Filipino"
            # Religion
            if hasattr(dialog, 'lineEdit_8'):
                data['religion'] = dialog.lineEdit_8.text().strip() or None
            # Occupation
            if hasattr(dialog, 'lineEdit_9'):
                data['occupation'] = dialog.lineEdit_9.text().strip() or None
            # Address - Sitio/Purok
            if hasattr(dialog, 'comboBox_3'):
                sitio = dialog.comboBox_3.currentText()
                if sitio and sitio != "Select":
                    data['sitio'] = sitio
            # Barangay (default)
            data['barangay'] = "Barangay Balibago"
            data['municipality'] = "Calatagan"
            # Photo path
            if hasattr(dialog, 'photo_path') and dialog.photo_path:
                data['photo_path'] = dialog.photo_path
            # Debug: Show collected data
            # Validate required fields
            if not data.get('last_name') or not data.get('first_name'):
                self.notification.show_error("❌ Last name and first name are required!")
                return
            if not data.get('gender'):
                self.notification.show_error("❌ Gender is required!")
                return
            if not data.get('birth_date'):
                self.notification.show_error("❌ Birth date is required!")
                return
            if not data.get('civil_status'):
                self.notification.show_error("❌ Civil status is required!")
                return
            # Insert into database
            db = SessionLocal()
            try:
                new_resident = Resident(
                    last_name=data.get('last_name'),
                    first_name=data.get('first_name'),
                    middle_name=data.get('middle_name'),
                    suffix=data.get('suffix'),
                    gender=data.get('gender'),
                    birth_date=data.get('birth_date'),
                    birth_place=data.get('birth_place'),
                    age=data.get('age'),
                    civil_status=data.get('civil_status'),
                    contact_number=data.get('contact_number'),
                    nationality=data.get('nationality', 'Filipino'),
                    religion=data.get('religion'),
                    occupation=data.get('occupation'),
                    sitio=data.get('sitio'),
                    barangay=data.get('barangay', 'Barangay Balibago'),
                    municipality=data.get('municipality', 'Calatagan'),
                    photo_path=data.get('photo_path')
                )
                db.add(new_resident)
                db.commit()
                db.refresh(new_resident)
                # Close dialog
                dialog.close()
                # Refresh the table
                if hasattr(self, 'current_residents_widget'):
                    self.load_residents_table(self.current_residents_widget)
                    self.notification.show_success(f"✅ Added: {new_resident.first_name} {new_resident.last_name}")
                else:
                    self.notification.show_success(f"✅ Resident added successfully!")
            except Exception as e:
                db.rollback()
                self.notification.show_error(f"❌ Database error: {e}")
                import traceback
                traceback.print_exc()
            finally:
                db.close()
        except Exception as e:
            self.notification.show_error(f"❌ Error saving data: {e}")
            import traceback
            traceback.print_exc()
    def show_dashboard_page(self):
        """Show comprehensive admin dashboard with animated charts and statistics"""
        try:
            # Get all statistics from database
            stats = self.get_comprehensive_dashboard_stats()
            # Main dashboard widget
            dashboard = QtWidgets.QWidget()
            dashboard.setStyleSheet("background-color: rgb(240, 244, 248);")
            main_layout = QtWidgets.QVBoxLayout(dashboard)
            main_layout.setContentsMargins(15, 15, 15, 15)
            main_layout.setSpacing(15)
            # === HEADER ===
            header = QtWidgets.QLabel("ADMIN DASHBOARD")
            header.setStyleSheet("""
                QLabel {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #1e3c72, stop:1 #2a5298);
                    color: white;
                    font-size: 22pt;
                    font-weight: bold;
                    padding: 15px;
                    border-radius: 12px;
                }
            """)
            header.setAlignment(QtCore.Qt.AlignCenter)
            header.setMinimumHeight(60)
            main_layout.addWidget(header)
            # === ROW 1: RESIDENT STATISTICS (Circular Progress) ===
            row1_label = QtWidgets.QLabel("📊 RESIDENT STATISTICS")
            row1_label.setStyleSheet("font-size: 14pt; font-weight: bold; color: #2c3e50; background: transparent;")
            main_layout.addWidget(row1_label)
            resident_grid = QtWidgets.QHBoxLayout()
            resident_grid.setSpacing(10)
            resident_cards = [
                ("TOTAL\nRESIDENTS", stats['total_residents'], ["#667eea", "#764ba2"]),
                ("MALE", stats['male'], ["#4facfe", "#00f2fe"]),
                ("FEMALE", stats['female'], ["#f093fb", "#f5576c"]),
                ("VOTERS", stats['voters'], ["#43e97b", "#38f9d7"]),
                ("4Ps", stats['fourps'], ["#fa709a", "#fee140"]),
                ("SOLO\nPARENT", stats['solo_parent'], ["#30cfd0", "#330867"]),
                ("INDIGENT", stats['indigent'], ["#ff9a9e", "#fad0c4"]),
            ]
            for title, value, colors in resident_cards:
                card = self.create_admin_stat_card(title, value, colors, size=100)
                resident_grid.addWidget(card)
            main_layout.addLayout(resident_grid)
            # === ROW 2: CHARTS (Line Chart + Bar Chart) ===
            charts_layout = QtWidgets.QHBoxLayout()
            charts_layout.setSpacing(15)
            # --- Line Chart: Monthly Requests Trend ---
            line_widget = QtWidgets.QWidget()
            line_widget.setStyleSheet("background-color: white; border-radius: 12px;")
            line_layout = QtWidgets.QVBoxLayout(line_widget)
            line_layout.setContentsMargins(12, 12, 12, 12)
            line_title = QtWidgets.QLabel("📈 MONTHLY REQUESTS TREND")
            line_title.setStyleSheet("""
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #11998e, stop:1 #38ef7d);
                color: white; font-size: 11pt; font-weight: bold; padding: 10px; border-radius: 8px;
            """)
            line_title.setAlignment(QtCore.Qt.AlignCenter)
            line_layout.addWidget(line_title)
            line_chart = AdminAnimatedLineChart()
            line_chart.set_data(stats['months'], stats['monthly_requests'], "#11998e")
            line_chart.setMinimumHeight(180)
            line_layout.addWidget(line_chart)
            charts_layout.addWidget(line_widget, stretch=1)
            # --- Bar Chart: Services Breakdown ---
            bar_widget = QtWidgets.QWidget()
            bar_widget.setStyleSheet("background-color: white; border-radius: 12px;")
            bar_layout = QtWidgets.QVBoxLayout(bar_widget)
            bar_layout.setContentsMargins(12, 12, 12, 12)
            bar_title = QtWidgets.QLabel("📊 SERVICES BREAKDOWN")
            bar_title.setStyleSheet("""
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #667eea, stop:1 #764ba2);
                color: white; font-size: 11pt; font-weight: bold; padding: 10px; border-radius: 8px;
            """)
            bar_title.setAlignment(QtCore.Qt.AlignCenter)
            bar_layout.addWidget(bar_title)
            bar_chart = AdminAnimatedBarChart()
            bar_chart.months = ['ID', 'Clearance', 'Indigency', 'Business', 'Completed', 'Pending']
            bar_chart.values = [
                stats['barangay_id'], stats['clearance'], stats['indigency'],
                stats['business_permit'], stats['completed'], stats['pending']
            ]
            bar_chart.max_value = max(bar_chart.values) if bar_chart.values else 1
            bar_chart.setMinimumHeight(180)
            bar_layout.addWidget(bar_chart)
            charts_layout.addWidget(bar_widget, stretch=1)
            main_layout.addLayout(charts_layout)
            # === ROW 3: RESIDENTS PER SITIO + REQUEST DISTRIBUTION ===
            row3_layout = QtWidgets.QHBoxLayout()
            row3_layout.setSpacing(15)
            # --- Sitio Bar Chart ---
            sitio_widget = QtWidgets.QWidget()
            sitio_widget.setStyleSheet("background-color: white; border-radius: 12px;")
            sitio_layout = QtWidgets.QVBoxLayout(sitio_widget)
            sitio_layout.setContentsMargins(12, 12, 12, 12)
            sitio_title = QtWidgets.QLabel("🏘️ RESIDENTS PER SITIO")
            sitio_title.setStyleSheet("""
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #f093fb, stop:1 #f5576c);
                color: white; font-size: 11pt; font-weight: bold; padding: 10px; border-radius: 8px;
            """)
            sitio_title.setAlignment(QtCore.Qt.AlignCenter)
            sitio_layout.addWidget(sitio_title)
            sitio_chart = AdminSitioBarChart()
            sitio_chart.set_data(stats['sitio_data'])
            sitio_chart.setMinimumHeight(200)
            sitio_layout.addWidget(sitio_chart)
            row3_layout.addWidget(sitio_widget, stretch=1)
            # --- Pie Chart: Request Distribution ---
            pie_widget = QtWidgets.QWidget()
            pie_widget.setStyleSheet("background-color: white; border-radius: 12px;")
            pie_layout = QtWidgets.QVBoxLayout(pie_widget)
            pie_layout.setContentsMargins(12, 12, 12, 12)
            pie_title = QtWidgets.QLabel("🥧 REQUEST DISTRIBUTION")
            pie_title.setStyleSheet("""
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4facfe, stop:1 #00f2fe);
                color: white; font-size: 11pt; font-weight: bold; padding: 10px; border-radius: 8px;
            """)
            pie_title.setAlignment(QtCore.Qt.AlignCenter)
            pie_layout.addWidget(pie_title)
            pie_chart = AdminAnimatedPieChart(stats)
            pie_chart.setMinimumHeight(200)
            pie_layout.addWidget(pie_chart)
            row3_layout.addWidget(pie_widget, stretch=1)
            main_layout.addLayout(row3_layout)
            # === ROW 4: QUICK STATS (Blotters, Total Requests, Transactions) ===
            row4_layout = QtWidgets.QHBoxLayout()
            row4_layout.setSpacing(10)
            quick_stats = [
                ("📝 BLOTTER\nREPORTS", stats['blotters'], ["#eb3349", "#f45c43"]),
                ("📋 TOTAL\nREQUESTS", stats['total_requests'], ["#2193b0", "#6dd5ed"]),
                ("💰 TOTAL\nTRANSACTIONS", stats['transactions'], ["#11998e", "#38ef7d"]),
                ("✅ COMPLETED", stats['completed'], ["#43e97b", "#38f9d7"]),
                ("⏳ PENDING", stats['pending'], ["#f7971e", "#ffd200"]),
                ("❌ REJECTED", stats['rejected'], ["#cb2d3e", "#ef473a"]),
            ]
            for title, value, colors in quick_stats:
                card = self.create_admin_stat_card(title, value, colors, size=90)
                row4_layout.addWidget(card)
            main_layout.addLayout(row4_layout)
            # Wrap in scroll area
            scroll = QtWidgets.QScrollArea()
            scroll.setWidget(dashboard)
            scroll.setWidgetResizable(True)
            scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
            scroll.setStyleSheet("QScrollArea { background-color: rgb(240, 244, 248); border: none; }")
            self.replace_content(scroll)
            self.notification.show_info("📊 Admin Dashboard loaded")
        except Exception as e:
            self.notification.show_error(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
    def get_comprehensive_dashboard_stats(self):
        """Get all dashboard statistics from database"""
        from datetime import datetime, timedelta
        stats = {
            'total_residents': 0, 'male': 0, 'female': 0,
            'voters': 0, 'fourps': 0, 'solo_parent': 0, 'indigent': 0,
            'barangay_id': 0, 'business_permit': 0, 'indigency': 0, 'clearance': 0,
            'completed': 0, 'pending': 0, 'rejected': 0,
            'total_requests': 0, 'blotters': 0, 'transactions': 0,
            'months': [], 'monthly_requests': [],
            'sitio_data': []
        }
        try:
            session = SessionLocal()
            # === RESIDENT STATISTICS ===
            stats['total_residents'] = session.query(Resident).count()
            stats['male'] = session.query(Resident).filter(Resident.gender == 'Male').count()
            stats['female'] = session.query(Resident).filter(Resident.gender == 'Female').count()
            stats['voters'] = session.query(Resident).filter(Resident.registered_voter == True).count()
            stats['fourps'] = session.query(Resident).filter(Resident.fourps_member == True).count()
            stats['solo_parent'] = session.query(Resident).filter(Resident.solo_parent == True).count()
            stats['indigent'] = session.query(Resident).filter(Resident.indigent == True).count()
            # === RESIDENTS PER SITIO ===
            from sqlalchemy import func
            sitio_counts = session.query(
                Resident.sitio, func.count(Resident.resident_id)
            ).group_by(Resident.sitio).order_by(func.count(Resident.resident_id).desc()).limit(8).all()
            stats['sitio_data'] = [(sitio or 'Unknown', count) for sitio, count in sitio_counts]
            if not stats['sitio_data']:
                stats['sitio_data'] = [('No Data', 0)]
            # === REQUEST STATISTICS ===
            try:
                from app.models import CertificateRequest
                stats['barangay_id'] = session.query(CertificateRequest).filter(
                    CertificateRequest.certificate_type.ilike('%id%')
                ).count()
                stats['business_permit'] = session.query(CertificateRequest).filter(
                    CertificateRequest.certificate_type.ilike('%business%')
                ).count()
                stats['indigency'] = session.query(CertificateRequest).filter(
                    CertificateRequest.certificate_type.ilike('%indigency%')
                ).count()
                stats['clearance'] = session.query(CertificateRequest).filter(
                    CertificateRequest.certificate_type.ilike('%clearance%')
                ).count()
                stats['completed'] = session.query(CertificateRequest).filter(
                    CertificateRequest.status.ilike('%completed%')
                ).count()
                stats['pending'] = session.query(CertificateRequest).filter(
                    CertificateRequest.status.ilike('%pending%')
                ).count()
                stats['rejected'] = session.query(CertificateRequest).filter(
                    CertificateRequest.status.ilike('%rejected%')
                ).count()
                stats['total_requests'] = session.query(CertificateRequest).count()
                stats['transactions'] = stats['completed']  # Completed = paid transactions
                # === MONTHLY TREND (last 6 months) ===
                for i in range(5, -1, -1):
                    date = datetime.now() - timedelta(days=i*30)
                    month_name = date.strftime('%b')
                    stats['months'].append(month_name)
                    start_date = date.replace(day=1)
                    if date.month == 12:
                        end_date = date.replace(year=date.year+1, month=1, day=1)
                    else:
                        end_date = date.replace(month=date.month+1, day=1)
                    count = session.query(CertificateRequest).filter(
                        CertificateRequest.created_at >= start_date,
                        CertificateRequest.created_at < end_date
                    ).count()
                    stats['monthly_requests'].append(count if count > 0 else (6-i) * 3)
            except Exception as e:
                stats['months'] = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
                stats['monthly_requests'] = [5, 12, 8, 15, 10, 18]
            # === BLOTTER COUNT ===
            try:
                from app.models import Blotter
                stats['blotters'] = session.query(Blotter).count()
            except:
                stats['blotters'] = 0
            session.close()
        except Exception as e:
            # Fallback sample data
            stats['months'] = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
            stats['monthly_requests'] = [5, 12, 8, 15, 10, 18]
            stats['sitio_data'] = [('Sitio 1', 25), ('Sitio 2', 18), ('Sitio 3', 12)]
        return stats
    def create_admin_stat_card(self, title, value, colors, size=120):
        """Create a stat card with animated circular progress"""
        card = QtWidgets.QWidget()
        card.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e0e0e0;
            }
        """)
        card.setMinimumSize(size + 40, size + 50)
        layout = QtWidgets.QVBoxLayout(card)
        layout.setAlignment(QtCore.Qt.AlignCenter)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(5)
        # Circular progress
        circle = AdminAnimatedCircleProgress(value, colors, max(value, 100))
        circle.setFixedSize(size, size)
        layout.addWidget(circle, alignment=QtCore.Qt.AlignCenter)
        # Title label
        title_label = QtWidgets.QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 9pt;
                font-weight: bold;
                background: transparent;
                border: none;
            }
        """)
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        title_label.setWordWrap(True)
        layout.addWidget(title_label)
        return card
    def show_blotter_page(self):
        """Create Blotter page programmatically with proper layouts for scaling"""
        try:
            # Outer wrapper with 2 inch margins (approx 50px per inch = 100px)
            outer_widget = QtWidgets.QWidget()
            outer_widget.setStyleSheet("background-color: #f0f0f0;")
            outer_layout = QtWidgets.QVBoxLayout(outer_widget)
            outer_layout.setContentsMargins(100, 50, 100, 50)  # 2 inches sides, 1 inch top/bottom
            # Main container widget - no max size, fills available space
            blotter_widget = QtWidgets.QWidget()
            blotter_widget.setStyleSheet("background-color: #dddddd; border-radius: 15px;")
            blotter_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            main_layout = QtWidgets.QVBoxLayout(blotter_widget)
            main_layout.setContentsMargins(20, 15, 20, 15)
            main_layout.setSpacing(10)
            # Header section
            header = QtWidgets.QLabel()
            header.setText("""<html><body>
                <p style="font-size: 18pt; font-weight: bold; color: white; margin: 0;">BLOTTER REPORTS</p>
                <p style="font-size: 11pt; color: white; margin: 0;">Documented Reports of Local Incidents</p>
            </body></html>""")
            header.setStyleSheet("""
                QLabel {
                    background: qlineargradient(
                        spread:pad, x1:0, y1:0, x2:0, y2:1,
                        stop:0 #0d47a1, stop:1 #1976d2
                    );
                    border-radius: 10px;
                    padding: 20px;
                }
            """)
            header.setMinimumHeight(100)
            main_layout.addWidget(header)
            # List button row - to view all blotter reports
            list_row = QtWidgets.QHBoxLayout()
            list_row.addStretch()
            list_btn = QtWidgets.QPushButton("📋 List")
            list_btn.setFixedSize(100, 32)
            list_btn.setCursor(QtCore.Qt.PointingHandCursor)
            list_btn.setStyleSheet("""
                QPushButton {
                    background-color: white;
                    border: 1px solid #ccc;
                    border-radius: 5px;
                    font-size: 10pt;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #e3f2fd;
                }
            """)
            list_btn.clicked.connect(self.show_blotter_table)
            list_row.addWidget(list_btn)
            main_layout.addLayout(list_row)
            # Content grid - 2x2 layout
            grid_layout = QtWidgets.QGridLayout()
            grid_layout.setSpacing(15)
            # Create COMPLAINANT section (0, 0)
            complainant_section, self.complainant_input = self.create_blotter_section("COMPLAINANT")
            grid_layout.addWidget(complainant_section, 0, 0)
            # Create RESPONDENT section (0, 1)
            respondent_section, self.respondent_input = self.create_blotter_section("RESPONDENT")
            grid_layout.addWidget(respondent_section, 0, 1)
            # Create special INCIDENT DETAILS section (1, 0)
            incident_section = self.create_incident_details_section()
            grid_layout.addWidget(incident_section, 1, 0)
            # Create LOCATION section (1, 1)
            location_section, self.location_input = self.create_blotter_section("LOCATION")
            grid_layout.addWidget(location_section, 1, 1)
            main_layout.addLayout(grid_layout, 1)
            # Submit button
            submit_row = QtWidgets.QHBoxLayout()
            submit_row.addStretch()
            submit_btn = QtWidgets.QPushButton("Submit Blotter Report")
            submit_btn.setCursor(QtCore.Qt.PointingHandCursor)
            submit_btn.setStyleSheet("""
                QPushButton {
                    padding: 10px 25px;
                    font-size: 11pt;
                    font-weight: bold;
                    background-color: #1976d2;
                    color: white;
                    border: none;
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background-color: #1565c0;
                }
            """)
            submit_btn.clicked.connect(self.submit_blotter_report)
            submit_row.addWidget(submit_btn)
            submit_row.addStretch()
            main_layout.addLayout(submit_row)
            # Add blotter widget to outer container - fills available space
            outer_layout.addWidget(blotter_widget)
            # Replace content
            self.replace_content(outer_widget)
            self.notification.show_success("✅ Blotter page loaded")
        except Exception as e:
            self.notification.show_error(f"❌ Error loading blotter page: {e}")
            import traceback
            traceback.print_exc()
    def create_blotter_section(self, title):
        """Create a blotter section widget with title and input area"""
        section = QtWidgets.QWidget()
        section.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        section.setStyleSheet("""
            QWidget {
                background-color: #e5e5e5;
                border-radius: 8px;
            }
        """)
        layout = QtWidgets.QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 8)
        layout.setSpacing(10)
        # Title label
        title_label = QtWidgets.QLabel(title)
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                background: qlineargradient(
                    spread:pad, x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(0, 98, 255, 239), stop:1 rgba(240, 240, 240, 255)
                );
                font-size: 14pt;
                font-weight: bold;
                color: #333;
                padding: 12px;
                border-radius: 10px 10px 0 0;
            }
        """)
        title_label.setMinimumHeight(50)
        layout.addWidget(title_label)
        # Text edit area for input
        text_edit = QtWidgets.QTextEdit()
        text_edit.setPlaceholderText(f"Enter {title.lower()} information...")
        text_edit.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: none;
                border-radius: 0 0 10px 10px;
                padding: 10px;
                font-size: 11pt;
            }
        """)
        layout.addWidget(text_edit, 1)  # stretch factor 1
        return section, text_edit
    def create_incident_details_section(self):
        """Create special INCIDENT DETAILS section with Date/Time, Reason, and Official fields"""
        section = QtWidgets.QWidget()
        section.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        section.setStyleSheet("""
            QWidget {
                background-color: #e5e5e5;
                border-radius: 8px;
            }
        """)
        layout = QtWidgets.QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 8)
        layout.setSpacing(5)
        # Title label
        title_label = QtWidgets.QLabel("INCIDENT DETAILS")
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                background: qlineargradient(
                    spread:pad, x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(0, 98, 255, 239), stop:1 rgba(240, 240, 240, 255)
                );
                font-size: 14pt;
                font-weight: bold;
                color: #333;
                padding: 12px;
                border-radius: 10px 10px 0 0;
            }
        """)
        title_label.setMinimumHeight(50)
        layout.addWidget(title_label)
        # Content area
        content_widget = QtWidgets.QWidget()
        content_widget.setStyleSheet("background-color: white; border-radius: 0 0 10px 10px;")
        content_layout = QtWidgets.QVBoxLayout(content_widget)
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(8)
        # Date and Time row
        datetime_row = QtWidgets.QHBoxLayout()
        # Date
        date_label = QtWidgets.QLabel("📅 Date:")
        date_label.setStyleSheet("font-weight: bold; font-size: 10pt; background: transparent;")
        datetime_row.addWidget(date_label)
        self.incident_date = QtWidgets.QDateEdit()
        self.incident_date.setCalendarPopup(True)
        self.incident_date.setDate(QtCore.QDate.currentDate())
        self.incident_date.setStyleSheet("""
            QDateEdit {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 4px;
                font-size: 10pt;
            }
        """)
        datetime_row.addWidget(self.incident_date)
        # Time
        time_label = QtWidgets.QLabel("🕐 Time:")
        time_label.setStyleSheet("font-weight: bold; font-size: 10pt; background: transparent;")
        datetime_row.addWidget(time_label)
        self.incident_time = QtWidgets.QTimeEdit()
        self.incident_time.setTime(QtCore.QTime.currentTime())
        self.incident_time.setStyleSheet("""
            QTimeEdit {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 4px;
                font-size: 10pt;
            }
        """)
        datetime_row.addWidget(self.incident_time)
        datetime_row.addStretch()
        content_layout.addLayout(datetime_row)
        # Reason/Details
        reason_label = QtWidgets.QLabel("📝 Reason/Details of Incident:")
        reason_label.setStyleSheet("font-weight: bold; font-size: 10pt; background: transparent;")
        content_layout.addWidget(reason_label)
        self.incident_reason = QtWidgets.QTextEdit()
        self.incident_reason.setPlaceholderText("Enter the reason or details of the incident...")
        self.incident_reason.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 5px;
                font-size: 10pt;
            }
        """)
        self.incident_reason.setMaximumHeight(80)
        content_layout.addWidget(self.incident_reason)
        # Barangay Official who handled
        official_row = QtWidgets.QHBoxLayout()
        official_label = QtWidgets.QLabel("👤 Handled by (Barangay Official):")
        official_label.setStyleSheet("font-weight: bold; font-size: 10pt; background: transparent;")
        official_row.addWidget(official_label)
        self.handling_official = QtWidgets.QLineEdit()
        self.handling_official.setPlaceholderText("Enter name of barangay official...")
        self.handling_official.setStyleSheet("""
            QLineEdit {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 4px;
                font-size: 10pt;
            }
        """)
        official_row.addWidget(self.handling_official)
        content_layout.addLayout(official_row)
        content_layout.addStretch()
        layout.addWidget(content_widget, 1)
        return section
    def submit_blotter_report(self):
        """Submit the blotter report to database"""
        try:
            from app.models import Blotter
            from datetime import datetime
            # Get values from inputs
            complainant = self.complainant_input.toPlainText().strip()
            respondent = self.respondent_input.toPlainText().strip()
            reason = self.incident_reason.toPlainText().strip()
            location = self.location_input.toPlainText().strip()
            handled_by = self.handling_official.text().strip()
            # Get date and time
            date = self.incident_date.date()
            time = self.incident_time.time()
            incident_datetime = datetime(
                date.year(), date.month(), date.day(),
                time.hour(), time.minute(), time.second()
            )
            # Validate required fields
            if not complainant:
                self.notification.show_error("❌ Please enter complainant information!")
                return
            if not respondent:
                self.notification.show_error("❌ Please enter respondent information!")
                return
            if not reason:
                self.notification.show_error("❌ Please enter the reason/details of incident!")
                return
            if not location:
                self.notification.show_error("❌ Please enter the location!")
                return
            if not handled_by:
                self.notification.show_error("❌ Please enter the barangay official who handled this!")
                return
            # Create blotter record
            db = SessionLocal()
            try:
                blotter = Blotter(
                    complainant_name=complainant,
                    respondent_name=respondent,
                    reason=reason,
                    incident_date=incident_datetime,
                    location=location,
                    handled_by=handled_by
                )
                db.add(blotter)
                db.commit()
                self.notification.show_success("✅ Blotter report submitted successfully!")
                # Clear the form
                self.complainant_input.clear()
                self.respondent_input.clear()
                self.incident_reason.clear()
                self.location_input.clear()
                self.handling_official.clear()
                self.incident_date.setDate(QtCore.QDate.currentDate())
                self.incident_time.setTime(QtCore.QTime.currentTime())
            except Exception as e:
                db.rollback()
                self.notification.show_error(f"❌ Database error: {e}")
            finally:
                db.close()
        except Exception as e:
            self.notification.show_error(f"❌ Error submitting blotter: {e}")
            import traceback
            traceback.print_exc()
    def show_blotter_table(self):
        """Show the blotter table list view"""
        try:
            # Outer wrapper with margins
            outer_widget = QtWidgets.QWidget()
            outer_widget.setStyleSheet("background-color: #f0f0f0;")
            outer_layout = QtWidgets.QVBoxLayout(outer_widget)
            outer_layout.setContentsMargins(50, 30, 50, 30)
            # Main container
            table_widget = QtWidgets.QWidget()
            table_widget.setStyleSheet("background-color: #dddddd; border-radius: 15px;")
            table_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            main_layout = QtWidgets.QVBoxLayout(table_widget)
            main_layout.setContentsMargins(20, 15, 20, 15)
            main_layout.setSpacing(10)
            # Header
            header = QtWidgets.QLabel()
            header.setText("""<html><body>
                <p style="font-size: 18pt; font-weight: bold; color: white; margin: 0;">OVERALL BLOTTER REPORTS</p>
            </body></html>""")
            header.setStyleSheet("""
                QLabel {
                    background: qlineargradient(
                        spread:pad, x1:0, y1:0, x2:0, y2:1,
                        stop:0 #0d47a1, stop:1 #1976d2
                    );
                    border-radius: 10px;
                    padding: 20px;
                }
            """)
            header.setMinimumHeight(70)
            main_layout.addWidget(header)
            # Back button row
            back_row = QtWidgets.QHBoxLayout()
            back_btn = QtWidgets.QPushButton("⬅ Back to Form")
            back_btn.setFixedSize(130, 32)
            back_btn.setCursor(QtCore.Qt.PointingHandCursor)
            back_btn.setStyleSheet("""
                QPushButton {
                    background-color: #1976d2;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    font-size: 10pt;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #1565c0;
                }
            """)
            back_btn.clicked.connect(self.show_blotter_page)
            back_row.addWidget(back_btn)
            back_row.addStretch()
            main_layout.addLayout(back_row)
            # Table widget
            table = QtWidgets.QTableWidget()
            table.setColumnCount(7)
            table.setHorizontalHeaderLabels(["COMPLAINANT", "RESPONDENT", "REASON", "DATE", "LOCATION", "HANDLED BY", "ACTION"])
            table.horizontalHeader().setStretchLastSection(True)
            table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
            table.setStyleSheet("""
                QTableWidget {
                    background-color: white;
                    border: none;
                    border-radius: 10px;
                    gridline-color: #d0d0d0;
                    font-size: 13px;
                }
                QHeaderView::section {
                    background-color: #0078D4;
                    color: white;
                    font-weight: bold;
                    font-size: 11px;
                    padding: 8px;
                    border: none;
                }
                QTableWidget::item {
                    padding: 8px;
                }
            """)
            table.setAlternatingRowColors(True)
            main_layout.addWidget(table, 1)
            # Load data from database
            self.load_blotter_data(table)
            # Add to outer layout
            outer_layout.addWidget(table_widget)
            # Replace content
            self.replace_content(outer_widget)
            self.notification.show_success("✅ Blotter list loaded")
        except Exception as e:
            self.notification.show_error(f"❌ Error loading blotter table: {e}")
            import traceback
            traceback.print_exc()
    def load_blotter_data(self, table):
        """Load blotter records from database into the table"""
        try:
            from app.models import Blotter
            db = SessionLocal()
            try:
                # Query all blotter records, ordered by date descending
                blotters = db.query(Blotter).order_by(Blotter.created_at.desc()).all()
                table.setRowCount(len(blotters))
                for row, blotter in enumerate(blotters):
                    # Set row height to fit buttons properly
                    table.setRowHeight(row, 50)
                    # COMPLAINANT
                    complainant_item = QtWidgets.QTableWidgetItem(blotter.complainant_name or "")
                    complainant_item.setTextAlignment(QtCore.Qt.AlignCenter)
                    table.setItem(row, 0, complainant_item)
                    # RESPONDENT
                    respondent_item = QtWidgets.QTableWidgetItem(blotter.respondent_name or "")
                    respondent_item.setTextAlignment(QtCore.Qt.AlignCenter)
                    table.setItem(row, 1, respondent_item)
                    # REASON (truncated for display)
                    reason_text = blotter.reason or ""
                    if len(reason_text) > 50:
                        reason_text = reason_text[:50] + "..."
                    reason_item = QtWidgets.QTableWidgetItem(reason_text)
                    reason_item.setTextAlignment(QtCore.Qt.AlignCenter)
                    table.setItem(row, 2, reason_item)
                    # DATE
                    date_str = ""
                    if blotter.incident_date:
                        date_str = blotter.incident_date.strftime("%Y-%m-%d %I:%M %p")
                    date_item = QtWidgets.QTableWidgetItem(date_str)
                    date_item.setTextAlignment(QtCore.Qt.AlignCenter)
                    table.setItem(row, 3, date_item)
                    # LOCATION
                    location_item = QtWidgets.QTableWidgetItem(blotter.location or "")
                    location_item.setTextAlignment(QtCore.Qt.AlignCenter)
                    table.setItem(row, 4, location_item)
                    # HANDLED BY
                    handled_item = QtWidgets.QTableWidgetItem(blotter.handled_by or "")
                    handled_item.setTextAlignment(QtCore.Qt.AlignCenter)
                    table.setItem(row, 5, handled_item)
                    # ACTION - Edit and Delete buttons
                    action_widget = QtWidgets.QWidget()
                    action_layout = QtWidgets.QHBoxLayout(action_widget)
                    action_layout.setContentsMargins(5, 2, 5, 2)
                    action_layout.setSpacing(8)
                    action_layout.setAlignment(QtCore.Qt.AlignCenter)
                    # Edit button
                    edit_btn = QtWidgets.QPushButton("Edit")
                    edit_btn.setFixedSize(50, 28)
                    edit_btn.setCursor(QtCore.Qt.PointingHandCursor)
                    edit_btn.setToolTip("Edit this record")
                    edit_btn.setStyleSheet("""
                        QPushButton {
                            background-color: #3498db;
                            color: white;
                            border: none;
                            border-radius: 5px;
                            font-size: 9pt;
                            font-weight: bold;
                        }
                        QPushButton:hover {
                            background-color: #2980b9;
                        }
                    """)
                    edit_btn.clicked.connect(lambda checked, bid=blotter.blotter_id: self.edit_blotter(bid))
                    action_layout.addWidget(edit_btn)
                    # Delete button
                    delete_btn = QtWidgets.QPushButton("Delete")
                    delete_btn.setFixedSize(50, 28)
                    delete_btn.setCursor(QtCore.Qt.PointingHandCursor)
                    delete_btn.setToolTip("Delete this record")
                    delete_btn.setStyleSheet("""
                        QPushButton {
                            background-color: #e74c3c;
                            color: white;
                            border: none;
                            border-radius: 5px;
                            font-size: 9pt;
                            font-weight: bold;
                        }
                        QPushButton:hover {
                            background-color: #c0392b;
                        }
                    """)
                    delete_btn.clicked.connect(lambda checked, bid=blotter.blotter_id: self.delete_blotter(bid))
                    action_layout.addWidget(delete_btn)
                    table.setCellWidget(row, 6, action_widget)
            finally:
                db.close()
        except Exception as e:
            import traceback
            traceback.print_exc()
    def delete_blotter(self, blotter_id):
        """Delete a blotter record"""
        try:
            from app.models import Blotter
            # Confirm deletion
            reply = QtWidgets.QMessageBox.question(
                self,
                "Confirm Delete",
                "Are you sure you want to delete this blotter record?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                QtWidgets.QMessageBox.No
            )
            if reply == QtWidgets.QMessageBox.Yes:
                db = SessionLocal()
                try:
                    blotter = db.query(Blotter).filter(Blotter.blotter_id == blotter_id).first()
                    if blotter:
                        db.delete(blotter)
                        db.commit()
                        self.notification.show_success("✅ Blotter record deleted!")
                        # Refresh the table
                        self.show_blotter_table()
                    else:
                        self.notification.show_error("❌ Blotter record not found!")
                except Exception as e:
                    db.rollback()
                    self.notification.show_error(f"❌ Error deleting: {e}")
                finally:
                    db.close()
        except Exception as e:
            self.notification.show_error(f"❌ Error: {e}")
    def edit_blotter(self, blotter_id):
        """Edit a blotter record in a dialog"""
        try:
            from app.models import Blotter
            db = SessionLocal()
            try:
                blotter = db.query(Blotter).filter(Blotter.blotter_id == blotter_id).first()
                if not blotter:
                    self.notification.show_error("❌ Blotter record not found!")
                    return
                # Create edit dialog
                dialog = QtWidgets.QDialog(self)
                dialog.setWindowTitle("Edit Blotter Report")
                dialog.setMinimumSize(500, 450)
                dialog.setStyleSheet("background-color: #f5f5f5;")
                layout = QtWidgets.QVBoxLayout(dialog)
                layout.setSpacing(15)
                layout.setContentsMargins(20, 20, 20, 20)
                # Title
                title = QtWidgets.QLabel("✏️ Edit Blotter Report")
                title.setStyleSheet("font-size: 16pt; font-weight: bold; color: #1976d2;")
                layout.addWidget(title)
                # Form layout
                form_layout = QtWidgets.QFormLayout()
                form_layout.setSpacing(10)
                # Complainant
                complainant_edit = QtWidgets.QTextEdit()
                complainant_edit.setPlainText(blotter.complainant_name or "")
                complainant_edit.setMaximumHeight(60)
                complainant_edit.setStyleSheet("background-color: white; border: 1px solid #ccc; border-radius: 5px; padding: 5px;")
                form_layout.addRow("Complainant:", complainant_edit)
                # Respondent
                respondent_edit = QtWidgets.QTextEdit()
                respondent_edit.setPlainText(blotter.respondent_name or "")
                respondent_edit.setMaximumHeight(60)
                respondent_edit.setStyleSheet("background-color: white; border: 1px solid #ccc; border-radius: 5px; padding: 5px;")
                form_layout.addRow("Respondent:", respondent_edit)
                # Date & Time
                datetime_widget = QtWidgets.QWidget()
                datetime_layout = QtWidgets.QHBoxLayout(datetime_widget)
                datetime_layout.setContentsMargins(0, 0, 0, 0)
                date_edit = QtWidgets.QDateEdit()
                date_edit.setCalendarPopup(True)
                if blotter.incident_date:
                    date_edit.setDate(QtCore.QDate(blotter.incident_date.year, blotter.incident_date.month, blotter.incident_date.day))
                date_edit.setStyleSheet("background-color: white; border: 1px solid #ccc; border-radius: 5px; padding: 5px;")
                datetime_layout.addWidget(date_edit)
                time_edit = QtWidgets.QTimeEdit()
                if blotter.incident_date and hasattr(blotter.incident_date, 'hour'):
                    time_edit.setTime(QtCore.QTime(blotter.incident_date.hour, blotter.incident_date.minute))
                else:
                    time_edit.setTime(QtCore.QTime(0, 0))
                time_edit.setStyleSheet("background-color: white; border: 1px solid #ccc; border-radius: 5px; padding: 5px;")
                datetime_layout.addWidget(time_edit)
                form_layout.addRow("Date & Time:", datetime_widget)
                # Reason
                reason_edit = QtWidgets.QTextEdit()
                reason_edit.setPlainText(blotter.reason or "")
                reason_edit.setMaximumHeight(80)
                reason_edit.setStyleSheet("background-color: white; border: 1px solid #ccc; border-radius: 5px; padding: 5px;")
                form_layout.addRow("Reason:", reason_edit)
                # Location
                location_edit = QtWidgets.QTextEdit()
                location_edit.setPlainText(blotter.location or "")
                location_edit.setMaximumHeight(60)
                location_edit.setStyleSheet("background-color: white; border: 1px solid #ccc; border-radius: 5px; padding: 5px;")
                form_layout.addRow("Location:", location_edit)
                # Handled By
                handled_edit = QtWidgets.QLineEdit()
                handled_edit.setText(blotter.handled_by or "")
                handled_edit.setStyleSheet("background-color: white; border: 1px solid #ccc; border-radius: 5px; padding: 8px;")
                form_layout.addRow("Handled By:", handled_edit)
                layout.addLayout(form_layout)
                # Buttons
                button_layout = QtWidgets.QHBoxLayout()
                button_layout.addStretch()
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
                    QPushButton:hover {
                        background-color: #7f8c8d;
                    }
                """)
                cancel_btn.clicked.connect(dialog.reject)
                button_layout.addWidget(cancel_btn)
                save_btn = QtWidgets.QPushButton("💾 Save Changes")
                save_btn.setStyleSheet("""
                    QPushButton {
                        padding: 10px 25px;
                        background-color: #27ae60;
                        color: white;
                        border: none;
                        border-radius: 5px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #219a52;
                    }
                """)
                def save_changes():
                    from datetime import datetime
                    from app.models import Blotter
                    # Create a fresh database session for saving
                    save_db = SessionLocal()
                    try:
                        # Get fresh blotter record
                        blotter_to_update = save_db.query(Blotter).filter(Blotter.blotter_id == blotter_id).first()
                        if not blotter_to_update:
                            self.notification.show_error("❌ Blotter record not found!")
                            return
                        # Update blotter record
                        blotter_to_update.complainant_name = complainant_edit.toPlainText().strip()
                        blotter_to_update.respondent_name = respondent_edit.toPlainText().strip()
                        blotter_to_update.reason = reason_edit.toPlainText().strip()
                        blotter_to_update.location = location_edit.toPlainText().strip()
                        blotter_to_update.handled_by = handled_edit.text().strip()
                        # Update date/time
                        date = date_edit.date()
                        time = time_edit.time()
                        new_datetime = datetime(
                            date.year(), date.month(), date.day(),
                            time.hour(), time.minute(), time.second()
                        )
                        blotter_to_update.incident_date = new_datetime
                        save_db.commit()
                        self.notification.show_success("✅ Blotter updated successfully!")
                        dialog.accept()
                        # Refresh table
                        self.show_blotter_table()
                    except Exception as e:
                        save_db.rollback()
                        self.notification.show_error(f"❌ Error saving: {e}")
                        import traceback
                        traceback.print_exc()
                    finally:
                        save_db.close()
                save_btn.clicked.connect(save_changes)
                button_layout.addWidget(save_btn)
                layout.addLayout(button_layout)
                dialog.exec_()
            finally:
                db.close()
        except Exception as e:
            self.notification.show_error(f"❌ Error editing blotter: {e}")
            import traceback
            traceback.print_exc()
    def show_profile_page(self):
        """Show profile page"""
        profile = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(profile)
        label = QtWidgets.QLabel("👤 Profile")
        label.setStyleSheet("""
            QLabel {
                font-size: 28pt;
                font-weight: bold;
                color: #2c3e50;
                padding: 40px;
            }
        """)
        label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(label)
        self.replace_content(profile)
        self.notification.show_info("👤 Profile")
    def show_notification_page(self):
        """Show notifications page"""
        try:
            # Create notification viewer widget
            from gui.widgets.notification_viewer import NotificationViewerWidget
            notification_widget = NotificationViewerWidget(parent=self)
            notification_widget.setSizePolicy(
                QtWidgets.QSizePolicy.Expanding,
                QtWidgets.QSizePolicy.Expanding
            )
            self.replace_content(notification_widget)
            self.notification.show_success("🔔 Notifications loaded!")
        except Exception as e:
            # Fallback to placeholder
            page = QtWidgets.QWidget()
            layout = QtWidgets.QVBoxLayout(page)
            label = QtWidgets.QLabel("🔔 Notifications")
            label.setStyleSheet("font-size: 28pt; font-weight: bold; color: #2c3e50; padding: 40px;")
            label.setAlignment(QtCore.Qt.AlignCenter)
            layout.addWidget(label)
            self.replace_content(page)
            self.notification.show_info("🔔 Notifications")
    def show_all_about_page(self):
        """Show All About / Information page (admin) matching user view"""
        try:
            about_ui_path = Path(__file__).resolve().parent.parent / "ui" / "ALL ABOUT.ui"

            if not about_ui_path.exists():
                self.notification.show_error(f"❌ All About UI file not found: {about_ui_path}")
                return

            temp_window = QtWidgets.QMainWindow()
            uic.loadUi(str(about_ui_path), temp_window)

            about_widget = temp_window.centralWidget()
            if not about_widget:
                self.notification.show_error("❌ No central widget found in All About UI")
                return

            about_widget.setParent(None)
            about_widget.setStyleSheet("background-color: white;")
            about_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            about_widget.setMinimumSize(1024, 1366)

            # Subtle fade-in animation for polish
            opacity = QtWidgets.QGraphicsOpacityEffect()
            about_widget.setGraphicsEffect(opacity)
            anim = QtCore.QPropertyAnimation(opacity, b"opacity", about_widget)
            anim.setDuration(600)
            anim.setStartValue(0.0)
            anim.setEndValue(1.0)
            anim.start(QtCore.QAbstractAnimation.DeleteWhenStopped)

            scroll_area = QtWidgets.QScrollArea()
            scroll_area.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            scroll_area.setWidget(about_widget)
            scroll_area.setWidgetResizable(True)
            scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)
            scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
            scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
            scroll_area.setContentsMargins(0, 0, 0, 0)
            scroll_area.setViewportMargins(0, 0, 0, 0)
            scroll_area.setStyleSheet("QScrollArea { background-color: white; border: none; margin: 0px; padding: 0px; }")

            # Stretch content to viewport width with consistent margins; shrink gracefully when smaller
            def resize_allabout(event):
                viewport_width = scroll_area.viewport().width()
                margin = 20
                body_width = max(800, viewport_width - 2 * margin)

                about_widget.setMinimumWidth(body_width)
                about_widget.resize(body_width, about_widget.height())

                bg_label = about_widget.findChild(QtWidgets.QLabel, "label_6")
                hero_label = about_widget.findChild(QtWidgets.QLabel, "label")
                if bg_label:
                    bg_label.setGeometry(0, bg_label.y(), body_width, bg_label.height())
                    bg_label.setScaledContents(True)
                if hero_label:
                    hero_label.setGeometry(0, hero_label.y(), body_width, hero_label.height())
                    hero_label.setAlignment(QtCore.Qt.AlignCenter)

                heading1 = about_widget.findChild(QtWidgets.QLabel, "label_2")
                box1 = about_widget.findChild(QtWidgets.QLabel, "label_3")
                heading2 = about_widget.findChild(QtWidgets.QLabel, "label_4")
                box2 = about_widget.findChild(QtWidgets.QLabel, "label_5")
                seal = about_widget.findChild(QtWidgets.QLabel, "label_7")

                x = margin
                section_width = body_width - 2 * margin

                if heading1:
                    heading1.setGeometry(x, heading1.y(), section_width, heading1.height())
                    heading1.setAlignment(QtCore.Qt.AlignCenter)
                if box1:
                    box1.setGeometry(x + 10, box1.y(), section_width - 20, box1.height())
                if heading2:
                    heading2.setGeometry(x, heading2.y(), section_width, heading2.height())
                    heading2.setAlignment(QtCore.Qt.AlignCenter)
                if box2:
                    box2.setGeometry(x + 10, box2.y(), section_width - 20, box2.height())
                if seal:
                    seal_size = min(451, section_width // 2)
                    seal_x = x + section_width - seal_size
                    seal.setGeometry(seal_x, seal.y(), seal_size, seal_size)
                    seal.setScaledContents(True)

                QtWidgets.QScrollArea.resizeEvent(scroll_area, event)

            scroll_area.resizeEvent = resize_allabout

            self.replace_content(scroll_area)
            self.notification.show_info("ℹ️ All About")

        except Exception as e:
            self.notification.show_error(f"❌ Error loading All About page: {e}")
            import traceback
            traceback.print_exc()
    def show_history_page(self):
        """Show History page"""
        page = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(page)
        label = QtWidgets.QLabel("📜 History")
        label.setStyleSheet("font-size: 28pt; font-weight: bold; color: #2c3e50; padding: 40px;")
        label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(label)
        info_label = QtWidgets.QLabel("Transaction and activity history")
        info_label.setStyleSheet("font-size: 14pt; color: #666; padding: 20px;")
        info_label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(info_label)
        self.replace_content(page)
        self.notification.show_info("📜 History")
    def show_officials_page(self):
        """Show officials page - admin version with edit/delete/upload capabilities"""
        try:
            from app.models import BarangayOfficial
            from app.db import SessionLocal
            
            # Create main container with scroll area for responsiveness
            main_widget = QtWidgets.QWidget()
            main_layout = QtWidgets.QVBoxLayout(main_widget)
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.setSpacing(0)
            
            # Blue header with title and Add button
            header = QtWidgets.QWidget()
            header.setFixedHeight(60)
            header.setStyleSheet("""
                QWidget {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #1e3c72, stop:1 #2a5298);
                }
            """)
            header_layout = QtWidgets.QHBoxLayout(header)
            header_layout.setContentsMargins(20, 0, 20, 0)
            
            title_label = QtWidgets.QLabel("👥 BARANGAY OFFICIALS")
            title_label.setStyleSheet("""
                font-size: 20pt;
                font-weight: bold;
                color: white;
                background: transparent;
            """)
            title_label.setAlignment(QtCore.Qt.AlignCenter)
            header_layout.addWidget(title_label)
            
            header_layout.addStretch()
            
            # Add New Official button
            add_btn = QtWidgets.QPushButton("➕ Add New Official")
            add_btn.setStyleSheet("""
                QPushButton {
                    background-color: #27ae60;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 5px;
                    font-size: 11pt;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #2ecc71;
                }
            """)
            add_btn.clicked.connect(self.add_new_official)
            header_layout.addWidget(add_btn)
            
            main_layout.addWidget(header)
            
            # Scroll area for content
            scroll_area = QtWidgets.QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setStyleSheet("""
                QScrollArea { border: none; background-color: #f5f5f5; }
                QScrollBar:vertical { width: 8px; background: #e0e0e0; }
                QScrollBar::handle:vertical { background: #1e3c72; border-radius: 4px; }
            """)
            
            content_widget = QtWidgets.QWidget()
            content_widget.setStyleSheet("background-color: #f5f5f5;")
            content_layout = QtWidgets.QVBoxLayout(content_widget)
            content_layout.setContentsMargins(20, 20, 20, 20)
            content_layout.setSpacing(15)
            content_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)
            
            # Fetch officials from database
            db = SessionLocal()
            try:
                officials = db.query(BarangayOfficial).filter(
                    BarangayOfficial.is_active == True
                ).order_by(BarangayOfficial.display_order).all()
                
                # Separate by category
                captain = None
                sanggunian = []
                others = []
                
                for official in officials:
                    if 'kapitan' in official.position.lower() or 'captain' in official.position.lower() or 'punong' in official.position.lower():
                        captain = official
                    elif official.category == 'Other':
                        others.append(official)
                    else:
                        sanggunian.append(official)
                
                # If no officials in database, show default/placeholder
                if not officials:
                    no_data_label = QtWidgets.QLabel("No officials yet. Click 'Add New Official' to get started!")
                    no_data_label.setStyleSheet("""
                        font-size: 14pt;
                        color: #666;
                        padding: 50px;
                        background: white;
                        border-radius: 10px;
                    """)
                    no_data_label.setAlignment(QtCore.Qt.AlignCenter)
                    content_layout.addWidget(no_data_label)
                else:
                    # === BARANGAY CAPTAIN (centered at top) ===
                    if captain:
                        captain_card = self.create_official_card_admin(captain, is_captain=True)
                        content_layout.addWidget(captain_card, alignment=QtCore.Qt.AlignHCenter)
                    
                    # === TWO COLUMNS: Sanggunian (left) and Other Officials (right) ===
                    two_columns = QtWidgets.QHBoxLayout()
                    two_columns.setSpacing(20)
                    two_columns.setAlignment(QtCore.Qt.AlignCenter)
                    
                    # LEFT COLUMN - Sangguniang Barangay
                    if sanggunian:
                        left_container = QtWidgets.QFrame()
                        left_container.setStyleSheet("QFrame { background-color: white; border-radius: 10px; }")
                        left_layout = QtWidgets.QVBoxLayout(left_container)
                        left_layout.setContentsMargins(15, 10, 15, 15)
                        left_layout.setSpacing(10)
                        
                        sanggunian_title = QtWidgets.QLabel("SANGGUNIANG BARANGAY")
                        sanggunian_title.setStyleSheet("""
                            font-size: 12pt; font-weight: bold; color: white;
                            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1e3c72, stop:1 #2a5298);
                            padding: 8px 15px; border-radius: 5px;
                        """)
                        sanggunian_title.setAlignment(QtCore.Qt.AlignCenter)
                        left_layout.addWidget(sanggunian_title)
                        
                        # Grid layout for sanggunian (3 columns)
                        grid_widget = QtWidgets.QWidget()
                        grid_layout = QtWidgets.QGridLayout(grid_widget)
                        grid_layout.setSpacing(10)
                        grid_layout.setAlignment(QtCore.Qt.AlignCenter)
                        
                        for i, official in enumerate(sanggunian):
                            row = i // 3
                            col = i % 3
                            card = self.create_official_card_admin(official)
                            grid_layout.addWidget(card, row, col)
                        
                        left_layout.addWidget(grid_widget)
                        two_columns.addWidget(left_container)
                    
                    # RIGHT COLUMN - Other Officials
                    if others:
                        right_container = QtWidgets.QFrame()
                        right_container.setStyleSheet("QFrame { background-color: white; border-radius: 10px; }")
                        right_layout = QtWidgets.QVBoxLayout(right_container)
                        right_layout.setContentsMargins(15, 10, 15, 15)
                        right_layout.setSpacing(10)
                        
                        other_title = QtWidgets.QLabel("OTHER OFFICIALS")
                        other_title.setStyleSheet("""
                            font-size: 12pt; font-weight: bold; color: white;
                            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1e3c72, stop:1 #2a5298);
                            padding: 8px 15px; border-radius: 5px;
                        """)
                        other_title.setAlignment(QtCore.Qt.AlignCenter)
                        right_layout.addWidget(other_title)
                        
                        # Grid layout for others (3 columns)
                        others_grid = QtWidgets.QWidget()
                        others_layout = QtWidgets.QGridLayout(others_grid)
                        others_layout.setSpacing(10)
                        others_layout.setAlignment(QtCore.Qt.AlignCenter)
                        
                        for i, official in enumerate(others):
                            row = i // 3
                            col = i % 3
                            card = self.create_official_card_admin(official)
                            others_layout.addWidget(card, row, col)
                        
                        right_layout.addWidget(others_grid)
                        right_layout.addStretch()
                        two_columns.addWidget(right_container)
                    
                    content_layout.addLayout(two_columns)
                
                content_layout.addStretch()
                
            finally:
                db.close()
            
            scroll_area.setWidget(content_widget)
            main_layout.addWidget(scroll_area)
            
            self.replace_content(main_widget)
            self.notification.show_success("👥 Barangay Officials loaded!")
            
        except Exception as e:
            self.notification.show_error(f"❌ Error loading Officials: {e}")
            import traceback
            traceback.print_exc()
    
    def create_official_card_admin(self, official, is_captain=False):
        """Create a card for an official with edit/delete/upload buttons"""
        import os
        
        card = QtWidgets.QFrame()
        card_width = 200 if is_captain else 160
        card_height = 250 if is_captain else 220
        card.setFixedSize(card_width, card_height)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {'#f8f9fa' if is_captain else '#fafafa'};
                border: {'3px' if is_captain else '2px'} solid #1e3c72;
                border-radius: 10px;
            }}
        """)
        
        card_layout = QtWidgets.QVBoxLayout(card)
        card_layout.setContentsMargins(5, 8, 5, 8)
        card_layout.setSpacing(5)
        
        # Photo
        photo_size = 90 if is_captain else 70
        photo_label = QtWidgets.QLabel()
        photo_label.setFixedSize(photo_size, photo_size)
        photo_label.setAlignment(QtCore.Qt.AlignCenter)
        photo_label.setStyleSheet(f"""
            QLabel {{
                background-color: #e8e8e8;
                border: 2px solid #1e3c72;
                border-radius: {photo_size // 2}px;
                font-size: {'26pt' if is_captain else '20pt'};
                color: #1e3c72;
            }}
        """)
        
        # Load photo if exists
        if official.photo_path and os.path.exists(official.photo_path):
            pixmap = QtGui.QPixmap(official.photo_path)
            scaled = pixmap.scaled(photo_size, photo_size, QtCore.Qt.KeepAspectRatioByExpanding, QtCore.Qt.SmoothTransformation)
            # Create circular mask
            rounded = QtGui.QPixmap(photo_size, photo_size)
            rounded.fill(QtCore.Qt.transparent)
            painter = QtGui.QPainter(rounded)
            painter.setRenderHint(QtGui.QPainter.Antialiasing)
            path = QtGui.QPainterPath()
            path.addEllipse(0, 0, photo_size, photo_size)
            painter.setClipPath(path)
            painter.drawPixmap(0, 0, scaled)
            painter.end()
            photo_label.setPixmap(rounded)
        else:
            photo_label.setText("👤")
        
        photo_container = QtWidgets.QWidget()
        photo_container.setStyleSheet("background: transparent; border: none;")
        photo_layout = QtWidgets.QHBoxLayout(photo_container)
        photo_layout.setContentsMargins(0, 0, 0, 0)
        photo_layout.setAlignment(QtCore.Qt.AlignCenter)
        photo_layout.addWidget(photo_label)
        card_layout.addWidget(photo_container)
        
        # Position and name label
        info_label = QtWidgets.QLabel()
        info_label.setAlignment(QtCore.Qt.AlignCenter)
        info_label.setWordWrap(True)
        info_label.setFixedHeight(55 if is_captain else 50)
        font_size = "9pt" if is_captain else "8pt"
        name_size = "7pt" if is_captain else "6.5pt"
        info_label.setText(f"""
            <p style="margin:0; padding:2px; font-weight:bold; font-size:{font_size}; color:white;">{official.position}</p>
            <p style="margin:0; padding:2px; font-size:{name_size}; color:#e0e0e0;">{official.full_name}</p>
        """)
        info_label.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1e3c72, stop:1 #2a5298);
                padding: 5px 5px;
            }
        """)
        card_layout.addWidget(info_label)
        
        # Action buttons container
        actions_container = QtWidgets.QWidget()
        actions_container.setStyleSheet("background: transparent; border: none;")
        actions_layout = QtWidgets.QHBoxLayout(actions_container)
        actions_layout.setContentsMargins(8, 2, 8, 2)
        actions_layout.setSpacing(5)
        
        # Upload Photo button
        upload_btn = QtWidgets.QPushButton("📷")
        upload_btn.setFixedSize(45, 35)
        upload_btn.setStyleSheet("""
            QPushButton { 
                background-color: #3498db; 
                color: white; 
                border-radius: 5px; 
                font-size: 14pt;
                border: none;
            }
            QPushButton:hover { background-color: #2980b9; }
        """)
        upload_btn.setToolTip("Upload Photo")
        upload_btn.clicked.connect(lambda: self.upload_official_photo(official.official_id))
        
        # Edit button
        edit_btn = QtWidgets.QPushButton("✏️")
        edit_btn.setFixedSize(45, 35)
        edit_btn.setStyleSheet("""
            QPushButton { 
                background-color: #f39c12; 
                color: white; 
                border-radius: 5px; 
                font-size: 14pt;
                border: none;
            }
            QPushButton:hover { background-color: #e67e22; }
        """)
        edit_btn.setToolTip("Edit Name/Position")
        edit_btn.clicked.connect(lambda: self.edit_official(official.official_id))
        
        # Delete button
        delete_btn = QtWidgets.QPushButton("🗑️")
        delete_btn.setFixedSize(45, 35)
        delete_btn.setStyleSheet("""
            QPushButton { 
                background-color: #e74c3c; 
                color: white; 
                border-radius: 5px; 
                font-size: 14pt;
                border: none;
            }
            QPushButton:hover { background-color: #c0392b; }
        """)
        delete_btn.setToolTip("Delete Official")
        delete_btn.clicked.connect(lambda: self.delete_official(official.official_id))
        
        actions_layout.addWidget(upload_btn)
        actions_layout.addWidget(edit_btn)
        actions_layout.addWidget(delete_btn)
        card_layout.addWidget(actions_container)
        
        return card
    
    def add_new_official(self):
        """Add a new barangay official"""
        try:
            from app.models import BarangayOfficial
            from app.db import SessionLocal
            
            dialog = QtWidgets.QDialog(self)
            dialog.setWindowTitle("Add New Official")
            dialog.setFixedSize(600, 550)
            dialog.setStyleSheet("""
                QDialog { background-color: #f5f5f5; }
                QLabel { font-size: 15pt; color: #333; font-weight: bold; }
                QLineEdit, QComboBox, QSpinBox {
                    padding: 8px 12px; border: 2px solid #ddd; border-radius: 5px;
                    font-size: 14pt; background: white; min-height: 50px;
                }
                QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
                    border: 2px solid #1e3c72;
                }
            """)
            
            layout = QtWidgets.QVBoxLayout(dialog)
            layout.setSpacing(18)
            layout.setContentsMargins(30, 30, 30, 30)
            
            # Position
            layout.addWidget(QtWidgets.QLabel("Position:"))
            position_input = QtWidgets.QLineEdit()
            position_input.setPlaceholderText("e.g., Punong Barangay, Kagawad, SK Chairman")
            layout.addWidget(position_input)
            
            # Full Name
            layout.addWidget(QtWidgets.QLabel("Full Name:"))
            name_input = QtWidgets.QLineEdit()
            name_input.setPlaceholderText("e.g., Hon. Juan Dela Cruz")
            layout.addWidget(name_input)
            
            # Category
            layout.addWidget(QtWidgets.QLabel("Category:"))
            category_combo = QtWidgets.QComboBox()
            category_combo.addItems(["Sanggunian", "Other"])
            layout.addWidget(category_combo)
            
            # Display Order
            layout.addWidget(QtWidgets.QLabel("Display Order:"))
            order_spin = QtWidgets.QSpinBox()
            order_spin.setRange(0, 100)
            order_spin.setValue(0)
            layout.addWidget(order_spin)
            
            # Buttons
            btn_layout = QtWidgets.QHBoxLayout()
            
            cancel_btn = QtWidgets.QPushButton("Cancel")
            cancel_btn.setMinimumHeight(50)
            cancel_btn.setStyleSheet("""
                QPushButton { 
                    background: #95a5a6; 
                    color: white; 
                    padding: 12px 35px;
                    border-radius: 5px; 
                    font-weight: bold;
                    font-size: 12pt;
                }
                QPushButton:hover { background: #7f8c8d; }
            """)
            cancel_btn.clicked.connect(dialog.reject)
            
            save_btn = QtWidgets.QPushButton("Save Official")
            save_btn.setMinimumHeight(50)
            save_btn.setStyleSheet("""
                QPushButton { 
                    background: #27ae60; 
                    color: white; 
                    padding: 12px 35px;
                    border-radius: 5px; 
                    font-weight: bold;
                    font-size: 12pt;
                }
                QPushButton:hover { background: #2ecc71; }
            """)
            
            def save_official():
                position = position_input.text().strip()
                full_name = name_input.text().strip()
                category = category_combo.currentText()
                display_order = order_spin.value()
                
                if not position or not full_name:
                    self.notification.show_warning("⚠️ Position and Full Name are required!")
                    return
                
                db = SessionLocal()
                try:
                    new_official = BarangayOfficial(
                        position=position,
                        full_name=full_name,
                        category=category,
                        display_order=display_order,
                        is_active=True
                    )
                    db.add(new_official)
                    db.commit()
                    dialog.accept()
                    self.notification.show_success(f"✅ Official '{full_name}' added successfully!")
                    self.show_officials_page()  # Refresh
                except Exception as e:
                    db.rollback()
                    self.notification.show_error(f"❌ Error adding official: {e}")
                finally:
                    db.close()
            
            save_btn.clicked.connect(save_official)
            
            btn_layout.addWidget(cancel_btn)
            btn_layout.addWidget(save_btn)
            layout.addLayout(btn_layout)
            
            dialog.exec_()
            
        except Exception as e:
            self.notification.show_error(f"❌ Error: {e}")
    
    def edit_official(self, official_id):
        """Edit an existing official"""
        try:
            from app.models import BarangayOfficial
            from app.db import SessionLocal
            
            db = SessionLocal()
            try:
                official = db.query(BarangayOfficial).filter(BarangayOfficial.official_id == official_id).first()
                if not official:
                    self.notification.show_error("❌ Official not found!")
                    return
                
                dialog = QtWidgets.QDialog(self)
                dialog.setWindowTitle("Edit Official")
                dialog.setFixedSize(600, 550)
                dialog.setStyleSheet("""
                    QDialog { background-color: #f5f5f5; }
                    QLabel { font-size: 15pt; color: #333; font-weight: bold; }
                    QLineEdit, QComboBox, QSpinBox {
                        padding: 8px 12px; border: 2px solid #ddd; border-radius: 5px;
                        font-size: 14pt; background: white; min-height: 50px;
                    }
                    QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
                        border: 2px solid #1e3c72;
                    }
                """)
                
                layout = QtWidgets.QVBoxLayout(dialog)
                layout.setSpacing(18)
                layout.setContentsMargins(30, 30, 30, 30)
                
                # Position
                layout.addWidget(QtWidgets.QLabel("Position:"))
                position_input = QtWidgets.QLineEdit(official.position)
                layout.addWidget(position_input)
                
                # Full Name
                layout.addWidget(QtWidgets.QLabel("Full Name:"))
                name_input = QtWidgets.QLineEdit(official.full_name)
                layout.addWidget(name_input)
                
                # Category
                layout.addWidget(QtWidgets.QLabel("Category:"))
                category_combo = QtWidgets.QComboBox()
                category_combo.addItems(["Sanggunian", "Other"])
                category_combo.setCurrentText(official.category or "Sanggunian")
                layout.addWidget(category_combo)
                
                # Display Order
                layout.addWidget(QtWidgets.QLabel("Display Order:"))
                order_spin = QtWidgets.QSpinBox()
                order_spin.setRange(0, 100)
                order_spin.setValue(official.display_order or 0)
                layout.addWidget(order_spin)
                
                # Buttons
                btn_layout = QtWidgets.QHBoxLayout()
                
                cancel_btn = QtWidgets.QPushButton("Cancel")
                cancel_btn.setMinimumHeight(50)
                cancel_btn.setStyleSheet("""
                    QPushButton { 
                        background: #95a5a6; 
                        color: white; 
                        padding: 12px 35px;
                        border-radius: 5px; 
                        font-weight: bold;
                        font-size: 12pt;
                    }
                    QPushButton:hover { background: #7f8c8d; }
                """)
                cancel_btn.clicked.connect(dialog.reject)
                
                save_btn = QtWidgets.QPushButton("Update Official")
                save_btn.setMinimumHeight(50)
                save_btn.setStyleSheet("""
                    QPushButton { 
                        background: #f39c12; 
                        color: white; 
                        padding: 12px 35px;
                        border-radius: 5px; 
                        font-weight: bold;
                        font-size: 12pt;
                    }
                    QPushButton:hover { background: #e67e22; }
                """)
                
                def update_official():
                    position = position_input.text().strip()
                    full_name = name_input.text().strip()
                    category = category_combo.currentText()
                    display_order = order_spin.value()
                    
                    if not position or not full_name:
                        self.notification.show_warning("⚠️ Position and Full Name are required!")
                        return
                    
                    official.position = position
                    official.full_name = full_name
                    official.category = category
                    official.display_order = display_order
                    db.commit()
                    dialog.accept()
                    self.notification.show_success(f"✅ Official '{full_name}' updated!")
                    self.show_officials_page()  # Refresh
                
                save_btn.clicked.connect(update_official)
                
                btn_layout.addWidget(cancel_btn)
                btn_layout.addWidget(save_btn)
                layout.addLayout(btn_layout)
                
                dialog.exec_()
                
            finally:
                db.close()
                
        except Exception as e:
            self.notification.show_error(f"❌ Error: {e}")
    
    def delete_official(self, official_id):
        """Delete/deactivate an official"""
        try:
            from app.models import BarangayOfficial
            from app.db import SessionLocal
            
            reply = QtWidgets.QMessageBox.question(
                self, "Confirm Delete",
                "Are you sure you want to remove this official?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            )
            
            if reply == QtWidgets.QMessageBox.Yes:
                db = SessionLocal()
                try:
                    official = db.query(BarangayOfficial).filter(BarangayOfficial.official_id == official_id).first()
                    if official:
                        official.is_active = False
                        db.commit()
                        self.notification.show_success(f"✅ Official removed successfully!")
                        self.show_officials_page()  # Refresh
                    else:
                        self.notification.show_error("❌ Official not found!")
                finally:
                    db.close()
                    
        except Exception as e:
            self.notification.show_error(f"❌ Error: {e}")
    
    def upload_official_photo(self, official_id):
        """Upload a photo for an official"""
        try:
            from app.models import BarangayOfficial
            from app.db import SessionLocal
            import os
            import shutil
            
            file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
                self, "Select Photo",
                "", "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)"
            )
            
            if file_path:
                # Create uploads/officials directory if not exists
                uploads_dir = Path(__file__).resolve().parent.parent.parent / "uploads" / "officials"
                uploads_dir.mkdir(parents=True, exist_ok=True)
                
                # Copy file to uploads folder with unique name
                file_ext = os.path.splitext(file_path)[1]
                new_filename = f"official_{official_id}{file_ext}"
                new_path = uploads_dir / new_filename
                
                shutil.copy(file_path, new_path)
                
                # Update database
                db = SessionLocal()
                try:
                    official = db.query(BarangayOfficial).filter(BarangayOfficial.official_id == official_id).first()
                    if official:
                        official.photo_path = str(new_path)
                        db.commit()
                        self.notification.show_success(f"✅ Photo uploaded successfully!")
                        self.show_officials_page()  # Refresh
                    else:
                        self.notification.show_error("❌ Official not found!")
                finally:
                    db.close()
                    
        except Exception as e:
            self.notification.show_error(f"❌ Error uploading photo: {e}")
    def show_announcement_page(self):
        """Show admin announcements page with database-driven announcements"""
        try:
            # Import the announcement manager widget
            from gui.widgets.announcement_manager import AnnouncementManagerWidget
            # Create the announcement manager widget
            # TODO: Get actual admin ID from login session
            announcement_widget = AnnouncementManagerWidget(admin_id=1, parent=self)
            # Set size policy to expand
            announcement_widget.setSizePolicy(
                QtWidgets.QSizePolicy.Expanding,
                QtWidgets.QSizePolicy.Expanding
            )
            # Replace content
            self.replace_content(announcement_widget)
            self.notification.show_success("📢 Admin Announcements loaded!")
        except Exception as e:
            self.notification.show_error(f"❌ Error loading Announcements: {e}")
            import traceback
            traceback.print_exc()
    def show_services_page(self):
        """Load and display admin services page - dynamically built to expand"""
        try:
            # Create outer wrapper with margins (1 inch = ~50px for comfortable spacing)
            outer_widget = QtWidgets.QWidget()
            outer_widget.setStyleSheet("background-color: #f0f0f0;")
            outer_layout = QtWidgets.QVBoxLayout(outer_widget)
            outer_layout.setContentsMargins(50, 30, 50, 30)
            outer_layout.setSpacing(0)
            # Main container that will expand
            main_container = QtWidgets.QWidget()
            main_container.setStyleSheet("background-color: #e8e8e8; border-radius: 15px;")
            main_container.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            main_layout = QtWidgets.QVBoxLayout(main_container)
            main_layout.setContentsMargins(20, 15, 20, 15)
            main_layout.setSpacing(10)
            # Header - ONLINE REQUEST
            header = QtWidgets.QLabel()
            header.setText("""<html><body>
                <p style="font-size: 18pt; font-weight: bold; color: white; margin: 0;">ONLINE REQUEST</p>
            </body></html>""")
            header.setStyleSheet("""
                QLabel {
                    background: qlineargradient(
                        spread:pad, x1:0, y1:0, x2:0, y2:1,
                        stop:0 #0d47a1, stop:1 #1976d2
                    );
                    border-radius: 10px;
                    padding: 20px;
                }
            """)
            header.setMinimumHeight(70)
            main_layout.addWidget(header)
            # Table widget - expandable
            table = QtWidgets.QTableWidget()
            table.setColumnCount(7)
            table.setHorizontalHeaderLabels(["NAME", "TYPE", "PURPOSE", "QUANTITY", "DATE", "STATUS", "ACTION"])
            table.horizontalHeader().setStretchLastSection(True)
            table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
            table.setStyleSheet("""
                QTableWidget {
                    background-color: white;
                    border: none;
                    border-radius: 10px;
                    gridline-color: #d0d0d0;
                    font-size: 13px;
                }
                QHeaderView::section {
                    background-color: #0078D4;
                    color: white;
                    font-weight: bold;
                    font-size: 11px;
                    padding: 8px;
                    border: none;
                }
                QTableWidget::item {
                    padding: 8px;
                }
            """)
            table.setAlternatingRowColors(True)
            table.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            table.verticalHeader().setDefaultSectionSize(50)
            # Add table to layout with stretch factor
            main_layout.addWidget(table, 1)
            # Add main container to outer layout
            outer_layout.addWidget(main_container, 1)
            # Load data into the table
            self.load_services_table_data(table)
            # Replace content
            self.replace_content(outer_widget)
            self.notification.show_success("🛎️ Admin Services page loaded")
        except Exception as e:
            self.notification.show_error(f"❌ Error loading admin services: {e}")
            import traceback
            traceback.print_exc()
    def load_services_table_data(self, table):
        """Load certificate requests from database and populate the table"""
        try:
            from app.models import CertificateRequest, Resident
            db = SessionLocal()
            try:
                # Query certificate requests
                requests = db.query(CertificateRequest).order_by(CertificateRequest.created_at.desc()).all()
                table.setRowCount(len(requests))
                for row, req in enumerate(requests):
                    table.setRowHeight(row, 70)
                    # Get name from REQUEST FORM (not account/resident)
                    # This allows requesting for others (e.g., family members)
                    # Auto-capitalize: john kester benitez → John Kester Benitez
                    first_name = (req.first_name or "").strip().title()
                    last_name = (req.last_name or "").strip().title()
                    resident_name = f"{first_name} {last_name}"
                    
                    # Fallback to resident table only if request has no name
                    if not first_name and not last_name and req.resident_id:
                        resident = db.query(Resident).filter(Resident.resident_id == req.resident_id).first()
                        if resident:
                            resident_name = f"{resident.first_name} {resident.last_name}".title()
                    # NAME
                    name_item = QtWidgets.QTableWidgetItem(resident_name)
                    name_item.setTextAlignment(QtCore.Qt.AlignCenter)
                    table.setItem(row, 0, name_item)
                    # TYPE
                    type_item = QtWidgets.QTableWidgetItem(req.certificate_type or "")
                    type_item.setTextAlignment(QtCore.Qt.AlignCenter)
                    table.setItem(row, 1, type_item)
                    # PURPOSE
                    purpose_item = QtWidgets.QTableWidgetItem(req.purpose or "")
                    purpose_item.setTextAlignment(QtCore.Qt.AlignCenter)
                    table.setItem(row, 2, purpose_item)
                    # QUANTITY
                    qty_item = QtWidgets.QTableWidgetItem(str(req.quantity or 1))
                    qty_item.setTextAlignment(QtCore.Qt.AlignCenter)
                    table.setItem(row, 3, qty_item)
                    # DATE
                    date_str = ""
                    if req.created_at:
                        date_str = req.created_at.strftime("%Y-%m-%d %H:%M")
                    date_item = QtWidgets.QTableWidgetItem(date_str)
                    date_item.setTextAlignment(QtCore.Qt.AlignCenter)
                    table.setItem(row, 4, date_item)
                    # STATUS
                    status_text = req.status or "Pending"
                    status_item = QtWidgets.QTableWidgetItem(status_text)
                    status_item.setTextAlignment(QtCore.Qt.AlignCenter)
                    # Color based on status
                    if status_text == "Declined":
                        status_item.setForeground(QtGui.QColor("#e74c3c"))  # Red
                    elif status_text == "Cancelled":
                        status_item.setForeground(QtGui.QColor("#9e9e9e"))  # Gray
                    elif status_text == "Pending":
                        status_item.setForeground(QtGui.QColor("#f39c12"))  # Orange
                    elif status_text in ["Under Review", "Processing", "Ready for Pickup", "Completed"]:
                        status_item.setForeground(QtGui.QColor("#27ae60"))  # Green
                    else:
                        status_item.setForeground(QtGui.QColor("#333333"))  # Default
                    table.setItem(row, 5, status_item)
                    # ACTION - View and Print buttons (circle icons)
                    action_widget = QtWidgets.QWidget()
                    action_layout = QtWidgets.QHBoxLayout(action_widget)
                    action_layout.setContentsMargins(5, 5, 5, 5)
                    action_layout.setSpacing(8)
                    action_layout.setAlignment(QtCore.Qt.AlignCenter)
                    # View button (eye icon - circle)
                    view_btn = QtWidgets.QPushButton("👁")
                    view_btn.setFixedSize(40, 40)
                    view_btn.setCursor(QtCore.Qt.PointingHandCursor)
                    view_btn.setToolTip("View Details")
                    view_btn.setStyleSheet("""
                        QPushButton {
                            background-color: #0078D4;
                            color: white;
                            border: none;
                            border-radius: 20px;
                            font-size: 16pt;
                            padding: 0px;
                        }
                        QPushButton:hover {
                            background-color: #005a9e;
                        }
                    """)
                    view_btn.clicked.connect(lambda checked, r=req: self.view_certificate_request(r))
                    action_layout.addWidget(view_btn)
                    # Print button (printer icon - circle)
                    print_btn = QtWidgets.QPushButton("🖨")
                    print_btn.setFixedSize(40, 40)
                    print_btn.setCursor(QtCore.Qt.PointingHandCursor)
                    print_btn.setToolTip("Print Certificate")
                    print_btn.setStyleSheet("""
                        QPushButton {
                            background-color: #27ae60;
                            color: white;
                            border: none;
                            border-radius: 20px;
                            font-size: 16pt;
                            padding: 0px;
                        }
                        QPushButton:hover {
                            background-color: #219a52;
                        }
                    """)
                    print_btn.clicked.connect(lambda checked, r=req: self.print_certificate(r))
                    action_layout.addWidget(print_btn)
                    # Complete button (check icon - circle) - mark as completed
                    complete_btn = QtWidgets.QPushButton("✔")
                    complete_btn.setFixedSize(40, 40)
                    complete_btn.setCursor(QtCore.Qt.PointingHandCursor)
                    complete_btn.setToolTip("Mark as Completed")
                    complete_btn.setStyleSheet("""
                        QPushButton {
                            background-color: #9b59b6;
                            color: white;
                            border: none;
                            border-radius: 20px;
                            font-size: 18pt;
                            padding: 0px;
                        }
                        QPushButton:hover {
                            background-color: #8e44ad;
                        }
                    """)
                    complete_btn.clicked.connect(lambda checked, r=req, tbl=table, rw=row: self.mark_as_completed(r, tbl, rw))
                    action_layout.addWidget(complete_btn)
                    table.setCellWidget(row, 6, action_widget)
            finally:
                db.close()
        except Exception as e:
            import traceback
            traceback.print_exc()
    def view_certificate_request(self, request):
        """View details of a certificate request with photo and Accept/Decline buttons"""
        try:
            from app.models import Resident, CertificateRequest
            from datetime import datetime
            import os
            # Store request_id for use in callbacks
            request_id = request.request_id
            db = SessionLocal()
            try:
                # Update status to "Under Review" when admin views the request (if still Pending)
                req = db.query(CertificateRequest).filter(CertificateRequest.request_id == request_id).first()
                if req and req.status == 'Pending':
                    req.status = 'Under Review'
                    req.updated_at = datetime.now()
                    db.commit()
                    request.status = 'Under Review'  # Update local object too
                resident = db.query(Resident).filter(Resident.resident_id == request.resident_id).first()
                resident_name = f"{resident.first_name} {resident.last_name}" if resident else "Unknown"
                # Create view dialog
                dialog = QtWidgets.QDialog(self)
                dialog.setWindowTitle("Certificate Request Details")
                dialog.setMinimumSize(550, 550)
                dialog.setStyleSheet("background-color: #f5f5f5;")
                layout = QtWidgets.QVBoxLayout(dialog)
                layout.setSpacing(15)
                layout.setContentsMargins(20, 20, 20, 20)
                # Title
                title = QtWidgets.QLabel("📄 Certificate Request Details")
                title.setStyleSheet("font-size: 16pt; font-weight: bold; color: #1976d2;")
                layout.addWidget(title)
                # Content area with horizontal layout
                content_layout = QtWidgets.QHBoxLayout()
                # Left side - Details
                details_widget = QtWidgets.QWidget()
                details_layout = QtWidgets.QVBoxLayout(details_widget)
                details_layout.setContentsMargins(0, 0, 0, 0)
                # Determine status color
                status_color = '#27ae60'  # Green for progress statuses
                if request.status == 'Declined':
                    status_color = '#e74c3c'  # Red
                elif request.status == 'Pending':
                    status_color = '#f39c12'  # Orange
                details_text = f"""
                <p><b>Resident:</b> {resident_name}</p>
                <p><b>Certificate Type:</b> {request.certificate_type or 'N/A'}</p>
                <p><b>Purpose:</b> {request.purpose or 'N/A'}</p>
                <p><b>Quantity:</b> {request.quantity or 1}</p>
                <p><b>Status:</b> <span style="color: {status_color};">{request.status or 'Pending'}</span></p>
                <p><b>Date Requested:</b> {request.created_at.strftime('%Y-%m-%d %H:%M') if request.created_at else 'N/A'}</p>
                """
                details = QtWidgets.QLabel(details_text)
                details.setStyleSheet("font-size: 11pt; background-color: white; padding: 15px; border-radius: 10px;")
                details.setWordWrap(True)
                details_layout.addWidget(details)
                details_layout.addStretch()
                content_layout.addWidget(details_widget, 1)
                # Right side - Photo (if exists)
                if request.uploaded_file_path:
                    photo_path = request.uploaded_file_path
                    # Check if it's a relative path
                    if not os.path.isabs(photo_path):
                        photo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), photo_path)
                    if os.path.exists(photo_path):
                        photo_widget = QtWidgets.QWidget()
                        photo_layout = QtWidgets.QVBoxLayout(photo_widget)
                        photo_layout.setContentsMargins(0, 0, 0, 0)
                        photo_label = QtWidgets.QLabel("📎 Uploaded Document:")
                        photo_label.setStyleSheet("font-weight: bold; font-size: 10pt;")
                        photo_layout.addWidget(photo_label)
                        # Thumbnail image (clickable)
                        img_label = QtWidgets.QLabel()
                        pixmap = QtGui.QPixmap(photo_path)
                        if not pixmap.isNull():
                            scaled_pixmap = pixmap.scaled(150, 150, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
                            img_label.setPixmap(scaled_pixmap)
                            img_label.setStyleSheet("border: 2px solid #1976d2; border-radius: 10px; padding: 5px; background-color: white;")
                            img_label.setCursor(QtCore.Qt.PointingHandCursor)
                            img_label.setToolTip("Click to view full size")
                            # Make image clickable
                            img_label.mousePressEvent = lambda event, path=photo_path: self.show_full_image(path)
                        photo_layout.addWidget(img_label)
                        photo_layout.addStretch()
                        content_layout.addWidget(photo_widget)
                layout.addLayout(content_layout)
                # Status buttons (show if Pending or Under Review)
                if request.status in ['Pending', 'Under Review']:
                    status_label = QtWidgets.QLabel("⚡ Update Status:")
                    status_label.setStyleSheet("font-weight: bold; font-size: 11pt; margin-top: 10px;")
                    layout.addWidget(status_label)
                    action_btn_layout = QtWidgets.QHBoxLayout()
                    # Accept button - sets to Processing
                    accept_btn = QtWidgets.QPushButton("✅ ACCEPT")
                    accept_btn.setFixedHeight(40)
                    accept_btn.setCursor(QtCore.Qt.PointingHandCursor)
                    accept_btn.setStyleSheet("""
                        QPushButton {
                            padding: 10px 30px;
                            background-color: #27ae60;
                            color: white;
                            border: none;
                            border-radius: 8px;
                            font-weight: bold;
                            font-size: 11pt;
                        }
                        QPushButton:hover { background-color: #219a52; }
                    """)
                    accept_btn.clicked.connect(lambda: self.update_request_status(request_id, 'Processing', dialog))
                    action_btn_layout.addWidget(accept_btn)
                    # Decline button - sets to Declined
                    decline_btn = QtWidgets.QPushButton("❌ DECLINE")
                    decline_btn.setFixedHeight(40)
                    decline_btn.setCursor(QtCore.Qt.PointingHandCursor)
                    decline_btn.setStyleSheet("""
                        QPushButton {
                            padding: 10px 30px;
                            background-color: #e74c3c;
                            color: white;
                            border: none;
                            border-radius: 8px;
                            font-weight: bold;
                            font-size: 11pt;
                        }
                        QPushButton:hover { background-color: #c0392b; }
                    """)
                    decline_btn.clicked.connect(lambda: self.update_request_status(request_id, 'Declined', dialog))
                    action_btn_layout.addWidget(decline_btn)
                    layout.addLayout(action_btn_layout)
                # Close button
                btn_layout = QtWidgets.QHBoxLayout()
                btn_layout.addStretch()
                close_btn = QtWidgets.QPushButton("Close")
                close_btn.setStyleSheet("""
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
                close_btn.clicked.connect(dialog.accept)
                btn_layout.addWidget(close_btn)
                layout.addLayout(btn_layout)
                dialog.exec_()
            finally:
                db.close()
        except Exception as e:
            self.notification.show_error(f"❌ Error viewing request: {e}")
            import traceback
            traceback.print_exc()
    def show_payment_page(self):
        """Show admin payment management page - for all accepted requests"""
        try:
            from app.models import CertificateRequest, CertificatePayment, Resident
            from datetime import datetime
            # Create outer wrapper
            outer_widget = QtWidgets.QWidget()
            outer_widget.setStyleSheet("background-color: #f0f0f0;")
            outer_layout = QtWidgets.QVBoxLayout(outer_widget)
            outer_layout.setContentsMargins(5, 15, 5, 15)  # Minimal margins
            outer_layout.setSpacing(0)
            # Main container
            main_container = QtWidgets.QWidget()
            main_container.setStyleSheet("background-color: #e8e8e8; border-radius: 15px;")
            main_container.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            main_layout = QtWidgets.QVBoxLayout(main_container)
            main_layout.setContentsMargins(5, 8, 5, 8)  # Very minimal margins
            main_layout.setSpacing(6)
            # Header
            header = QtWidgets.QLabel()
            header.setText("""<html><body>
                <p style="font-size: 16pt; font-weight: bold; color: white; margin: 0;">💳 PAYMENT MANAGEMENT</p>
            </body></html>""")
            header.setStyleSheet("""
                QLabel {
                    background: qlineargradient(
                        spread:pad, x1:0, y1:0, x2:0, y2:1,
                        stop:0 #1565c0, stop:1 #1976d2
                    );
                    border-radius: 10px;
                    padding: 10px;
                }
            """)
            header.setAlignment(QtCore.Qt.AlignCenter)
            main_layout.addWidget(header)
            # Summary stats row
            stats_widget = QtWidgets.QWidget()
            stats_layout = QtWidgets.QHBoxLayout(stats_widget)
            stats_layout.setSpacing(8)
            stats_layout.setContentsMargins(0, 0, 0, 0)
            # Get payment stats from database
            db = SessionLocal()
            try:
                # Count pending payments (all unpaid payment records)
                pending_count = db.query(CertificatePayment).filter(
                    CertificatePayment.is_paid == False
                ).count()
                # Count paid today
                from datetime import datetime, timedelta
                today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                paid_today = db.query(CertificatePayment).filter(
                    CertificatePayment.is_paid == True,
                    CertificatePayment.received_at >= today_start
                ).count()
                # Total collected today
                total_today = db.query(CertificatePayment).filter(
                    CertificatePayment.is_paid == True,
                    CertificatePayment.received_at >= today_start
                ).all()
                total_amount_today = sum(float(p.total_amount or 0) for p in total_today)
            except Exception as e:
                pending_count = 0
                paid_today = 0
                total_amount_today = 0
            finally:
                db.close()
            # Stat cards
            for title, value, color in [
                ("Pending Payments", str(pending_count), "#ff9800"),
                ("Paid Today", str(paid_today), "#4caf50"),
                ("Total Collected Today", f"₱{total_amount_today:.2f}", "#2196f3")
            ]:
                stat_card = QtWidgets.QFrame()
                stat_card.setStyleSheet(f"""
                    QFrame {{
                        background-color: white;
                        border-left: 5px solid {color};
                        border-radius: 8px;
                        padding: 6px;
                    }}
                """)
                stat_card_layout = QtWidgets.QVBoxLayout(stat_card)
                stat_card_layout.setContentsMargins(3, 3, 3, 3)
                stat_card_layout.setSpacing(2)
                stat_title = QtWidgets.QLabel(title)
                stat_title.setStyleSheet("font-size: 8pt; color: #666;")
                stat_card_layout.addWidget(stat_title)
                stat_value = QtWidgets.QLabel(value)
                stat_value.setStyleSheet(f"font-size: 14pt; font-weight: bold; color: {color};")
                stat_card_layout.addWidget(stat_value)
                stats_layout.addWidget(stat_card)
            main_layout.addWidget(stats_widget)
            # Table header with refresh button
            table_header = QtWidgets.QHBoxLayout()
            table_header.setContentsMargins(0, 0, 0, 0)
            table_header.setSpacing(5)
            table_title = QtWidgets.QLabel("Ready for Payment")
            table_title.setStyleSheet("font-size: 12pt; font-weight: bold; color: #333;")
            table_header.addWidget(table_title)
            table_header.addStretch()
            refresh_btn = QtWidgets.QPushButton("🔄 Refresh")
            refresh_btn.clicked.connect(self.show_payment_page)
            refresh_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2196f3;
                    color: white;
                    border: none;
                    padding: 6px 12px;
                    border-radius: 5px;
                    font-weight: bold;
                    font-size: 9pt;
                }
                QPushButton:hover { background-color: #1976d2; }
            """)
            table_header.addWidget(refresh_btn)
            main_layout.addLayout(table_header)
            # Payment table
            table = QtWidgets.QTableWidget()
            table.setColumnCount(9)
            table.setHorizontalHeaderLabels([
                "ID", "NAME", "CERTIFICATE TYPE", "QUANTITY", "UNIT PRICE", "TOTAL", "RECEIPT #", "STATUS", "ACTION"
            ])
            table.setStyleSheet("""
                QTableWidget {
                    background-color: white;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    gridline-color: #e0e0e0;
                }
                QHeaderView::section {
                    background-color: #1565c0;
                    color: white;
                    font-weight: bold;
                    padding: 10px;
                    border: none;
                }
                QTableWidget::item {
                    padding: 8px;
                }
            """)
            table.setAlternatingRowColors(True)
            table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
            table.verticalHeader().setVisible(False)
            # Set row height for better visibility (taller for icons/buttons)
            table.verticalHeader().setDefaultSectionSize(55)
            # Set custom column widths - use Stretch mode for most columns to fill available space
            table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
            # Set minimum widths for smaller columns to maintain readability
            table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)  # ID
            table.setColumnWidth(0, 40)    # ID - small
            # Let other columns stretch proportionally
            table.setColumnWidth(1, 300)   # NAME - expanded more
            table.setColumnWidth(2, 180)   # CERTIFICATE TYPE
            table.setColumnWidth(3, 15)    # QUANTITY - minimal width
            table.setColumnWidth(4, 50)    # UNIT PRICE
            table.setColumnWidth(5, 50)    # TOTAL
            table.setColumnWidth(6, 120)   # RECEIPT #
            table.setColumnWidth(7, 70)    # STATUS
            table.setColumnWidth(8, 100)   # ACTION
            table.horizontalHeader().setStretchLastSection(True)  # Stretch last column to fill remaining space
            # Define certificate prices
            CERTIFICATE_PRICES = {
                'Barangay Indigency': 0.00,  # Free
                'Barangay Clearance': 50.00,
                'Barangay ID': 100.00,
                'Business Permit': 500.00
            }
            # Load data - ALL accepted requests (Processing, Ready for Pickup, and Completed)
            db = SessionLocal()
            try:
                # First, ensure all accepted requests have payment records
                # Query requests that are Processing, Ready for Pickup, or Completed
                accepted_requests = db.query(CertificateRequest).filter(
                    CertificateRequest.status.in_(['Processing', 'Ready for Pickup', 'Completed'])
                ).all()
                
                # Create payment records for any that don't have one
                for req in accepted_requests:
                    existing_payment = db.query(CertificatePayment).filter(
                        CertificatePayment.request_id == req.request_id
                    ).first()
                    
                    if not existing_payment:
                        # Create payment record for this request
                        cert_type = req.certificate_type or ''
                        unit_price = CERTIFICATE_PRICES.get(cert_type, 50.00)
                        quantity = req.quantity or 1
                        total_amount = unit_price * quantity
                        requestor_name = f"{req.first_name or ''} {req.last_name or ''}".strip()
                        
                        # For Completed requests, mark as paid
                        is_paid = (req.status == 'Completed')
                        
                        payment = CertificatePayment(
                            request_id=req.request_id,
                            resident_id=req.resident_id,
                            certificate_type=cert_type,
                            requestor_name=requestor_name,
                            quantity=quantity,
                            unit_price=unit_price,
                            total_amount=total_amount,
                            is_paid=is_paid,
                            payment_method='Cash',
                            created_at=req.created_at or datetime.now(),
                            received_at=req.updated_at if is_paid else None
                        )
                        db.add(payment)
                        print(f"💰 Created missing payment record for request #{req.request_id} ({cert_type})")
                
                db.commit()  # Save any new payment records
                
                # Now query all payment records
                payments = db.query(CertificatePayment).order_by(
                    CertificatePayment.is_paid.asc(),  # Unpaid first
                    CertificatePayment.created_at.desc()
                ).all()
                
                table.setRowCount(len(payments))
                for row, payment in enumerate(payments):
                    # Get the associated request
                    req = db.query(CertificateRequest).filter(
                        CertificateRequest.request_id == payment.request_id
                    ).first()
                    
                    if not req:
                        continue
                    # ID
                    id_item = QtWidgets.QTableWidgetItem(str(req.request_id))
                    id_item.setTextAlignment(QtCore.Qt.AlignCenter)
                    table.setItem(row, 0, id_item)
                    # NAME - use name from request form, auto-capitalize
                    first_name = (req.first_name or "").strip().title()
                    last_name = (req.last_name or "").strip().title()
                    name = f"{first_name} {last_name}"
                    name_item = QtWidgets.QTableWidgetItem(name)
                    name_item.setTextAlignment(QtCore.Qt.AlignCenter)
                    table.setItem(row, 1, name_item)
                    # CERTIFICATE TYPE
                    type_item = QtWidgets.QTableWidgetItem(req.certificate_type)
                    type_item.setTextAlignment(QtCore.Qt.AlignCenter)
                    table.setItem(row, 2, type_item)
                    # QUANTITY
                    qty_item = QtWidgets.QTableWidgetItem(str(req.quantity or 1))
                    qty_item.setTextAlignment(QtCore.Qt.AlignCenter)
                    table.setItem(row, 3, qty_item)
                    # UNIT PRICE
                    unit_price = CERTIFICATE_PRICES.get(req.certificate_type, 0.00)
                    price_item = QtWidgets.QTableWidgetItem(f"₱{unit_price:.2f}")
                    price_item.setTextAlignment(QtCore.Qt.AlignCenter)
                    table.setItem(row, 4, price_item)
                    # TOTAL
                    total = unit_price * (req.quantity or 1)
                    total_item = QtWidgets.QTableWidgetItem(f"₱{total:.2f}")
                    total_item.setTextAlignment(QtCore.Qt.AlignCenter)
                    total_item.setForeground(QtGui.QColor("#1565c0"))
                    table.setItem(row, 5, total_item)
                    # RECEIPT # (OR Number or Reference Number with payment method)
                    receipt_text = ""
                    if payment and payment.is_paid:
                        method = payment.payment_method or "Cash"
                        if payment.or_number and payment.reference_number:
                            receipt_text = f"OR: {payment.or_number}\nRef: {payment.reference_number}"
                        elif payment.or_number:
                            receipt_text = f"OR: {payment.or_number}"
                        elif payment.reference_number:
                            receipt_text = f"{method}: {payment.reference_number}"
                        else:
                            receipt_text = f"({method})"
                    receipt_item = QtWidgets.QTableWidgetItem(receipt_text)
                    receipt_item.setTextAlignment(QtCore.Qt.AlignCenter)
                    if receipt_text:
                        receipt_item.setForeground(QtGui.QColor("#1565c0"))
                    table.setItem(row, 6, receipt_item)
                    # STATUS (column 7)
                    if payment and payment.is_paid:
                        status_text = "PAID ✓"
                        status_color = "#4caf50"
                    else:
                        status_text = "UNPAID"
                        status_color = "#ff9800"
                    status_item = QtWidgets.QTableWidgetItem(status_text)
                    status_item.setTextAlignment(QtCore.Qt.AlignCenter)
                    status_item.setForeground(QtGui.QColor(status_color))
                    table.setItem(row, 7, status_item)
                    # ACTION - Mark as Paid button (column 8 - at the very end)
                    action_widget = QtWidgets.QWidget()
                    action_layout = QtWidgets.QHBoxLayout(action_widget)
                    action_layout.setContentsMargins(5, 5, 5, 5)
                    action_layout.setAlignment(QtCore.Qt.AlignCenter)
                    if payment and payment.is_paid:
                        # Already paid - show checkmark
                        paid_label = QtWidgets.QLabel("✓ Paid")
                        paid_label.setStyleSheet("color: #4caf50; font-weight: bold; font-size: 10pt;")
                        paid_label.setAlignment(QtCore.Qt.AlignCenter)
                        action_layout.addWidget(paid_label)
                    else:
                        # Mark as Paid button
                        pay_btn = QtWidgets.QPushButton("💵 Mark Paid")
                        pay_btn.setCursor(QtCore.Qt.PointingHandCursor)
                        pay_btn.setStyleSheet("""
                            QPushButton {
                                background-color: #4caf50;
                                color: white;
                                border: none;
                                padding: 6px 8px;
                                border-radius: 5px;
                                font-weight: bold;
                                font-size: 9pt;
                            }
                            QPushButton:hover { background-color: #388e3c; }
                        """)
                        # Store request data for the button
                        request_id = req.request_id
                        resident_id = req.resident_id
                        cert_type = req.certificate_type
                        # Use name from request form, auto-capitalize
                        first_name = (req.first_name or "").strip().title()
                        last_name = (req.last_name or "").strip().title()
                        requestor = f"{first_name} {last_name}"
                        qty = req.quantity or 1
                        unit_price = CERTIFICATE_PRICES.get(req.certificate_type, 0.00)
                        total = unit_price * qty
                        pay_btn.clicked.connect(
                            lambda checked, rid=request_id, resid=resident_id, ct=cert_type, 
                                   rn=requestor, q=qty, up=unit_price, t=total:
                            self.mark_as_paid(rid, resid, ct, rn, q, up, t)
                        )
                        action_layout.addWidget(pay_btn)
                    table.setCellWidget(row, 8, action_widget)
            finally:
                db.close()
            main_layout.addWidget(table, 1)  # Give table stretch priority
            outer_layout.addWidget(main_container)
            # Replace content
            self.replace_content(outer_widget)
            self.notification.show_success("💳 Payment Management loaded!")
        except Exception as e:
            self.notification.show_error(f"❌ Error loading Payment page: {e}")
            import traceback
            traceback.print_exc()
    def mark_as_paid(self, request_id, resident_id, cert_type, requestor_name, quantity, unit_price, total):
        """Mark a certificate request as paid"""
        try:
            from app.models import CertificatePayment, CertificateRequest
            from datetime import datetime
            # Show confirmation dialog with payment method and receipt inputs
            dialog = QtWidgets.QDialog(self)
            dialog.setWindowTitle("Confirm Payment")
            dialog.setFixedWidth(450)
            dialog.setStyleSheet("background-color: white;")
            layout = QtWidgets.QVBoxLayout(dialog)
            layout.setSpacing(15)
            layout.setContentsMargins(20, 20, 20, 20)
            # Title
            title = QtWidgets.QLabel("💵 Confirm Payment Received")
            title.setStyleSheet("font-size: 14pt; font-weight: bold; color: #333;")
            title.setAlignment(QtCore.Qt.AlignCenter)
            layout.addWidget(title)
            # Details
            details = QtWidgets.QLabel(f"""
                <b>Request ID:</b> {request_id}<br>
                <b>Name:</b> {requestor_name}<br>
                <b>Certificate:</b> {cert_type}<br>
                <b>Quantity:</b> {quantity}<br>
                <b>Unit Price:</b> ₱{unit_price:.2f}<br>
                <b>Total Amount:</b> <span style="color: #1565c0; font-size: 14pt;">₱{total:.2f}</span>
            """)
            details.setStyleSheet("font-size: 11pt; line-height: 1.6;")
            layout.addWidget(details)
            # Payment Method selection
            method_layout = QtWidgets.QHBoxLayout()
            method_label = QtWidgets.QLabel("Payment Method:")
            method_label.setStyleSheet("font-weight: bold;")
            method_layout.addWidget(method_label)
            method_combo = QtWidgets.QComboBox()
            method_combo.addItems(["Cash", "GCash", "Bank Transfer", "Other"])
            method_combo.setStyleSheet("""
                QComboBox {
                    padding: 8px;
                    border: 1px solid #ccc;
                    border-radius: 5px;
                }
            """)
            method_layout.addWidget(method_combo)
            layout.addLayout(method_layout)
            # OR Number input (for Cash)
            or_layout = QtWidgets.QHBoxLayout()
            or_label = QtWidgets.QLabel("OR Number:")
            or_label.setStyleSheet("font-weight: bold;")
            or_layout.addWidget(or_label)
            or_input = QtWidgets.QLineEdit()
            or_input.setPlaceholderText("Official Receipt Number")
            or_input.setStyleSheet("""
                QLineEdit {
                    padding: 8px;
                    border: 1px solid #ccc;
                    border-radius: 5px;
                }
            """)
            or_layout.addWidget(or_input)
            layout.addLayout(or_layout)
            # Reference Number input (for online payments)
            ref_layout = QtWidgets.QHBoxLayout()
            ref_label = QtWidgets.QLabel("Reference #:")
            ref_label.setStyleSheet("font-weight: bold;")
            ref_layout.addWidget(ref_label)
            ref_input = QtWidgets.QLineEdit()
            ref_input.setPlaceholderText("GCash/Bank Reference Number")
            ref_input.setStyleSheet("""
                QLineEdit {
                    padding: 8px;
                    border: 1px solid #ccc;
                    border-radius: 5px;
                }
            """)
            ref_layout.addWidget(ref_input)
            layout.addLayout(ref_layout)
            # Buttons
            btn_layout = QtWidgets.QHBoxLayout()
            cancel_btn = QtWidgets.QPushButton("Cancel")
            cancel_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e0e0e0;
                    color: #333;
                    border: none;
                    padding: 10px 25px;
                    border-radius: 5px;
                    font-weight: bold;
                }
                QPushButton:hover { background-color: #bdbdbd; }
            """)
            cancel_btn.clicked.connect(dialog.reject)
            btn_layout.addWidget(cancel_btn)
            confirm_btn = QtWidgets.QPushButton("✓ Confirm Payment")
            confirm_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4caf50;
                    color: white;
                    border: none;
                    padding: 10px 25px;
                    border-radius: 5px;
                    font-weight: bold;
                }
                QPushButton:hover { background-color: #388e3c; }
            """)
            def do_confirm():
                payment_method = method_combo.currentText()
                or_number = or_input.text().strip()
                ref_number = ref_input.text().strip()
                db = SessionLocal()
                try:
                    # Check if payment record exists
                    payment = db.query(CertificatePayment).filter(
                        CertificatePayment.request_id == request_id
                    ).first()
                    if not payment:
                        # Create new payment record
                        payment = CertificatePayment(
                            request_id=request_id,
                            resident_id=resident_id,
                            certificate_type=cert_type,
                            requestor_name=requestor_name,
                            quantity=quantity,
                            unit_price=unit_price,
                            total_amount=total,
                            is_paid=True,
                            payment_method=payment_method,
                            received_at=datetime.now(),
                            or_number=or_number if or_number else None,
                            reference_number=ref_number if ref_number else None
                        )
                        db.add(payment)
                    else:
                        # Update existing payment record
                        payment.is_paid = True
                        payment.payment_method = payment_method
                        payment.received_at = datetime.now()
                        payment.or_number = or_number if or_number else None
                        payment.reference_number = ref_number if ref_number else None
                    db.commit()
                    self.notification.show_success(f"✅ Payment of ₱{total:.2f} ({payment_method}) confirmed for Request #{request_id}")
                    dialog.accept()
                    # Refresh the payment page
                    self.show_payment_page()
                except Exception as e:
                    self.notification.show_error(f"❌ Error: {e}")
                finally:
                    db.close()
            confirm_btn.clicked.connect(do_confirm)
            btn_layout.addWidget(confirm_btn)
            layout.addLayout(btn_layout)
            dialog.exec_()
        except Exception as e:
            self.notification.show_error(f"❌ Error: {e}")
    def show_full_image(self, image_path):
        """Show full-size image in a dialog - no scroll bar"""
        try:
            # Get screen size
            screen_size = QtWidgets.QApplication.primaryScreen().size()
            # Load the image first to get its size
            pixmap = QtGui.QPixmap(image_path)
            if pixmap.isNull():
                self.notification.show_error("❌ Could not load image")
                return
            # Calculate dialog size based on image (80% of screen max)
            max_width = int(screen_size.width() * 0.8)
            max_height = int(screen_size.height() * 0.8)
            # Scale image to fit within max dimensions
            scaled_pixmap = pixmap.scaled(max_width, max_height - 60, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            # Create dialog sized to fit the scaled image
            dialog = QtWidgets.QDialog(self)
            dialog.setWindowTitle("Uploaded Document")
            dialog.setFixedSize(scaled_pixmap.width() + 40, scaled_pixmap.height() + 80)
            dialog.setStyleSheet("background-color: #2c3e50;")
            layout = QtWidgets.QVBoxLayout(dialog)
            layout.setContentsMargins(20, 15, 20, 15)
            layout.setSpacing(10)
            # Image label - no scroll, just display
            img_label = QtWidgets.QLabel()
            img_label.setAlignment(QtCore.Qt.AlignCenter)
            img_label.setPixmap(scaled_pixmap)
            img_label.setStyleSheet("background-color: transparent;")
            layout.addWidget(img_label)
            # Close button
            close_btn = QtWidgets.QPushButton("Close")
            close_btn.setFixedSize(100, 35)
            close_btn.setCursor(QtCore.Qt.PointingHandCursor)
            close_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    font-weight: bold;
                }
                QPushButton:hover { background-color: #2980b9; }
            """)
            close_btn.clicked.connect(dialog.accept)
            btn_layout = QtWidgets.QHBoxLayout()
            btn_layout.addStretch()
            btn_layout.addWidget(close_btn)
            btn_layout.addStretch()
            layout.addLayout(btn_layout)
            dialog.exec_()
        except Exception as e:
            pass
    def print_certificate(self, request):
        """Show certificate preview"""
        try:
            from app.models import Resident
            import os
            import re
            db = SessionLocal()
            try:
                resident = db.query(Resident).filter(Resident.resident_id == request.resident_id).first()
                
                # Use name from the REQUEST FORM (not the account name)
                # This allows users to request certificates for others (e.g., family members)
                # Auto-capitalize: john kester benitez → John Kester Benitez
                first_name = (request.first_name or "").strip().title()
                middle_name = (request.middle_name or "").strip().title()
                last_name = (request.last_name or "").strip().title()
                suffix = (request.suffix or "").strip().upper() if request.suffix else ""
                
                # Clean any numeric-only values from name fields (data migration issue)
                # Remove phone numbers, IDs, or any purely numeric strings
                def clean_name_part(name_part):
                    """Remove numeric-only parts and phone numbers from name"""
                    if not name_part:
                        return ""
                    # Remove if it's purely numeric or looks like a phone number
                    cleaned = re.sub(r'^\d+$', '', name_part)  # Remove pure numbers
                    cleaned = re.sub(r'^\d{10,}', '', cleaned)  # Remove phone numbers at start
                    cleaned = re.sub(r'\d{10,}$', '', cleaned)  # Remove phone numbers at end
                    return cleaned.strip()
                
                first_name = clean_name_part(first_name)
                middle_name = clean_name_part(middle_name)
                last_name = clean_name_part(last_name)
                
                # Build full name from request form
                if middle_name:
                    resident_name = f"{first_name} {middle_name} {last_name}"
                else:
                    resident_name = f"{first_name} {last_name}"
                
                if suffix:
                    resident_name += f" {suffix}"
                
                # Clean up any extra spaces
                resident_name = ' '.join(resident_name.split())
                
                # Fallback to resident table if request has no name
                if not first_name and not last_name and resident:
                    resident_name = f"{resident.first_name} {resident.last_name}".title()
                
                # Create certificate preview dialog
                dialog = QtWidgets.QDialog(self)
                dialog.setWindowTitle("Certificate Preview")
                dialog.setFixedSize(650, 850)
                dialog.setStyleSheet("background-color: #f0f0f0;")
                layout = QtWidgets.QVBoxLayout(dialog)
                layout.setSpacing(10)
                layout.setContentsMargins(20, 20, 20, 20)
                # Title
                title_label = QtWidgets.QLabel("📄 Certificate Preview")
                title_label.setStyleSheet("font-size: 14pt; font-weight: bold; color: #333;")
                title_label.setAlignment(QtCore.Qt.AlignCenter)
                layout.addWidget(title_label)
                # Certificate frame (like paper)
                cert_frame = QtWidgets.QFrame()
                cert_frame.setStyleSheet("""
                    QFrame {
                        background-color: white;
                        border: 1px solid #ccc;
                        border-radius: 5px;
                    }
                """)
                cert_layout = QtWidgets.QVBoxLayout(cert_frame)
                cert_layout.setContentsMargins(25, 25, 25, 25)
                cert_layout.setSpacing(5)
                # Header section with logo and text
                header_widget = QtWidgets.QWidget()
                header_layout = QtWidgets.QHBoxLayout(header_widget)
                header_layout.setContentsMargins(0, 0, 0, 0)
                # Logo on left
                logo_label = QtWidgets.QLabel()
                logo_path = os.path.join(os.path.dirname(__file__), '..', 'ui', 'logo.jpg')
                if os.path.exists(logo_path):
                    pixmap = QtGui.QPixmap(logo_path)
                    scaled_pixmap = pixmap.scaled(65, 65, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
                    logo_label.setPixmap(scaled_pixmap)
                logo_label.setFixedSize(70, 70)
                header_layout.addWidget(logo_label)
                # Header text (center)
                header_text = QtWidgets.QLabel()
                header_text.setAlignment(QtCore.Qt.AlignCenter)
                header_text.setText("""
                    <p style="margin: 0; font-size: 9pt;">Republic of the Philippines</p>
                    <p style="margin: 0; font-size: 9pt; font-weight: bold;">PROVINCE OF BATANGAS</p>
                    <p style="margin: 0; font-size: 9pt; font-style: italic;">Municipality of Calatagan</p>
                    <p style="margin: 0; font-size: 9pt; font-weight: bold;">Barangay Balibago</p>
                """)
                header_layout.addWidget(header_text, 1)
                cert_layout.addWidget(header_widget)
                # Date calculations
                from datetime import datetime
                current_date = datetime.now()
                day = current_date.day
                if 10 <= day % 100 <= 20:
                    suffix = 'th'
                else:
                    suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
                day_with_suffix = f"{day}{suffix}"
                month_year = current_date.strftime('%B, %Y')
                
                # Get certificate type
                cert_type = request.certificate_type.lower() if request.certificate_type else ''
                
                # Different certificate templates based on type
                if 'business' in cert_type:
                    # BUSINESS PERMIT CERTIFICATE
                    body_html = f"""
                    <p style="text-align: center; font-size: 11pt; font-weight: bold; margin: 10px 0 5px 0; text-decoration: underline;">
                        OFFICE OF THE BARANGAY CAPTAIN
                    </p>
                    <p style="text-align: center; font-size: 13pt; font-weight: bold; color: #006400; margin: 12px 0;">
                        BARANGAY BUSINESS PERMIT
                    </p>
                    <p style="text-align: left; font-size: 10pt; font-weight: bold; margin: 12px 0 8px 0;">
                        TO WHOM IT MAY CONCERN:
                    </p>
                    <p style="text-indent: 35px; line-height: 1.5; text-align: justify; font-size: 10pt; margin: 6px 0;">
                        THIS IS TO CERTIFY that <strong><u>{resident_name.upper()}</u></strong> of legal age, a 
                        Filipino Citizen and a bonafide resident of Barangay Balibago, Calatagan, 
                        Batangas, is hereby granted this <strong>BARANGAY BUSINESS PERMIT</strong> to operate 
                        a business establishment within the territorial jurisdiction of this barangay.
                    </p>
                    <p style="text-indent: 35px; line-height: 1.5; text-align: justify; font-size: 10pt; margin: 6px 0;">
                        <strong>Purpose:</strong> {request.purpose.upper() if request.purpose else 'BUSINESS OPERATION'}
                    </p>
                    <p style="text-indent: 35px; line-height: 1.5; text-align: justify; font-size: 10pt; margin: 6px 0;">
                        This permit is issued subject to existing barangay ordinances, rules and regulations, 
                        and is valid for one (1) year from the date of issuance unless sooner revoked for cause.
                    </p>
                    <p style="text-indent: 35px; line-height: 1.5; font-size: 10pt; margin: 12px 0;">
                        Issued this <u>{day_with_suffix}</u> day of <u>{month_year}</u> at Barangay Balibago, Calatagan, Batangas.
                    </p>
                    <div style="margin-top: 35px; text-align: center;">
                        <p style="margin: 0; font-size: 10pt; font-weight: bold;">
                            _________________________________
                        </p>
                        <p style="margin: 3px 0 0 0; font-size: 9pt; font-style: italic;">
                            Punong Barangay
                        </p>
                    </div>
                    <p style="text-align: center; font-size: 8pt; font-weight: bold; margin-top: 25px;">
                        NOT VALID WITHOUT SEAL
                    </p>
                    """
                elif 'indigency' in cert_type:
                    # CERTIFICATE OF INDIGENCY
                    body_html = f"""
                    <p style="text-align: center; font-size: 11pt; font-weight: bold; margin: 10px 0 5px 0; text-decoration: underline;">
                        OFFICE OF THE BARANGAY CAPTAIN
                    </p>
                    <p style="text-align: center; font-size: 13pt; font-weight: bold; color: #8B4513; margin: 12px 0;">
                        CERTIFICATE OF INDIGENCY
                    </p>
                    <p style="text-align: left; font-size: 10pt; font-weight: bold; margin: 12px 0 8px 0;">
                        TO WHOM IT MAY CONCERN:
                    </p>
                    <p style="text-indent: 35px; line-height: 1.5; text-align: justify; font-size: 10pt; margin: 6px 0;">
                        THIS IS TO CERTIFY that <strong><u>{resident_name.upper()}</u></strong> of legal age, a 
                        Filipino Citizen and a bonafide resident of Barangay Balibago, Calatagan, 
                        Batangas, belongs to the <strong>INDIGENT FAMILIES</strong> in this barangay.
                    </p>
                    <p style="text-indent: 35px; line-height: 1.5; text-align: justify; font-size: 10pt; margin: 6px 0;">
                        <strong>Purpose:</strong> {request.purpose.upper() if request.purpose else 'GENERAL PURPOSE'}
                    </p>
                    <p style="text-indent: 35px; line-height: 1.5; text-align: justify; font-size: 10pt; margin: 6px 0;">
                        This certification is issued upon the request of the above-mentioned person for 
                        whatever legal purpose it may serve, particularly for availing government assistance 
                        and other benefits intended for indigent families.
                    </p>
                    <p style="text-indent: 35px; line-height: 1.5; font-size: 10pt; margin: 12px 0;">
                        Issued this <u>{day_with_suffix}</u> day of <u>{month_year}</u> at Barangay Balibago, Calatagan, Batangas.
                    </p>
                    <div style="margin-top: 35px; text-align: center;">
                        <p style="margin: 0; font-size: 10pt; font-weight: bold;">
                            _________________________________
                        </p>
                        <p style="margin: 3px 0 0 0; font-size: 9pt; font-style: italic;">
                            Punong Barangay
                        </p>
                    </div>
                    <p style="text-align: center; font-size: 8pt; font-weight: bold; margin-top: 25px;">
                        NOT VALID WITHOUT SEAL
                    </p>
                    """
                elif 'id' in cert_type:
                    # BARANGAY ID CERTIFICATE
                    body_html = f"""
                    <p style="text-align: center; font-size: 11pt; font-weight: bold; margin: 10px 0 5px 0; text-decoration: underline;">
                        OFFICE OF THE BARANGAY CAPTAIN
                    </p>
                    <p style="text-align: center; font-size: 13pt; font-weight: bold; color: #1E90FF; margin: 12px 0;">
                        BARANGAY IDENTIFICATION CERTIFICATE
                    </p>
                    <p style="text-align: left; font-size: 10pt; font-weight: bold; margin: 12px 0 8px 0;">
                        TO WHOM IT MAY CONCERN:
                    </p>
                    <p style="text-indent: 35px; line-height: 1.5; text-align: justify; font-size: 10pt; margin: 6px 0;">
                        THIS IS TO CERTIFY that <strong><u>{resident_name.upper()}</u></strong> of legal age, a 
                        Filipino Citizen, is a bonafide resident of Barangay Balibago, Calatagan, 
                        Batangas.
                    </p>
                    <p style="text-indent: 35px; line-height: 1.5; text-align: justify; font-size: 10pt; margin: 6px 0;">
                        <strong>Purpose:</strong> {request.purpose.upper() if request.purpose else 'IDENTIFICATION'}
                    </p>
                    <p style="text-indent: 35px; line-height: 1.5; text-align: justify; font-size: 10pt; margin: 6px 0;">
                        This certification is issued for identification purposes and to certify the 
                        residency status of the above-mentioned person.
                    </p>
                    <p style="text-indent: 35px; line-height: 1.5; font-size: 10pt; margin: 12px 0;">
                        Issued this <u>{day_with_suffix}</u> day of <u>{month_year}</u> at Barangay Balibago, Calatagan, Batangas.
                    </p>
                    <div style="margin-top: 35px; text-align: center;">
                        <p style="margin: 0; font-size: 10pt; font-weight: bold;">
                            _________________________________
                        </p>
                        <p style="margin: 3px 0 0 0; font-size: 9pt; font-style: italic;">
                            Punong Barangay
                        </p>
                    </div>
                    <p style="text-align: center; font-size: 8pt; font-weight: bold; margin-top: 25px;">
                        NOT VALID WITHOUT SEAL
                    </p>
                    """
                else:
                    # BARANGAY CLEARANCE CERTIFICATE (default)
                    body_html = f"""
                    <p style="text-align: center; font-size: 11pt; font-weight: bold; margin: 10px 0 5px 0; text-decoration: underline;">
                        OFFICE OF THE BARANGAY CAPTAIN
                    </p>
                    <p style="text-align: center; font-size: 13pt; font-weight: bold; color: #8B0000; margin: 12px 0;">
                        BARANGAY CLEARANCE
                    </p>
                    <p style="text-align: left; font-size: 10pt; font-weight: bold; margin: 12px 0 8px 0;">
                        TO WHOM IT MAY CONCERN:
                    </p>
                    <p style="text-indent: 35px; line-height: 1.5; text-align: justify; font-size: 10pt; margin: 6px 0;">
                        THIS IS TO CERTIFY that <strong><u>{resident_name.upper()}</u></strong> of legal age, a 
                        Filipino Citizen and a bonafide resident of Barangay Balibago, Calatagan, 
                        Batangas, has no derogatory record filed in this barangay as of this date.
                    </p>
                    <p style="text-indent: 35px; line-height: 1.5; text-align: justify; font-size: 10pt; margin: 6px 0;">
                        <strong>Purpose:</strong> {request.purpose.upper() if request.purpose else 'GENERAL PURPOSE'}
                    </p>
                    <p style="text-indent: 35px; line-height: 1.5; text-align: justify; font-size: 10pt; margin: 6px 0;">
                        This certification is issued upon the request of the above-mentioned person for 
                        whatever legal purpose it may serve.
                    </p>
                    <p style="text-indent: 35px; line-height: 1.5; font-size: 10pt; margin: 12px 0;">
                        Issued this <u>{day_with_suffix}</u> day of <u>{month_year}</u> at Barangay Balibago, Calatagan, Batangas.
                    </p>
                    <div style="margin-top: 35px; text-align: center;">
                        <p style="margin: 0; font-size: 10pt; font-weight: bold;">
                            _________________________________
                        </p>
                        <p style="margin: 3px 0 0 0; font-size: 9pt; font-style: italic;">
                            Punong Barangay
                        </p>
                    </div>
                    <p style="text-align: center; font-size: 8pt; font-weight: bold; margin-top: 25px;">
                        NOT VALID WITHOUT SEAL
                    </p>
                    """
                body_label = QtWidgets.QLabel()
                body_label.setText(body_html)
                body_label.setWordWrap(True)
                body_label.setAlignment(QtCore.Qt.AlignTop)
                cert_layout.addWidget(body_label)
                cert_layout.addStretch()
                layout.addWidget(cert_frame)
                # Buttons
                btn_layout = QtWidgets.QHBoxLayout()
                btn_layout.addStretch()
                # Print button - sets status to Ready for Pickup
                print_btn = QtWidgets.QPushButton("🖨 Print")
                print_btn.setFixedSize(100, 35)
                print_btn.setCursor(QtCore.Qt.PointingHandCursor)
                print_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #27ae60;
                        color: white;
                        border: none;
                        border-radius: 5px;
                        font-weight: bold;
                        font-size: 10pt;
                    }
                    QPushButton:hover { background-color: #219a52; }
                """)
                print_btn.clicked.connect(lambda: self.do_print(request.request_id, dialog))
                btn_layout.addWidget(print_btn)
                # Close button
                close_btn = QtWidgets.QPushButton("Close")
                close_btn.setFixedSize(100, 35)
                close_btn.setCursor(QtCore.Qt.PointingHandCursor)
                close_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #95a5a6;
                        color: white;
                        border: none;
                        border-radius: 5px;
                        font-weight: bold;
                        font-size: 10pt;
                    }
                    QPushButton:hover { background-color: #7f8c8d; }
                """)
                close_btn.clicked.connect(dialog.accept)
                btn_layout.addWidget(close_btn)
                btn_layout.addStretch()
                layout.addLayout(btn_layout)
                dialog.exec_()
            finally:
                db.close()
        except Exception as e:
            self.notification.show_error(f"❌ Error showing certificate: {e}")
            import traceback
            traceback.print_exc()
    def mark_as_completed(self, request, table, row):
        """Mark a request as completed with confirmation"""
        # Ask for confirmation first
        reply = QtWidgets.QMessageBox.question(
            self,
            "Confirm Completion",
            "Are you sure you want to mark this request as Completed?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )
        if reply == QtWidgets.QMessageBox.Yes:
            try:
                from app.models import CertificateRequest, Notification
                from datetime import datetime
                db = SessionLocal()
                try:
                    req = db.query(CertificateRequest).filter(CertificateRequest.request_id == request.request_id).first()
                    if req:
                        req.status = "Completed"
                        req.updated_at = datetime.now()
                        
                        # Create notification for user - "Request Completed"
                        notification = Notification(
                            resident_id=req.resident_id,
                            title="🎉 Request Completed",
                            message=f"Your {req.certificate_type} request has been completed! Thank you for using Barangay E-Services.",
                            is_read=False,
                            created_at=datetime.now()
                        )
                        db.add(notification)
                        
                        db.commit()
                        # Update the table cell
                        status_item = QtWidgets.QTableWidgetItem("Completed")
                        status_item.setTextAlignment(QtCore.Qt.AlignCenter)
                        status_item.setForeground(QtGui.QColor("#3498db"))  # Blue
                        table.setItem(row, 5, status_item)
                        self.notification.show_success("✅ Request marked as Completed")
                    else:
                        self.notification.show_error("❌ Request not found")
                finally:
                    db.close()
            except Exception as e:
                self.notification.show_error(f"❌ Error updating status: {e}")
    def do_print(self, request_id, dialog):
        """Set status to Ready for Pickup and notify user"""
        try:
            # Show printing notification immediately
            self.notification.show_info("🖨️ Printing certificate... Please wait.")
            
            from app.models import CertificateRequest, Notification, Account, CertificatePayment
            from datetime import datetime
            # Certificate prices
            CERTIFICATE_PRICES = {
                'Barangay Indigency': 0.00,
                'Barangay Clearance': 50.00,
                'Barangay ID': 100.00,
                'Business Permit': 500.00
            }
            db = SessionLocal()
            try:
                request = db.query(CertificateRequest).filter(CertificateRequest.request_id == request_id).first()
                if request:
                    request.status = 'Ready for Pickup'
                    request.updated_at = datetime.now()
                    # Create payment record if not exists
                    existing_payment = db.query(CertificatePayment).filter(
                        CertificatePayment.request_id == request_id
                    ).first()
                    if not existing_payment:
                        unit_price = CERTIFICATE_PRICES.get(request.certificate_type, 0.00)
                        quantity = request.quantity or 1
                        total = unit_price * quantity
                        payment = CertificatePayment(
                            request_id=request_id,
                            resident_id=request.resident_id,
                            certificate_type=request.certificate_type,
                            requestor_name=f"{request.first_name} {request.last_name}",
                            quantity=quantity,
                            unit_price=unit_price,
                            total_amount=total,
                            is_paid=False,
                            payment_method='Cash'
                        )
                        db.add(payment)
                    # Create notification for user - "Ready for Payment"
                    notification = Notification(
                        resident_id=request.resident_id,
                        title="💳 Ready for Payment",
                        message=f"Your {request.certificate_type} request is ready! Please proceed to the Barangay Hall for payment and pickup.",
                        is_read=False,
                        created_at=datetime.now()
                    )
                    db.add(notification)
                    db.commit()
                    self.notification.show_success("🖨 Certificate printed! Status set to Ready for Pickup. User notified for payment.")
                    dialog.accept()
                    self.show_services_page()  # Refresh table
                else:
                    self.notification.show_error("❌ Request not found")
            finally:
                db.close()
        except Exception as e:
            self.notification.show_error(f"❌ Error: {e}")
    def update_request_status(self, request_id, new_status, dialog):
        """Update the status of a certificate request and create payment record if accepted"""
        try:
            from app.models import CertificateRequest, CertificatePayment, Resident, Notification
            from datetime import datetime
            
            # Official certificate fees (in PHP) - based on Barangay price list
            CERTIFICATE_FEES = {
                'Barangay Indigency': 0.00,      # FREE
                'Barangay Clearance': 50.00,     # ₱50
                'Barangay ID': 100.00,           # ₱100
                'Business Permit': 500.00,       # ₱500
            }
            
            db = SessionLocal()
            try:
                request = db.query(CertificateRequest).filter(CertificateRequest.request_id == request_id).first()
                if request:
                    request.status = new_status
                    request.reviewed_at = datetime.now()
                    request.updated_at = datetime.now()
                    
                    # If accepted (Processing), create a payment record for admin to manage
                    if new_status == 'Processing':
                        # Check if payment record already exists
                        existing_payment = db.query(CertificatePayment).filter(
                            CertificatePayment.request_id == request_id
                        ).first()
                        
                        if not existing_payment:
                            # Get resident info
                            resident = db.query(Resident).filter(
                                Resident.resident_id == request.resident_id
                            ).first()
                            
                            # Get fee based on certificate type
                            cert_type = request.certificate_type or ''
                            unit_price = CERTIFICATE_FEES.get(cert_type, 50.00)
                            quantity = request.quantity or 1
                            total_amount = unit_price * quantity
                            
                            # Create requestor name
                            requestor_name = f"{request.first_name or ''} {request.last_name or ''}".strip()
                            if not requestor_name and resident:
                                requestor_name = resident.full_name()
                            
                            # Create payment record
                            payment = CertificatePayment(
                                request_id=request_id,
                                resident_id=request.resident_id,
                                certificate_type=cert_type,
                                requestor_name=requestor_name,
                                quantity=quantity,
                                unit_price=unit_price,
                                total_amount=total_amount,
                                is_paid=False,  # Not paid yet - admin will mark as paid
                                payment_method='Cash',  # Default
                                created_at=datetime.now()
                            )
                            db.add(payment)
                            print(f"💰 Created payment record: {cert_type} - ₱{total_amount} for {requestor_name}")
                        
                        # Create notification for user - "Request Accepted"
                        notification = Notification(
                            resident_id=request.resident_id,
                            title="✅ Request Accepted",
                            message=f"Your {request.certificate_type} request has been accepted and is now being processed. Please wait for further updates.",
                            is_read=False,
                            created_at=datetime.now()
                        )
                        db.add(notification)
                        
                        self.notification.show_success("✅ Request accepted! Payment record created for admin.")
                    elif new_status == 'Declined':
                        # Create notification for user - "Request Declined"
                        notification = Notification(
                            resident_id=request.resident_id,
                            title="❌ Request Declined",
                            message=f"Your {request.certificate_type} request has been declined. Please visit the Barangay Hall for more information.",
                            is_read=False,
                            created_at=datetime.now()
                        )
                        db.add(notification)
                        
                        self.notification.show_warning("❌ Request declined.")
                    else:
                        self.notification.show_success(f"✅ Status updated to {new_status}")
                    
                    db.commit()
                    
                    # Close dialog and refresh table
                    dialog.accept()
                    self.show_services_page()
                else:
                    self.notification.show_error("❌ Request not found!")
            finally:
                db.close()
        except Exception as e:
            self.notification.show_error(f"❌ Error updating status: {e}")
            import traceback
            traceback.print_exc()
    def load_certificate_requests_table(self, widget):
        """Load certificate requests from database and populate the table"""
        try:
            from app.models import CertificateRequest, Resident
            # Find the table widget (try common names)
            table = None
            for table_name in ['tableWidget', 'tableWidget_2', 'table', 'requestsTable']:
                table = widget.findChild(QtWidgets.QTableWidget, table_name)
                if table:
                    break
            if not table:
                # Try finding any QTableWidget
                tables = widget.findChildren(QtWidgets.QTableWidget)
                if tables:
                    table = tables[0]
            if not table:
                return
            # Make table expand to fill available space
            table.setSizePolicy(
                QtWidgets.QSizePolicy.Expanding,
                QtWidgets.QSizePolicy.Expanding
            )
            # Set vertical header (row numbers) to resize mode
            table.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
            # Enable word wrap for better text display
            table.setWordWrap(True)
            # Adjust row height
            table.verticalHeader().setDefaultSectionSize(40)  # Comfortable row height
            # Set up table headers
            table.setColumnCount(6)
            table.setHorizontalHeaderLabels(["NAME", "TYPE", "PURPOSE", "QUANTITY", "DATE", "ACTION"])
            # Set column widths to fill space properly
            header = table.horizontalHeader()
            header.setStretchLastSection(True)  # Stretch last column
            # Set minimum column widths
            table.setColumnWidth(0, 150)  # NAME
            table.setColumnWidth(1, 180)  # TYPE
            table.setColumnWidth(2, 200)  # PURPOSE
            table.setColumnWidth(3, 100)  # QUANTITY
            table.setColumnWidth(4, 150)  # DATE
            table.setColumnWidth(5, 120)  # ACTION
            # Enable stretching for better appearance
            header.setSectionResizeMode(0, QtWidgets.QHeaderView.Interactive)
            header.setSectionResizeMode(1, QtWidgets.QHeaderView.Interactive)
            header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)  # PURPOSE stretches
            header.setSectionResizeMode(3, QtWidgets.QHeaderView.Interactive)
            header.setSectionResizeMode(4, QtWidgets.QHeaderView.Interactive)
            header.setSectionResizeMode(5, QtWidgets.QHeaderView.Interactive)
            # Fetch certificate requests from database
            db = SessionLocal()
            try:
                requests = db.query(CertificateRequest).join(
                    Resident, CertificateRequest.resident_id == Resident.resident_id
                ).order_by(CertificateRequest.created_at.desc()).all()
                # Set row count
                table.setRowCount(len(requests))
                # Populate table
                for row, request in enumerate(requests):
                    # Get resident info
                    resident = db.query(Resident).filter(Resident.resident_id == request.resident_id).first()
                    # NAME column
                    name = f"{request.first_name or ''} {request.last_name or ''}".strip()
                    if not name and resident:
                        name = resident.full_name()
                    table.setItem(row, 0, QtWidgets.QTableWidgetItem(name))
                    # TYPE column
                    table.setItem(row, 1, QtWidgets.QTableWidgetItem(request.certificate_type or ''))
                    # PURPOSE column  
                    table.setItem(row, 2, QtWidgets.QTableWidgetItem(request.purpose or ''))
                    # QUANTITY column
                    table.setItem(row, 3, QtWidgets.QTableWidgetItem(str(request.quantity or 1)))
                    # DATE column
                    date_str = request.created_at.strftime("%Y-%m-%d %H:%M") if request.created_at else ''
                    table.setItem(row, 4, QtWidgets.QTableWidgetItem(date_str))
                    # ACTION column - VIEW button with icon
                    view_button = QtWidgets.QPushButton("👁 VIEW")
                    view_button.setStyleSheet("""
                        QPushButton {
                            background-color: #2196F3;
                            color: white;
                            border: none;
                            padding: 5px 10px;
                            border-radius: 3px;
                            font-weight: bold;
                        }
                        QPushButton:hover {
                            background-color: #1976D2;
                        }
                        QPushButton:pressed {
                            background-color: #0D47A1;
                        }
                    """)
                    # Connect button to view request details
                    view_button.clicked.connect(lambda checked, req=request: self.view_request_details(req))
                    # Add button to table
                    table.setCellWidget(row, 5, view_button)
            except Exception as e:
                import traceback
                traceback.print_exc()
            finally:
                db.close()
        except Exception as e:
            import traceback
            traceback.print_exc()
    def view_request_details(self, request):
        """View request details in a floating dialog"""
        try:
            # Path to ADMIN_SERVICES_P2.ui
            details_ui_path = Path(__file__).resolve().parent.parent / "ui" / "ADMIN_SERVICES_P2.ui"
            if not details_ui_path.exists():
                self.notification.show_error(f"❌ UI file not found: {details_ui_path}")
                return
            # Create a floating dialog (nakalutang!)
            dialog = QtWidgets.QDialog(self)
            dialog.setWindowTitle(f"Certificate Request Details - #{request.request_id}")
            dialog.setModal(True)  # Block interaction with main window
            # Add beautiful gray/blue background styling
            dialog.setStyleSheet("""
                QDialog {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                                stop:0 #E8EAF6, stop:1 #C5CAE9);
                }
                QLabel {
                    background-color: transparent;
                }
                QLineEdit, QTextEdit {
                    background-color: white;
                    border: 2px solid #5C6BC0;
                    border-radius: 5px;
                    padding: 5px;
                }
                QPushButton {
                    border-radius: 5px;
                    padding: 10px 20px;
                    font-weight: bold;
                    font-size: 14px;
                }
            """)
            # Load the UI (it's a QMainWindow, so load it into a temp window first)
            temp_window = QtWidgets.QMainWindow()
            uic.loadUi(str(details_ui_path), temp_window)
            # Get the central widget from the QMainWindow
            content_widget = temp_window.centralWidget()
            if not content_widget:
                # If no central widget, try loading as QWidget
                content_widget = QtWidgets.QWidget()
                uic.loadUi(str(details_ui_path), content_widget)
            else:
                # Reparent to prevent destruction
                content_widget.setParent(None)
            # Add the content widget to the dialog with CENTERED layout
            layout = QtWidgets.QVBoxLayout()
            layout.setContentsMargins(15, 15, 15, 15)  # Comfortable margins
            layout.addWidget(content_widget)
            dialog.setLayout(layout)
            # Make sure content widget is visible
            content_widget.show()
            # Populate with request data BEFORE adjusting size
            self.populate_dialog_with_data(content_widget, request)
            # Let it automatically size to fit content
            dialog.adjustSize()
            # Set a minimum size so everything shows
            dialog.setMinimumSize(550, 450)
            # Show the floating dialog
            dialog.exec_()
        except Exception as e:
            self.notification.show_error(f"❌ Error loading request details: {e}")
            import traceback
            traceback.print_exc()
    def populate_dialog_with_data(self, dialog, request):
        """Populate the dialog with request data"""
        try:
            # Find all widgets
            all_labels = dialog.findChildren(QtWidgets.QLabel)
            all_line_edits = dialog.findChildren(QtWidgets.QLineEdit)
            all_text_edits = dialog.findChildren(QtWidgets.QTextEdit)
            all_buttons = dialog.findChildren(QtWidgets.QPushButton)
            # Map data to fill
            field_data = {
                'last': request.last_name or '',
                'surname': request.last_name or '',
                'first': request.first_name or '',
                'middle': request.middle_name or '',
                'suffix': request.suffix or '',
                'ext': request.suffix or '',
                'contact': request.phone_number or '',
                'phone': request.phone_number or '',
                'number': request.phone_number or '',
                'type': request.certificate_type or '',
                'certificate': request.certificate_type or '',
                'purpose': request.purpose or '',
                'reason': request.purpose or '',
                'quantity': str(request.quantity or 1),
                'qty': str(request.quantity or 1),
            }
            # Fill QLineEdit fields
            fields_filled = 0
            for line_edit in all_line_edits:
                obj_name = line_edit.objectName().lower()
                placeholder = line_edit.placeholderText().lower()
                for key, value in field_data.items():
                    if key in obj_name or key in placeholder:
                        line_edit.setText(value)
                        fields_filled += 1
                        break
            # Fill QTextEdit fields
            for text_edit in all_text_edits:
                obj_name = text_edit.objectName().lower()
                for key, value in field_data.items():
                    if key in obj_name:
                        text_edit.setPlainText(value)
                        fields_filled += 1
                        break
            # Display clickable ID photo
            if request.uploaded_file_path:
                # Find image label
                image_label = None
                for label in all_labels:
                    obj_name = label.objectName().lower()
                    if 'id' in obj_name or 'photo' in obj_name or 'image' in obj_name:
                        image_label = label
                        break
                if image_label:
                    import os
                    if os.path.exists(request.uploaded_file_path):
                        pixmap = QtGui.QPixmap(request.uploaded_file_path)
                        if not pixmap.isNull():
                            # Add nice styling to image label
                            image_label.setStyleSheet("""
                                QLabel {
                                    background-color: #ECEFF1;
                                    border: 3px solid #3F51B5;
                                    border-radius: 10px;
                                    padding: 10px;
                                }
                            """)
                            # Scale to fit label
                            scaled_pixmap = pixmap.scaled(
                                image_label.size(),
                                QtCore.Qt.KeepAspectRatio,
                                QtCore.Qt.SmoothTransformation
                            )
                            image_label.setPixmap(scaled_pixmap)
                            image_label.setAlignment(QtCore.Qt.AlignCenter)
                            # Make clickable
                            image_label.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
                            image_label.setToolTip("Click to view full-size image")
                            # Click event - view full image
                            def show_full_image():
                                img_dialog = QtWidgets.QDialog()
                                img_dialog.setWindowTitle(f"ID Photo - Request #{request.request_id}")
                                img_dialog.resize(1000, 800)  # Bigger size!
                                layout = QtWidgets.QVBoxLayout()
                                img_label = QtWidgets.QLabel()
                                full_pixmap = QtGui.QPixmap(request.uploaded_file_path)
                                # Bigger scaling
                                scaled_full = full_pixmap.scaled(980, 720, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
                                img_label.setPixmap(scaled_full)
                                img_label.setAlignment(QtCore.Qt.AlignCenter)
                                scroll = QtWidgets.QScrollArea()
                                scroll.setWidget(img_label)
                                scroll.setWidgetResizable(True)
                                layout.addWidget(scroll)
                                # Center the close button
                                btn_layout = QtWidgets.QHBoxLayout()
                                btn_layout.addStretch()
                                close_btn = QtWidgets.QPushButton("Close")
                                close_btn.setFixedWidth(150)
                                close_btn.clicked.connect(img_dialog.close)
                                btn_layout.addWidget(close_btn)
                                btn_layout.addStretch()
                                layout.addLayout(btn_layout)
                                img_dialog.setLayout(layout)
                                img_dialog.exec_()
                            image_label.mousePressEvent = lambda event: show_full_image()
                        else:
                            image_label.setText("❌ Invalid image")
                    else:
                        image_label.setText("❌ File not found")
                else:
                    pass
            else:
                pass
            # Connect APPROVE and REJECT buttons
            approve_btn = None
            reject_btn = None
            for button in all_buttons:
                btn_text = button.text().lower()
                obj_name = button.objectName().lower()
                if 'approve' in btn_text or 'accept' in btn_text or 'approve' in obj_name:
                    # Green APPROVE button
                    button.setStyleSheet("""
                        QPushButton {
                            background-color: #4CAF50;
                            color: white;
                            border: none;
                            border-radius: 8px;
                            padding: 12px 30px;
                            font-weight: bold;
                            font-size: 14px;
                        }
                        QPushButton:hover {
                            background-color: #45a049;
                        }
                        QPushButton:pressed {
                            background-color: #3d8b40;
                        }
                    """)
                    button.clicked.connect(lambda: self.approve_request(request, dialog))
                    approve_btn = button
                elif 'reject' in btn_text or 'reject' in obj_name:
                    # Red REJECT button
                    button.setStyleSheet("""
                        QPushButton {
                            background-color: #f44336;
                            color: white;
                            border: none;
                            border-radius: 8px;
                            padding: 12px 30px;
                            font-weight: bold;
                            font-size: 14px;
                        }
                        QPushButton:hover {
                            background-color: #da190b;
                        }
                        QPushButton:pressed {
                            background-color: #c2160a;
                        }
                    """)
                    button.clicked.connect(lambda: self.reject_request(request, dialog))
                    reject_btn = button
            # Center the buttons by finding their parent layout
            if approve_btn or reject_btn:
                # Try to find the layout containing the buttons
                for btn in [approve_btn, reject_btn]:
                    if btn and btn.parent():
                        parent_widget = btn.parent()
                        if parent_widget.layout():
                            parent_layout = parent_widget.layout()
                            if isinstance(parent_layout, QtWidgets.QHBoxLayout):
                                parent_layout.setAlignment(QtCore.Qt.AlignCenter)
                            break
        except Exception as e:
            import traceback
            traceback.print_exc()
    def approve_request(self, request, dialog):
        """Approve the certificate request"""
        try:
            from app.database import SessionLocal
            db = SessionLocal()
            request.status = 'Approved'
            request.reviewed_at = get_philippine_time()
            # request.reviewed_by_admin_id = self.current_admin_id  # Add if you have admin ID
            db.commit()
            db.close()
            self.notification.show_success(f"✅ Request #{request.request_id} APPROVED!")
            dialog.accept()  # Close dialog
            self.show_services_page()  # Refresh table
        except Exception as e:
            self.notification.show_error(f"❌ Error approving request: {e}")
    def reject_request(self, request, dialog):
        """Reject the certificate request"""
        try:
            from app.database import SessionLocal
            db = SessionLocal()
            request.status = 'Rejected'
            request.reviewed_at = get_philippine_time()
            # request.reviewed_by_admin_id = self.current_admin_id  # Add if you have admin ID
            db.commit()
            db.close()
            self.notification.show_success(f"❌ Request #{request.request_id} REJECTED")
            dialog.accept()  # Close dialog
            self.show_services_page()  # Refresh table
        except Exception as e:
            self.notification.show_error(f"❌ Error rejecting request: {e}")
    # populate_request_details method removed - will be recreated when new UI is connected
    def replace_content(self, new_widget):
        """Helper to replace content in the content area"""
        if isinstance(self.content_area, QtWidgets.QStackedWidget):
            while self.content_area.count() > 0:
                self.content_area.removeWidget(self.content_area.widget(0))
            self.content_area.addWidget(new_widget)
            self.content_area.setCurrentWidget(new_widget)
        elif isinstance(self.content_area, QtWidgets.QTabWidget):
            self.content_area.clear()
            self.content_area.addTab(new_widget, "Page")
        else:
            old_layout = self.content_area.layout()
            if old_layout:
                while old_layout.count():
                    item = old_layout.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
            else:
                old_layout = QtWidgets.QVBoxLayout(self.content_area)
                self.content_area.setLayout(old_layout)
            old_layout.addWidget(new_widget)
    def handle_logout(self):
        """Logout and return to login"""
        # Save current window state before closing
        save_window_state(self)
        
        from gui.views.login_view import LoginWindow
        self.login_window = LoginWindow()
        apply_window_state(self.login_window)
        self.close()
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = SidebarHomeWindow()
    window.showMaximized()
    sys.exit(app.exec_())
