# gui/views/sidebar_home_user_view.py
from PyQt5 import uic, QtWidgets, QtCore, QtGui
from pathlib import Path
from gui.widgets.notification_bar import NotificationBar
from gui.window_state import save_window_state, apply_window_state
from app.db import SessionLocal
from app.models import Resident, Account
from app.config import get_philippine_time
import math

UI_PATH = Path(__file__).resolve().parent.parent / "ui" / "sidebarhomee_USER.ui"


# ============ ANIMATED CHART WIDGETS ============

class AnimatedCounterLabel(QtWidgets.QLabel):
    """Label that animates counting up to a target value"""
    
    def __init__(self, target_value=0, parent=None):
        super().__init__(parent)
        self.target_value = target_value
        self.current_value = 0
        self.setText("0")
        
        # Animation timer
        self.animation_timer = QtCore.QTimer(self)
        self.animation_timer.timeout.connect(self.update_count)
        self.animation_timer.start(30)  # 30ms interval
        
    def update_count(self):
        if self.current_value < self.target_value:
            # Increment by 1 or more for larger numbers
            increment = max(1, self.target_value // 20)
            self.current_value = min(self.current_value + increment, self.target_value)
            self.setText(str(self.current_value))
        else:
            self.animation_timer.stop()


class AnimatedBarChart(QtWidgets.QWidget):
    """Animated bar chart widget for request summary - shows REAL data from database"""
    
    def __init__(self, request_data=None, parent=None):
        super().__init__(parent)
        self.setMinimumSize(200, 200)
        
        # If request_data is provided, use it; otherwise use empty data
        if request_data:
            self.labels = request_data.get('labels', [])
            self.values = request_data.get('values', [])
        else:
            # Default empty data - 7 days with 0 values
            self.labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            self.values = [0, 0, 0, 0, 0, 0, 0]
        
        # Calculate target heights based on max value (handle empty/zero data)
        max_val = max(self.values) if self.values and max(self.values) > 0 else 1
        self.target_heights = [v / max_val if max_val > 0 else 0 for v in self.values]
        self.current_heights = [0.0] * len(self.values)
        
        # Colors for bars
        self.bar_colors = [
            QtGui.QColor(30, 144, 255),   # Dodger Blue
            QtGui.QColor(0, 191, 255),    # Deep Sky Blue
            QtGui.QColor(135, 206, 250),  # Light Sky Blue
            QtGui.QColor(70, 130, 180),   # Steel Blue
            QtGui.QColor(100, 149, 237),  # Cornflower Blue
            QtGui.QColor(65, 105, 225),   # Royal Blue
            QtGui.QColor(0, 206, 209),    # Dark Turquoise
            QtGui.QColor(32, 178, 170),   # Light Sea Green
            QtGui.QColor(0, 139, 139),    # Dark Cyan
            QtGui.QColor(72, 61, 139),    # Dark Slate Blue
            QtGui.QColor(123, 104, 238),  # Medium Slate Blue
            QtGui.QColor(106, 90, 205),   # Slate Blue
        ]
        
        # Animation
        self.animation_timer = QtCore.QTimer(self)
        self.animation_timer.timeout.connect(self.animate_bars)
        self.animation_timer.start(20)
        
        # Hover animation
        self.hovered_bar = -1
        self.setMouseTracking(True)
    
    def update_data(self, request_data):
        """Update chart with new data and restart animation"""
        if request_data:
            self.labels = request_data.get('labels', [])
            self.values = request_data.get('values', [])
        else:
            self.labels = []
            self.values = []
        
        # Recalculate target heights
        max_val = max(self.values) if self.values and max(self.values) > 0 else 1
        self.target_heights = [v / max_val if max_val > 0 else 0 for v in self.values]
        self.current_heights = [0.0] * len(self.values)
        
        # Restart animation
        self.animation_timer.start(20)
        self.update()
        
    def animate_bars(self):
        all_done = True
        for i in range(len(self.current_heights)):
            if self.current_heights[i] < self.target_heights[i]:
                self.current_heights[i] = min(
                    self.current_heights[i] + 0.03,
                    self.target_heights[i]
                )
                all_done = False
        
        if all_done:
            self.animation_timer.stop()
        self.update()
    
    def mouseMoveEvent(self, event):
        # Detect which bar is hovered
        if not self.values:
            return
            
        width = self.width()
        bar_count = len(self.values)
        if bar_count == 0:
            return
        bar_width = (width - 60) / bar_count - 10
        
        x = event.x()
        new_hovered = -1
        
        for i in range(bar_count):
            bar_x = 40 + i * ((width - 60) / bar_count) + 5
            if bar_x <= x <= bar_x + bar_width:
                new_hovered = i
                break
        
        if new_hovered != self.hovered_bar:
            self.hovered_bar = new_hovered
            self.update()
    
    def leaveEvent(self, event):
        self.hovered_bar = -1
        self.update()
        
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        width = self.width()
        height = self.height()
        
        # Background
        painter.fillRect(self.rect(), QtGui.QColor(250, 250, 250))
        
        # Draw grid lines
        painter.setPen(QtGui.QPen(QtGui.QColor(220, 220, 220), 1))
        for i in range(5):
            y = 30 + i * (height - 80) / 4
            painter.drawLine(40, int(y), width - 20, int(y))
        
        # Handle empty data
        if not self.values or len(self.values) == 0:
            painter.setPen(QtGui.QColor(150, 150, 150))
            painter.setFont(QtGui.QFont("Arial", 12))
            painter.drawText(self.rect(), QtCore.Qt.AlignCenter, "No request data available")
            return
        
        # Draw bars
        bar_count = len(self.values)
        bar_width = (width - 60) / bar_count - 10
        max_bar_height = height - 80
        
        for i in range(len(self.labels)):
            if i >= len(self.values) or i >= len(self.current_heights):
                continue
                
            label = self.labels[i]
            value = self.values[i]
            h = self.current_heights[i]
            
            bar_x = 40 + i * ((width - 60) / bar_count) + 5
            bar_height = h * max_bar_height
            bar_y = height - 50 - bar_height
            
            # Only draw bar if there's a value
            if value > 0 and bar_height > 0:
                # Bar shadow
                shadow_color = QtGui.QColor(0, 0, 0, 30)
                painter.fillRect(
                    QtCore.QRectF(bar_x + 3, bar_y + 3, bar_width, bar_height),
                    shadow_color
                )
                
                # Bar gradient
                color = self.bar_colors[i % len(self.bar_colors)]
                if i == self.hovered_bar:
                    color = color.lighter(120)
                
                gradient = QtGui.QLinearGradient(bar_x, bar_y, bar_x + bar_width, bar_y)
                gradient.setColorAt(0, color)
                gradient.setColorAt(1, color.darker(110))
                
                # Draw rounded bar
                path = QtGui.QPainterPath()
                path.addRoundedRect(
                    QtCore.QRectF(bar_x, bar_y, bar_width, bar_height),
                    5, 5
                )
                painter.fillPath(path, gradient)
                
                # Value label on top of bar
                if bar_height > 20:
                    painter.setPen(QtGui.QColor(255, 255, 255))
                    painter.setFont(QtGui.QFont("Arial", 9, QtGui.QFont.Bold))
                    painter.drawText(
                        QtCore.QRectF(bar_x, bar_y + 5, bar_width, 20),
                        QtCore.Qt.AlignCenter,
                        str(int(value))
                    )
            else:
                # Draw a thin baseline for zero values
                painter.setPen(QtGui.QPen(QtGui.QColor(200, 200, 200), 2))
                baseline_y = height - 50
                painter.drawLine(int(bar_x), int(baseline_y), int(bar_x + bar_width), int(baseline_y))
            
            # Label below (always show)
            painter.setPen(QtGui.QColor(80, 80, 80))
            painter.setFont(QtGui.QFont("Arial", 8))
            painter.drawText(
                QtCore.QRectF(bar_x, height - 40, bar_width, 30),
                QtCore.Qt.AlignCenter,
                label
            )
        
        # Y-axis label
        painter.setPen(QtGui.QColor(100, 100, 100))
        painter.setFont(QtGui.QFont("Arial", 8))
        painter.save()
        painter.translate(15, height / 2)
        painter.rotate(-90)
        painter.drawText(QtCore.QRectF(-50, -10, 100, 20), QtCore.Qt.AlignCenter, "Requests")
        painter.restore()


class AnimatedPieChart(QtWidgets.QWidget):
    """Animated pie chart widget for request distribution"""
    
    def __init__(self, stats=None, parent=None):
        super().__init__(parent)
        self.setMinimumSize(150, 150)
        
        # Data from stats
        if stats:
            self.data = [
                ("ID", stats.get('barangay_id', 5), QtGui.QColor(30, 144, 255)),
                ("Permit", stats.get('business_permit', 3), QtGui.QColor(255, 165, 0)),
                ("Indigency", stats.get('indigency', 8), QtGui.QColor(50, 205, 50)),
                ("Clearance", stats.get('clearance', 6), QtGui.QColor(147, 112, 219)),
            ]
        else:
            self.data = [
                ("ID", 5, QtGui.QColor(30, 144, 255)),
                ("Permit", 3, QtGui.QColor(255, 165, 0)),
                ("Indigency", 8, QtGui.QColor(50, 205, 50)),
                ("Clearance", 6, QtGui.QColor(147, 112, 219)),
            ]
        
        self.total = sum(d[1] for d in self.data) or 1
        self.current_angle = 0
        self.target_angle = 360 * 16  # Full circle in 1/16th degrees
        
        # Animation
        self.animation_timer = QtCore.QTimer(self)
        self.animation_timer.timeout.connect(self.animate_pie)
        self.animation_timer.start(15)
        
        # Hover
        self.hovered_segment = -1
        self.setMouseTracking(True)
        
        # Rotation animation for visual effect
        self.rotation_offset = 0
        
    def animate_pie(self):
        if self.current_angle < self.target_angle:
            self.current_angle = min(self.current_angle + 200, self.target_angle)
            self.update()
        else:
            # Subtle continuous rotation
            self.rotation_offset = (self.rotation_offset + 1) % 360
            self.update()
    
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        width = self.width()
        height = self.height()
        
        # Calculate pie dimensions
        size = min(width, height) - 20
        pie_rect = QtCore.QRectF(
            (width - size) / 2,
            (height - size) / 2 - 10,
            size,
            size
        )
        
        # Draw segments
        start_angle = 90 * 16 + self.rotation_offset * 16  # Start from top
        
        for i, (label, value, color) in enumerate(self.data):
            span_angle = int((value / self.total) * self.current_angle)
            
            # Hover effect
            draw_rect = pie_rect
            if i == self.hovered_segment:
                # Explode the segment outward
                mid_angle = (start_angle + span_angle / 2) / 16
                rad = math.radians(mid_angle)
                offset_x = math.cos(rad) * 5
                offset_y = -math.sin(rad) * 5
                draw_rect = pie_rect.adjusted(offset_x, offset_y, offset_x, offset_y)
            
            # Draw pie slice with gradient
            gradient = QtGui.QRadialGradient(
                draw_rect.center(),
                size / 2
            )
            gradient.setColorAt(0, color.lighter(120))
            gradient.setColorAt(1, color)
            
            painter.setBrush(gradient)
            painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255), 2))
            painter.drawPie(draw_rect, start_angle, span_angle)
            
            start_angle += span_angle
        
        # Draw center circle (donut effect)
        center_size = size * 0.4
        center_rect = QtCore.QRectF(
            (width - center_size) / 2,
            (height - center_size) / 2 - 10,
            center_size,
            center_size
        )
        painter.setBrush(QtGui.QColor(250, 250, 250))
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawEllipse(center_rect)
        
        # Draw total in center
        painter.setPen(QtGui.QColor(50, 50, 50))
        painter.setFont(QtGui.QFont("Arial", 12, QtGui.QFont.Bold))
        painter.drawText(center_rect, QtCore.Qt.AlignCenter, str(self.total))
        
        # Draw legend
        legend_x = 10
        legend_y = height - 25
        legend_spacing = (width - 20) / len(self.data)
        
        painter.setFont(QtGui.QFont("Arial", 7))
        for i, (label, value, color) in enumerate(self.data):
            x = legend_x + i * legend_spacing
            
            # Color box
            painter.fillRect(QtCore.QRectF(x, legend_y, 10, 10), color)
            
            # Label
            painter.setPen(QtGui.QColor(80, 80, 80))
            painter.drawText(
                QtCore.QRectF(x + 12, legend_y - 2, legend_spacing - 15, 15),
                QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter,
                f"{label}"
            )


class AnimatedCircleProgress(QtWidgets.QWidget):
    """Animated circular progress widget with number in center - like budget report style"""
    
    def __init__(self, value=0, max_value=100, title="", color1=None, color2=None, parent=None):
        super().__init__(parent)
        self.value = value
        self.max_value = max_value if max_value > 0 else 1
        self.title = title
        
        # Gradient colors for the progress arc
        self.color1 = color1 or QtGui.QColor(255, 100, 150)  # Pink/Red
        self.color2 = color2 or QtGui.QColor(100, 150, 255)  # Blue
        
        # Animation properties
        self.current_progress = 0.0
        self.target_progress = min(value / self.max_value, 1.0) if max_value > 0 else 0
        self.current_value_display = 0
        
        # Glow/pulse animation
        self.glow_intensity = 0
        self.glow_direction = 1
        
        self.setMinimumSize(120, 140)
        
        # Animation timer
        self.animation_timer = QtCore.QTimer(self)
        self.animation_timer.timeout.connect(self.animate)
        self.animation_timer.start(16)  # ~60fps
    
    def animate(self):
        changed = False
        
        # Animate progress arc
        if self.current_progress < self.target_progress:
            self.current_progress = min(self.current_progress + 0.02, self.target_progress)
            changed = True
        
        # Animate counter value
        if self.current_value_display < self.value:
            increment = max(1, self.value // 20)
            self.current_value_display = min(self.current_value_display + increment, self.value)
            changed = True
        
        # Animate glow effect (continuous pulse)
        self.glow_intensity += 0.05 * self.glow_direction
        if self.glow_intensity >= 1:
            self.glow_direction = -1
        elif self.glow_intensity <= 0:
            self.glow_direction = 1
        changed = True
        
        if changed:
            self.update()
    
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        width = self.width()
        height = self.height()
        
        # Circle dimensions
        circle_size = min(width, height - 30) - 20
        circle_x = (width - circle_size) / 2
        circle_y = 10
        circle_rect = QtCore.QRectF(circle_x, circle_y, circle_size, circle_size)
        
        # Draw outer glow effect
        glow_size = circle_size + 10 + (self.glow_intensity * 5)
        glow_rect = QtCore.QRectF(
            (width - glow_size) / 2,
            circle_y - 5 - (self.glow_intensity * 2.5),
            glow_size,
            glow_size
        )
        
        glow_gradient = QtGui.QRadialGradient(glow_rect.center(), glow_size / 2)
        glow_color = QtGui.QColor(self.color1)
        glow_color.setAlpha(int(30 + self.glow_intensity * 40))
        glow_gradient.setColorAt(0.7, glow_color)
        glow_gradient.setColorAt(1, QtGui.QColor(0, 0, 0, 0))
        painter.setBrush(glow_gradient)
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawEllipse(glow_rect)
        
        # Draw background circle (dark track)
        painter.setPen(QtGui.QPen(QtGui.QColor(50, 50, 70), 8))
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.drawEllipse(circle_rect.adjusted(4, 4, -4, -4))
        
        # Draw progress arc with gradient
        if self.current_progress > 0:
            arc_width = 10
            arc_rect = circle_rect.adjusted(4, 4, -4, -4)
            
            # Create conical gradient for rainbow effect
            gradient = QtGui.QConicalGradient(arc_rect.center(), 90)
            gradient.setColorAt(0, self.color1)
            gradient.setColorAt(0.5, self.color2)
            gradient.setColorAt(1, self.color1)
            
            pen = QtGui.QPen(QtGui.QBrush(gradient), arc_width)
            pen.setCapStyle(QtCore.Qt.RoundCap)
            painter.setPen(pen)
            
            # Draw arc (from top, clockwise)
            start_angle = 90 * 16  # Start from top
            span_angle = int(-self.current_progress * 360 * 16)  # Negative for clockwise
            painter.drawArc(arc_rect, start_angle, span_angle)
        
        # Draw inner circle (center) - WHITE background for readability
        inner_size = circle_size * 0.7
        inner_rect = QtCore.QRectF(
            (width - inner_size) / 2,
            circle_y + (circle_size - inner_size) / 2,
            inner_size,
            inner_size
        )
        
        # Inner circle gradient - WHITE for readable text
        inner_gradient = QtGui.QRadialGradient(inner_rect.center(), inner_size / 2)
        inner_gradient.setColorAt(0, QtGui.QColor(255, 255, 255))  # White center
        inner_gradient.setColorAt(1, QtGui.QColor(240, 240, 245))  # Slightly gray edge
        
        painter.setBrush(inner_gradient)
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawEllipse(inner_rect)
        
        # Draw value in center - DARK text on white background
        painter.setPen(QtGui.QColor(30, 30, 50))  # Dark text
        painter.setFont(QtGui.QFont("Arial", int(inner_size / 3), QtGui.QFont.Bold))
        painter.drawText(inner_rect, QtCore.Qt.AlignCenter, str(self.current_value_display))
        
        # Draw title below circle
        title_rect = QtCore.QRectF(0, circle_y + circle_size + 5, width, 25)
        painter.setPen(QtGui.QColor(50, 50, 50))
        painter.setFont(QtGui.QFont("Arial", 8, QtGui.QFont.Bold))
        painter.drawText(title_rect, QtCore.Qt.AlignCenter, self.title)


# ============ MAIN WINDOW CLASS ============

class SidebarHomeUserWindow(QtWidgets.QMainWindow):
    """User Dashboard Interface - For Residents"""
    
    def __init__(self, username=None):
        super().__init__()
        uic.loadUi(str(UI_PATH), self)
        
        self.username = username
        self.account = None
        self.resident = None
        
        # Load user data
        self.load_user_data()
        
        # Set window properties - FULLSCREEN CAPABLE
        self.setWindowTitle("Barangay E-Services - User Dashboard")
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
        
        # Show welcome message
        if self.resident:
            self.notification.show_success(f"✅ Welcome, {self.resident.first_name}!")
    
    def load_user_data(self):
        """Load user account and resident data"""
        if not self.username:
            return
            
        db = SessionLocal()
        try:
            self.account = db.query(Account).filter(Account.username == self.username).first()
            if self.account and self.account.resident_id:
                self.resident = db.query(Resident).filter(
                    Resident.resident_id == self.account.resident_id
                ).first()
        except Exception as e:
            pass
        finally:
            db.close()
    
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
        
        # DASHBOARD button (pushButton_15)
        if hasattr(self, 'pushButton_15'):
            self.pushButton_15.clicked.connect(self.show_dashboard_page)

        # SERVICES button (pushButton_13)
        if hasattr(self, 'pushButton_13'):
            self.pushButton_13.clicked.connect(self.show_services_page)

        # NOTIFICATIONS button (pushButton_17)
        if hasattr(self, 'pushButton_17'):
            self.pushButton_17.clicked.connect(self.show_notifications_page)

        # ANNOUNCEMENT button (pushButton_18)
        if hasattr(self, 'pushButton_18'):
            self.pushButton_18.clicked.connect(self.show_announcement_page)

        # MY REQUEST button (pushButton_14)
        if hasattr(self, 'pushButton_14'):
            self.pushButton_14.clicked.connect(self.show_my_request_page)

        # PAYMENT button (pushButton_16)
        if hasattr(self, 'pushButton_16'):
            self.pushButton_16.clicked.connect(self.show_payment_page)

        # HISTORY button (pushButton_19)
        if hasattr(self, 'pushButton_19'):
            self.pushButton_19.clicked.connect(self.show_history_page)

        # BLOTTER button (pushButton_20)
        if hasattr(self, 'pushButton_20'):
            self.pushButton_20.clicked.connect(self.show_blotter_page)

        # OFFICIALS button (pushButton_11)
        if hasattr(self, 'pushButton_11'):
            self.pushButton_11.clicked.connect(self.show_officials_page)

        # ALL ABOUT button (pushButton_24)
        if hasattr(self, 'pushButton_24'):
            self.pushButton_24.clicked.connect(self.show_allabout_page)

        # PROFILE button (pushButton_12) - Logout
        if hasattr(self, 'pushButton_12'):
            self.pushButton_12.clicked.connect(self.handle_logout)

    def show_dashboard_page(self):
        """Show dashboard page - creates responsive dashboard that expands with window"""
        try:
            # Initialize filter state
            if not hasattr(self, 'dashboard_filter'):
                self.dashboard_filter = {
                    'type': 'year',  # Default to year for monthly breakdown
                    'start_date': None,
                    'end_date': None,
                }

            # Create a fully responsive dashboard using code instead of fixed UI
            dashboard_widget = self.create_responsive_dashboard()
            
            # Replace content in the stacked widget
            self.replace_content(dashboard_widget)
            
            self.notification.show_info("📊 Dashboard loaded")

        except Exception as e:
            self.notification.show_error(f"❌ Error loading dashboard: {e}")

            import traceback
            traceback.print_exc()
    
    def show_filter_menu(self):
        """Show filter menu for dashboard date range"""
        menu = QtWidgets.QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 2px solid rgb(100, 150, 220);
                border-radius: 8px;
                padding: 5px;
            }
            QMenu::item:selected {
                background-color: rgb(100, 150, 220);
                color: white;
            }
        """)
        
        # Filter options
        today_action = menu.addAction("📅 Today")
        today_action.triggered.connect(lambda: self.apply_date_filter('today'))
        
        week_action = menu.addAction("📆 This Week")
        week_action.triggered.connect(lambda: self.apply_date_filter('week'))
        
        month_action = menu.addAction("📊 This Month")
        month_action.triggered.connect(lambda: self.apply_date_filter('month'))
        
        year_action = menu.addAction("📈 This Year")
        year_action.triggered.connect(lambda: self.apply_date_filter('year'))
        
        menu.addSeparator()
        
        all_action = menu.addAction("🔄 All Time")
        all_action.triggered.connect(lambda: self.apply_date_filter('all'))
        
        custom_action = menu.addAction("📌 Custom Range")
        custom_action.triggered.connect(self.show_custom_date_picker)
        
        # Show menu at cursor position
        menu.exec_(QtGui.QCursor.pos())
    
    def apply_date_filter(self, filter_type):
        """Apply date filter and refresh dashboard"""
        from datetime import datetime, timedelta
        
        if not hasattr(self, 'dashboard_filter'):
            self.dashboard_filter = {}
        
        today = datetime.now().date()
        
        if filter_type == 'today':
            self.dashboard_filter['type'] = 'today'
            self.dashboard_filter['start_date'] = today
            self.dashboard_filter['end_date'] = today
            self.notification.show_info("📅 Showing today's data")
        elif filter_type == 'week':
            self.dashboard_filter['type'] = 'week'
            start = today - timedelta(days=today.weekday())  # Monday
            self.dashboard_filter['start_date'] = start
            self.dashboard_filter['end_date'] = today
            self.notification.show_info("📆 Showing this week's data")
        elif filter_type == 'month':
            self.dashboard_filter['type'] = 'month'
            self.dashboard_filter['start_date'] = today.replace(day=1)
            self.dashboard_filter['end_date'] = today
            self.notification.show_info("📊 Showing this month's data")
        elif filter_type == 'year':
            self.dashboard_filter['type'] = 'year'
            self.dashboard_filter['start_date'] = today.replace(month=1, day=1)
            self.dashboard_filter['end_date'] = today
            self.notification.show_info("📈 Showing this year's data")
        elif filter_type == 'all':
            self.dashboard_filter['type'] = 'all'
            self.dashboard_filter['start_date'] = None
            self.dashboard_filter['end_date'] = None
            self.notification.show_info("🔄 Showing all-time data")
        
        # Refresh dashboard
        self.show_dashboard_page()
    
    def show_custom_date_picker(self):
        """Show custom date range picker dialog"""
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Select Custom Date Range")
        dialog.setFixedSize(600, 380)
        dialog.setStyleSheet("""
            QDialog { background-color: #f5f5f5; }
            QLabel { font-size: 13pt; font-weight: bold; color: #333; margin-top: 10px; }
            QDateEdit {
                padding: 12px;
                border: 2px solid #ddd;
                border-radius: 5px;
                font-size: 12pt;
                min-height: 50px;
                background: white;
            }
            QDateEdit:focus {
                border: 2px solid #1e3c72;
            }
        """)
        
        layout = QtWidgets.QVBoxLayout(dialog)
        layout.setSpacing(20)
        layout.setContentsMargins(35, 35, 35, 35)
        
        # Start date
        start_label = QtWidgets.QLabel("Start Date:")
        start_label.setMinimumHeight(30)
        layout.addWidget(start_label)
        start_date_edit = QtWidgets.QDateEdit()
        start_date_edit.setDate(QtCore.QDate.currentDate().addMonths(-1))
        start_date_edit.setCalendarPopup(True)
        start_date_edit.setMinimumHeight(50)
        layout.addWidget(start_date_edit)
        
        # End date
        end_label = QtWidgets.QLabel("End Date:")
        end_label.setMinimumHeight(30)
        layout.addWidget(end_label)
        end_date_edit = QtWidgets.QDateEdit()
        end_date_edit.setDate(QtCore.QDate.currentDate())
        end_date_edit.setCalendarPopup(True)
        end_date_edit.setMinimumHeight(50)
        layout.addWidget(end_date_edit)
        
        # Add spacing before buttons (push buttons down)
        layout.addSpacing(30)
        
        # Buttons
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.setSpacing(20)
        
        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.setMinimumHeight(50)
        cancel_btn.setMinimumWidth(140)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: #95a5a6;
                color: white;
                padding: 12px 25px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12pt;
            }
            QPushButton:hover { background: #7f8c8d; }
        """)
        cancel_btn.clicked.connect(dialog.reject)
        
        apply_btn = QtWidgets.QPushButton("Apply Filter")
        apply_btn.setMinimumHeight(50)
        apply_btn.setMinimumWidth(160)
        apply_btn.setStyleSheet("""
            QPushButton {
                background: #27ae60;
                color: white;
                padding: 12px 25px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12pt;
            }
            QPushButton:hover { background: #2ecc71; }
        """)
        
        def apply_custom():
            if not hasattr(self, 'dashboard_filter'):
                self.dashboard_filter = {}
            
            self.dashboard_filter['type'] = 'custom'
            self.dashboard_filter['start_date'] = start_date_edit.date().toPyDate()
            self.dashboard_filter['end_date'] = end_date_edit.date().toPyDate()
            
            dialog.accept()
            self.notification.show_info(f"📌 Filter applied: {self.dashboard_filter['start_date']} to {self.dashboard_filter['end_date']}")
            self.show_dashboard_page()
        
        apply_btn.clicked.connect(apply_custom)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(apply_btn)
        layout.addLayout(btn_layout)
        
        dialog.exec_()
    
    def create_responsive_dashboard(self):
        """Create a responsive dashboard that expands with window size"""
        # Main container with scroll area
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)
        scroll_area.setStyleSheet("QScrollArea { border: none; background-color: rgb(221, 221, 221); }")
        
        main_widget = QtWidgets.QWidget()
        main_widget.setStyleSheet("background-color: rgb(221, 221, 221);")
        main_layout = QtWidgets.QVBoxLayout(main_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # === DASHBOARD HEADER WITH FILTER ===
        header_frame = QtWidgets.QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 rgb(30, 100, 180), stop:1 rgb(50, 150, 220));
                border-radius: 15px;
            }
        """)
        header_frame.setMinimumHeight(60)
        header_frame.setMaximumHeight(80)
        header_layout = QtWidgets.QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 10, 20, 10)
        header_layout.setSpacing(15)
        
        header_label = QtWidgets.QLabel("DASHBOARD")
        header_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 24pt;
                font-weight: bold;
                background: transparent;
            }
        """)
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        
        # Filter button
        filter_btn = QtWidgets.QPushButton("🔽 Filter")
        filter_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                color: white;
                border: 2px solid white;
                border-radius: 8px;
                padding: 8px 15px;
                font-weight: bold;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.4);
            }
        """)
        filter_btn.setMinimumWidth(120)
        filter_btn.clicked.connect(self.show_filter_menu)
        header_layout.addWidget(filter_btn)
        
        main_layout.addWidget(header_frame)
        
        # === CONTENT AREA ===
        content_widget = QtWidgets.QWidget()
        content_layout = QtWidgets.QHBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(20)
        
        # --- LEFT SIDE: Transaction with Animated Chart ---
        left_frame = QtWidgets.QFrame()
        left_frame.setStyleSheet("""
            QFrame {
                background-color: rgb(240, 240, 240);
                border-radius: 15px;
                border: 1px solid rgb(200, 200, 200);
            }
        """)
        left_layout = QtWidgets.QVBoxLayout(left_frame)
        left_layout.setContentsMargins(15, 15, 15, 15)
        left_layout.setSpacing(10)
        
        # Get current filter type for label
        filter_type = 'year'  # Default
        if hasattr(self, 'dashboard_filter'):
            filter_type = self.dashboard_filter.get('type', 'year')
        
        # Create filter-specific label
        filter_labels = {
            'today': "TODAY'S REQUESTS",
            'week': "THIS WEEK'S REQUESTS",
            'month': "THIS MONTH'S REQUESTS",
            'year': "THIS YEAR'S REQUESTS",
            'all': "ALL-TIME REQUESTS",
            'custom': "CUSTOM PERIOD REQUESTS"
        }
        label_text = filter_labels.get(filter_type, "REQUEST SUMMARY")
        
        weekly_label = QtWidgets.QLabel(label_text)
        weekly_label.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 rgb(0, 180, 255), stop:1 rgb(0, 220, 255));
                color: black;
                font-size: 14pt;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 20px;
            }
        """)
        weekly_label.setAlignment(QtCore.Qt.AlignCenter)
        left_layout.addWidget(weekly_label)
        
        # Get request summary data (filtered by date range)
        request_data = self.get_request_summary_data()
        
        # Add animated bar chart for request summary with real data
        bar_chart = AnimatedBarChart(request_data=request_data)
        bar_chart.setMinimumHeight(250)
        left_layout.addWidget(bar_chart, stretch=1)
        
        content_layout.addWidget(left_frame, stretch=2)
        
        # --- RIGHT SIDE: Certificate Cards Grid with Stats ---
        right_widget = QtWidgets.QWidget()
        right_layout = QtWidgets.QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(15)
        
        # Get real stats from database
        stats = self.get_dashboard_stats()
        
        # Certificate cards data with values
        certificates = [
            ("BARANGAY ID", stats.get('barangay_id', 0), "rgb(30, 100, 200)"),
            ("BUSINESS PERMIT", stats.get('business_permit', 0), "rgb(30, 100, 200)"),
            ("BARANGAY INDIGENCY", stats.get('indigency', 0), "rgb(30, 100, 200)"),
            ("BARANGAY CLEARANCE", stats.get('clearance', 0), "rgb(30, 100, 200)"),
        ]
        
        # Row 1: Barangay ID & Business Permit
        row1 = QtWidgets.QHBoxLayout()
        row1.setSpacing(15)
        for i in range(2):
            card = self.create_dashboard_card_with_value(
                certificates[i][0], certificates[i][1], certificates[i][2]
            )
            row1.addWidget(card)
        right_layout.addLayout(row1)
        
        # Row 2: Barangay Indigency & Barangay Clearance
        row2 = QtWidgets.QHBoxLayout()
        row2.setSpacing(15)
        for i in range(2, 4):
            card = self.create_dashboard_card_with_value(
                certificates[i][0], certificates[i][1], certificates[i][2]
            )
            row2.addWidget(card)
        right_layout.addLayout(row2)
        
        # Row 3: Request Status - Pending, Completed, Cancelled, Rejected
        row3 = QtWidgets.QHBoxLayout()
        row3.setSpacing(15)
        
        # Status cards with colors
        status_cards = [
            ("PENDING", stats.get('pending', 0), QtGui.QColor(255, 165, 0)),        # Orange
            ("COMPLETED", stats.get('completed', 0), QtGui.QColor(34, 139, 34)),    # Green
            ("CANCELLED", stats.get('cancelled', 0), QtGui.QColor(169, 169, 169)),  # Gray
            ("REJECTED", stats.get('rejected', 0), QtGui.QColor(220, 53, 69)),      # Red
        ]
        
        for status, value, color in status_cards:
            card = self.create_dashboard_card_with_value(
                status, value, color
            )
            row3.addWidget(card)
        
        right_layout.addLayout(row3)
        
        # Add pie chart for request distribution
        pie_chart_frame = QtWidgets.QFrame()
        pie_chart_frame.setStyleSheet("""
            QFrame {
                background-color: rgb(240, 240, 240);
                border-radius: 15px;
                border: 1px solid rgb(200, 200, 200);
            }
        """)
        pie_layout = QtWidgets.QVBoxLayout(pie_chart_frame)
        pie_layout.setContentsMargins(15, 15, 15, 15)
        
        pie_title = QtWidgets.QLabel("REQUEST DISTRIBUTION")
        pie_title.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 rgb(100, 50, 200), stop:1 rgb(150, 100, 250));
                color: white;
                font-size: 10pt;
                font-weight: bold;
                padding: 8px 15px;
                border-radius: 15px;
            }
        """)
        pie_title.setAlignment(QtCore.Qt.AlignCenter)
        pie_layout.addWidget(pie_title)
        
        pie_chart = AnimatedPieChart(stats)
        pie_chart.setMinimumHeight(150)
        pie_layout.addWidget(pie_chart, stretch=1)
        
        right_layout.addWidget(pie_chart_frame)
        
        content_layout.addWidget(right_widget, stretch=3)
        
        main_layout.addWidget(content_widget, stretch=1)
        
        scroll_area.setWidget(main_widget)
        return scroll_area
    
    def get_dashboard_stats(self):
        """Get statistics for the dashboard from database - ONLY for logged-in user"""
        stats = {
            'barangay_id': 0,
            'business_permit': 0,
            'indigency': 0,
            'clearance': 0,
            'completed': 0,
            'rejected': 0,
            'pending': 0,
            'cancelled': 0,
        }
        
        try:
            from app.db import SessionLocal
            from app.models import CertificateRequest
            from datetime import datetime
            
            # Ensure user is logged in and has a resident record
            if not self.account or not self.resident:
                print("❌ No user logged in - using sample data")
                return self._get_sample_stats()
            
            db = SessionLocal()
            resident_id = self.resident.resident_id
            
            # Query ONLY this resident's certificate requests
            query = db.query(CertificateRequest).filter(
                CertificateRequest.resident_id == resident_id
            )
            
            # Apply date filter if set
            if hasattr(self, 'dashboard_filter') and self.dashboard_filter.get('type') != 'all':
                start_date = self.dashboard_filter.get('start_date')
                end_date = self.dashboard_filter.get('end_date')
                
                if start_date and end_date:
                    # Filter by date range
                    query = query.filter(
                        CertificateRequest.created_at >= datetime.combine(start_date, datetime.min.time()),
                        CertificateRequest.created_at <= datetime.combine(end_date, datetime.max.time())
                    )
                    print(f"📅 Filter: {start_date} to {end_date}")
            
            requests = query.all()
            
            print(f"📊 Loaded {len(requests)} requests for resident {resident_id} ({self.username})")
            
            for req in requests:
                cert_type = (req.certificate_type or '').lower()
                status = (req.status or '').lower().strip()
                
                # Count certificate types
                if 'id' in cert_type:
                    stats['barangay_id'] += 1
                elif 'permit' in cert_type or 'business' in cert_type:
                    stats['business_permit'] += 1
                elif 'indigency' in cert_type:
                    stats['indigency'] += 1
                elif 'clearance' in cert_type:
                    stats['clearance'] += 1
                
                # Count statuses (map to dashboard categories)
                if 'completed' in status or 'complete' in status:
                    stats['completed'] += 1
                elif 'declined' in status or 'rejected' in status or 'reject' in status:
                    stats['rejected'] += 1
                elif 'cancelled' in status or 'cancel' in status:
                    stats['cancelled'] += 1
                elif 'pending' in status or 'processing' in status or 'under review' in status or 'ready' in status:
                    stats['pending'] += 1
            
            db.close()
        except Exception as e:
            print(f"❌ Error loading dashboard stats: {e}")
            return self._get_sample_stats()
        
        return stats
    
    def _get_sample_stats(self):
        """Return sample data for demo purposes"""
        return {
            'barangay_id': 5,
            'business_permit': 3,
            'indigency': 8,
            'clearance': 6,
            'completed': 12,
            'rejected': 2,
            'pending': 8,
            'cancelled': 3,
        }
    
    def get_request_summary_data(self):
        """Get request summary data for bar chart based on certificate requests"""
        from datetime import datetime, timedelta
        from collections import defaultdict
        
        try:
            from app.db import SessionLocal
            from app.models import CertificateRequest
            
            # Ensure user is logged in
            if not self.account or not self.resident:
                print(f"❌ No user logged in - account:{self.account} resident:{self.resident}")
                return {'labels': [], 'values': []}
            
            db = SessionLocal()
            resident_id = self.resident.resident_id
            print(f"📊 Getting request data for resident_id={resident_id}")
            
            # Determine date range based on filter
            filter_type = 'year'  # Default to year for better visibility
            start_date = None
            end_date = datetime.now().date()
            
            if hasattr(self, 'dashboard_filter'):
                filter_type = self.dashboard_filter.get('type', 'year')
                start_date = self.dashboard_filter.get('start_date')
                end_date = self.dashboard_filter.get('end_date') or datetime.now().date()
            
            # Set default start date based on filter type
            if not start_date:
                if filter_type == 'today':
                    start_date = end_date
                elif filter_type == 'week':
                    start_date = end_date - timedelta(days=6)
                elif filter_type == 'month':
                    start_date = end_date.replace(day=1)
                elif filter_type == 'year':
                    start_date = end_date.replace(month=1, day=1)
                else:  # all
                    start_date = datetime(2020, 1, 1).date()
            
            print(f"📅 Date range: {start_date} to {end_date}, filter: {filter_type}")
            
            # Query requests from CertificateRequest table for this resident
            requests_query = db.query(CertificateRequest).filter(
                CertificateRequest.resident_id == resident_id
            )
            
            # Apply date filter based on when request was created
            if start_date and end_date:
                requests_query = requests_query.filter(
                    CertificateRequest.created_at >= datetime.combine(start_date, datetime.min.time()),
                    CertificateRequest.created_at <= datetime.combine(end_date, datetime.max.time())
                )
            
            requests = requests_query.all()
            
            print(f"📄 Loaded {len(requests)} requests for resident {resident_id}")
            
            # Group requests by appropriate time period
            request_data = defaultdict(int)
            
            for req in requests:
                # Use created_at date for grouping
                req_date = req.created_at
                
                if req_date:
                    if filter_type == 'today':
                        # Round to nearest 3-hour block
                        hour_block = (req_date.hour // 3) * 3
                        key = datetime(2000, 1, 1, hour_block).strftime('%I %p').lstrip('0')
                    elif filter_type == 'week':
                        day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
                        key = day_names[req_date.weekday()]
                    elif filter_type == 'month':
                        week_num = (req_date.day - 1) // 7 + 1
                        key = f"Week {week_num}"
                    elif filter_type == 'year':
                        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                        key = month_names[req_date.month - 1]
                    else:  # all
                        key = str(req_date.year)
                    
                    request_data[key] += 1
            
            # Generate labels and values based on filter type
            if filter_type == 'today':
                labels = []
                for h in range(0, 24, 3):
                    label = datetime(2000, 1, 1, h).strftime('%I %p').lstrip('0')
                    labels.append(label)
                values = [request_data.get(l, 0) for l in labels]
                
            elif filter_type == 'week':
                labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
                values = [request_data.get(d, 0) for d in labels]
                
            elif filter_type == 'month':
                labels = ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5']
                values = [request_data.get(w, 0) for w in labels]
                
            elif filter_type == 'year':
                labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                         'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                values = [request_data.get(m, 0) for m in labels]
                
            else:  # all time
                if request_data:
                    labels = sorted(request_data.keys())
                    values = [request_data[y] for y in labels]
                else:
                    labels = [str(datetime.now().year)]
                    values = [0]
            
            db.close()
            
            total = sum(values)
            print(f"📊 Request summary (Total: {total}): {dict(zip(labels, values))}")
            
            return {'labels': labels, 'values': values}
            
        except Exception as e:
            print(f"❌ Error loading request summary: {e}")
            import traceback
            traceback.print_exc()
            return {'labels': [], 'values': []}
    
    def create_dashboard_card_with_value(self, title, value, color):
        """Create a dashboard card widget with animated circular progress"""
        card = QtWidgets.QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 15px;
                border: 1px solid rgb(200, 200, 200);
            }}
        """)
        card.setMinimumHeight(180)
        card.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        
        card_layout = QtWidgets.QVBoxLayout(card)
        card_layout.setContentsMargins(10, 10, 10, 10)
        card_layout.setSpacing(5)
        
        # Handle color input - can be QColor or string
        if isinstance(color, str):
            # Parse RGB string like "rgb(34, 139, 34)"
            color_obj = QtGui.QColor()
            color_obj.setNamedColor(color)
        else:
            color_obj = color
        
        # Create two-tone gradient for visual appeal
        color1 = color_obj
        color2 = color_obj.lighter(120)
        
        # Handle special status types for distinct gradient colors
        title_upper = title.upper()
        if "PENDING" in title_upper:
            color1 = QtGui.QColor(255, 165, 0)    # Orange
            color2 = QtGui.QColor(255, 220, 100)  # Light orange
        elif "COMPLETED" in title_upper:
            color1 = QtGui.QColor(50, 205, 100)   # Green
            color2 = QtGui.QColor(100, 255, 150)  # Light green
        elif "CANCELLED" in title_upper:
            color1 = QtGui.QColor(169, 169, 169)  # Gray
            color2 = QtGui.QColor(220, 220, 220)  # Light gray
        elif "REJECTED" in title_upper:
            color1 = QtGui.QColor(255, 80, 80)    # Red
            color2 = QtGui.QColor(255, 150, 100)  # Light red
        elif "ID" in title_upper and "INDIGENCY" not in title_upper:
            color1 = QtGui.QColor(255, 100, 150)  # Pink
            color2 = QtGui.QColor(100, 100, 255)  # Blue
        elif "PERMIT" in title_upper or "BUSINESS" in title_upper:
            color1 = QtGui.QColor(255, 165, 0)    # Orange
            color2 = QtGui.QColor(255, 220, 100)  # Yellow
        elif "INDIGENCY" in title_upper:
            color1 = QtGui.QColor(0, 200, 255)    # Cyan
            color2 = QtGui.QColor(100, 255, 200)  # Mint
        elif "CLEARANCE" in title_upper:
            color1 = QtGui.QColor(150, 100, 255)  # Purple
            color2 = QtGui.QColor(255, 100, 200)  # Pink
        
        # Calculate max value for progress (use 20 as reasonable max for demo)
        max_value = 20
        
        # Create animated circle progress
        circle_progress = AnimatedCircleProgress(
            value=value,
            max_value=max_value,
            title=title,
            color1=color1,
            color2=color2
        )
        circle_progress.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        
        card_layout.addWidget(circle_progress)
        
        return card
    
    def create_dashboard_card(self, title, color):
        """Create a dashboard card widget"""
        card = QtWidgets.QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: rgb(240, 240, 240);
                border-radius: 15px;
                border: 1px solid rgb(200, 200, 200);
            }}
        """)
        card.setMinimumHeight(100)
        card.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        
        card_layout = QtWidgets.QVBoxLayout(card)
        card_layout.setContentsMargins(10, 10, 10, 10)
        card_layout.setSpacing(5)
        
        # Title label
        title_label = QtWidgets.QLabel(title)
        title_label.setStyleSheet(f"""
            QLabel {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 rgb(30, 100, 200), stop:1 rgb(80, 150, 230));
                color: white;
                font-size: 10pt;
                font-weight: bold;
                padding: 8px 15px;
                border-radius: 15px;
            }}
        """)
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        card_layout.addWidget(title_label)
        
        # Value area (empty box for now)
        value_frame = QtWidgets.QFrame()
        value_frame.setStyleSheet("""
            QFrame {
                background-color: rgb(250, 250, 250);
                border-radius: 10px;
                border: 1px solid rgb(220, 220, 220);
            }
        """)
        value_frame.setMinimumHeight(50)
        card_layout.addWidget(value_frame, stretch=1)
        
        return card
    
    def show_services_page(self):
        """Load and display services page"""
        try:

            # Load services_page1.ui
            services_ui_path = Path(__file__).resolve().parent.parent / "ui" / "services_page1.ui"
            
            if not services_ui_path.exists():
                self.notification.show_error(f"❌ Services UI file not found: {services_ui_path}")
                return
            
            # services_page1.ui is a QMainWindow, so we need to load it as such
            temp_window = QtWidgets.QMainWindow()
            uic.loadUi(str(services_ui_path), temp_window)
            
            # Extract the central widget from the QMainWindow
            services_widget = temp_window.centralWidget()
            
            if not services_widget:
                self.notification.show_error("❌ No central widget found in services UI")
                return
            
            # Find and fix the image labels to have reasonable sizes that fit the window
            label_4 = services_widget.findChild(QtWidgets.QLabel, "label_4")
            label_3 = services_widget.findChild(QtWidgets.QLabel, "label_3")
            
            if label_4:
                label_4.setMinimumSize(200, 200)  # Small minimum
                label_4.setMaximumSize(16777215, 16777215)  # No max limit
                label_4.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
                label_4.setScaledContents(True)  # Scale image to fit
            
            if label_3:
                label_3.setMinimumSize(200, 200)  # Small minimum
                label_3.setMaximumSize(16777215, 16777215)  # No max limit
                label_3.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
                label_3.setScaledContents(True)  # Scale image to fit
            
            # Also fix widget_2 (the container for the images)
            widget_2 = services_widget.findChild(QtWidgets.QWidget, "widget_2")
            if widget_2:
                widget_2.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            
            # Wrap services_widget in a scroll area so content is accessible at any size
            scroll_area = QtWidgets.QScrollArea()
            scroll_area.setWidget(services_widget)
            scroll_area.setWidgetResizable(True)  # Make content resize with scroll area
            scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)
            scroll_area.setStyleSheet("""
                QScrollArea {
                    background-color: white;
                    border: none;
                }
            """)
            
            services_widget.setStyleSheet("""
                QWidget {
                    background-color: white;
                }
            """)
            
            # CONNECT THE REQUEST BUTTON
            request_button = services_widget.findChild(QtWidgets.QPushButton, "pushButton")
            if request_button:
                # Disconnect any existing connections
                try:
                    request_button.clicked.disconnect()
                except:
                    pass
                
                # Connect to load services_p2
                request_button.clicked.connect(self.show_services_p2)

            else:
                pass

            # Load services into the widget (if there are service buttons/cards)
            self.load_services_content(services_widget)
            
            # Replace content in the stacked widget - use scroll_area for scrollable content
            self.replace_content(scroll_area)
            
            self.notification.show_success("🛎️ Services page loaded")

        except Exception as e:
            self.notification.show_error(f"❌ Error loading services: {e}")

            import traceback
            traceback.print_exc()
    
    def show_services_p2(self):
        """Show services_p2.ui as a centered popup dialog"""
        try:
            
            # Load services_p2.ui
            services_p2_path = Path(__file__).resolve().parent.parent / "ui" / "services_p2.ui"
            
            if not services_p2_path.exists():
                self.notification.show_error(f"❌ Services P2 UI file not found")
                return
            
            # Create QDialog for popup
            dialog = QtWidgets.QDialog(self)
            dialog.setWindowTitle("Select Certificate Type")
            
            # Remove window frame for modern look, keep close button
            dialog.setWindowFlags(
                QtCore.Qt.Dialog | 
                QtCore.Qt.WindowCloseButtonHint |
                QtCore.Qt.WindowTitleHint
            )
            
            # Load the UI into the dialog
            temp_window = QtWidgets.QMainWindow()
            uic.loadUi(str(services_p2_path), temp_window)
            
            # Extract the central widget
            services_p2_widget = temp_window.centralWidget()
            
            if not services_p2_widget:
                self.notification.show_error("❌ No central widget found in services_p2 UI")
                return
            
            # Set dialog layout to hold the widget
            layout = QtWidgets.QVBoxLayout(dialog)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(services_p2_widget)
            
            # Set fixed size for the popup - adjusted for spaced buttons
            dialog.setFixedSize(560, 340)
            
            # STYLE THE BUTTONS WITH BLUE COLOR AND DARK BLUE BORDER
            button_style = """
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    font-size: 9pt;
                    font-weight: bold;
                    border: 3px solid #1a5490;
                    border-radius: 10px;
                    padding: 12px;
                    text-align: center;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                    border: 3px solid #0d3a6b;
                }
                QPushButton:pressed {
                    background-color: #1c5985;
                    border: 3px solid #0a2847;
                }
                QPushButton:checked {
                    background-color: #27ae60;
                    color: white;
                    border: 3px solid #1e7e34;
                }
            """
            
            # Find and style all 4 buttons
            indigency_btn = services_p2_widget.findChild(QtWidgets.QPushButton, "pushButton")
            clearance_btn = services_p2_widget.findChild(QtWidgets.QPushButton, "pushButton_2")
            id_btn = services_p2_widget.findChild(QtWidgets.QPushButton, "pushButton_3")
            permit_btn = services_p2_widget.findChild(QtWidgets.QPushButton, "pushButton_4")
            
            # ADD SPACING by adjusting button positions and sizes
            # Layout: 2x2 grid with spacing
            button_width = 240
            button_height = 95
            spacing_h = 20  # horizontal spacing
            spacing_v = 15  # vertical spacing
            start_x = 30
            start_y = 90
            
            if indigency_btn:
                # Top-left
                indigency_btn.setGeometry(start_x, start_y, button_width, button_height)
            if clearance_btn:
                # Top-right
                clearance_btn.setGeometry(start_x + button_width + spacing_h, start_y, button_width, button_height)
            if id_btn:
                # Bottom-left
                id_btn.setGeometry(start_x, start_y + button_height + spacing_v, button_width, button_height)
            if permit_btn:
                # Bottom-right
                permit_btn.setGeometry(start_x + button_width + spacing_h, start_y + button_height + spacing_v, button_width, button_height)
            
            # Apply blue styling to all buttons
            for btn in [indigency_btn, clearance_btn, id_btn, permit_btn]:
                if btn:
                    btn.setStyleSheet(button_style)
                    btn.setCursor(QtCore.Qt.PointingHandCursor)
            
            # Connect buttons
            if indigency_btn:
                indigency_btn.clicked.connect(lambda: self.handle_certificate_request("Barangay Indigency", dialog))

            if clearance_btn:
                clearance_btn.clicked.connect(lambda: self.handle_certificate_request("Barangay Clearance", dialog))

            if id_btn:
                id_btn.clicked.connect(lambda: self.handle_certificate_request("Barangay ID", dialog))

            if permit_btn:
                permit_btn.clicked.connect(lambda: self.handle_certificate_request("Business Permit", dialog))

            # Center the dialog on screen
            dialog.move(
                self.geometry().center() - dialog.rect().center()
            )
            
            # Show as modal dialog (blocks interaction with parent)
            dialog.exec_()

        except Exception as e:
            self.notification.show_error(f"❌ Error loading services P2: {e}")

            import traceback
            traceback.print_exc()
    
    def handle_certificate_request(self, certificate_type, dialog):
        """Handle certificate request and load appropriate form"""

        # Close the popup
        dialog.accept()
        
        # Map certificate types to UI files
        ui_mapping = {
            "Barangay Indigency": "services_user_indigency.ui",
            "Barangay Clearance": "services_user_clearance.ui",
            "Barangay ID": "services_user_id.ui",
            "Business Permit": "services_user_business.ui"
        }
        
        ui_file = ui_mapping.get(certificate_type)
        
        if not ui_file:
            self.notification.show_error(f"❌ Unknown certificate type: {certificate_type}")
            return
        
        # Load the certificate request form
        self.load_certificate_form(certificate_type, ui_file)
    
    def load_certificate_form(self, certificate_type, ui_filename):
        """Load and display certificate request form as floating dialog"""
        try:

            # Path to the UI file
            form_ui_path = Path(__file__).resolve().parent.parent / "ui" / ui_filename
            
            if not form_ui_path.exists():
                self.notification.show_error(f"❌ Form UI not found: {ui_filename}")

                return
            
            # Read and fix UI file content (fix Qt enum syntax issues)
            with open(form_ui_path, 'r', encoding='utf-8') as f:
                ui_content = f.read()
            
            # Fix Qt6-style enum syntax to PyQt5 syntax
            ui_content = ui_content.replace('QFrame::Shape::', 'QFrame::')
            ui_content = ui_content.replace('Qt::AlignmentFlag::', 'Qt::')
            
            # Create temporary file with fixed content
            import tempfile
            temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.ui', delete=False, encoding='utf-8')
            temp_file.write(ui_content)
            temp_file.close()
            temp_ui_path = temp_file.name
            
            try:
                # Create QDialog for floating popup
                dialog = QtWidgets.QDialog(self)
                dialog.setWindowTitle(f"{certificate_type} Request Form")
                dialog.setWindowFlags(
                    QtCore.Qt.Dialog | 
                    QtCore.Qt.WindowCloseButtonHint |
                    QtCore.Qt.WindowTitleHint
                )
                
                # Set the beautiful cyan/turquoise background color from original design
                dialog.setStyleSheet("""
                    QDialog {
                        background-color: rgb(164, 234, 255);
                    }
                """)
                
                # Load the QMainWindow UI
                temp_window = QtWidgets.QMainWindow()
                uic.loadUi(temp_ui_path, temp_window)
                
                # Get the central widget
                form_widget = temp_window.centralWidget()
                
                if not form_widget:
                    self.notification.show_error("❌ No central widget found in form")
                    return
                
                # Reparent to prevent destruction
                form_widget.setParent(None)
                
                # SCALE THE FORM to fill the bigger dialog space
                # Apply scaling transformation to make all elements bigger
                from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsProxyWidget
                
                # Create graphics scene and view for scaling
                scene = QGraphicsScene()
                proxy = QGraphicsProxyWidget()
                proxy.setWidget(form_widget)
                scene.addItem(proxy)
                
                # Scale the form content by 1.4x to fill the space
                proxy.setScale(1.4)
                
                # Create graphics view to hold the scaled content
                graphics_view = QGraphicsView(scene)
                graphics_view.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
                graphics_view.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
                graphics_view.setStyleSheet("background-color: rgb(164, 234, 255); border: none;")
                graphics_view.setFrameShape(QtWidgets.QFrame.NoFrame)
                
                # IMPORTANT: Ensure the widget keeps its original background color from UI file
                # Don't override the stylesheet - let it use the original design
                
                # Create main layout for dialog
                main_layout = QtWidgets.QVBoxLayout(dialog)
                main_layout.setContentsMargins(10, 10, 10, 10)
                main_layout.setSpacing(8)
                
                # Add BACK button at the TOP LEFT
                back_button = QtWidgets.QPushButton("⬅ BACK")
                back_button.setMaximumWidth(120)
                back_button.setMinimumHeight(35)
                back_button.setStyleSheet("""
                    QPushButton {
                        background-color: #5DADE2;
                        color: white;
                        font-size: 10pt;
                        font-weight: bold;
                        border: none;
                        border-radius: 5px;
                        padding: 8px 15px;
                        text-align: left;
                    }
                    QPushButton:hover {
                        background-color: #3498DB;
                    }
                    QPushButton:pressed {
                        background-color: #2E86C1;
                    }
                """)
                back_button.setCursor(QtCore.Qt.PointingHandCursor)
                
                # When BACK is clicked, close this dialog and show services_p2 again
                back_button.clicked.connect(lambda: self.handle_back_to_selection(dialog))
                
                # Create a horizontal layout for the back button (top left alignment)
                top_layout = QtWidgets.QHBoxLayout()
                top_layout.addWidget(back_button)
                top_layout.addStretch()  # Push button to the left
                
                main_layout.addLayout(top_layout)
                
                # Add the scaled graphics view (which contains the form)
                main_layout.addWidget(graphics_view)
                
                # Set dialog size - MUCH BIGGER for better visibility
                dialog.setFixedSize(750, 850)
                
                # Connect form buttons (they're inside the proxy widget)
                self.connect_form_buttons(form_widget, certificate_type, dialog)
                
                # PROPERLY CENTER DIALOG ON SCREEN
                # Get screen geometry
                screen = QtWidgets.QApplication.desktop().screenGeometry()
                # Calculate center position
                x = (screen.width() - dialog.width()) // 2
                y = (screen.height() - dialog.height()) // 2
                # Move dialog to center
                dialog.move(x, y)

            finally:
                # Clean up temporary file
                import os
                try:
                    os.unlink(temp_ui_path)
                except:
                    pass
            
            # Show as modal dialog (floating window)
            result = dialog.exec_()
            
            if result == QtWidgets.QDialog.Accepted:
                pass
            elif result == QtWidgets.QDialog.Rejected:
                # User clicked BACK - show certificate selection again
                self.show_services_p2()
            
        except Exception as e:
            self.notification.show_error(f"❌ Error loading form: {e}")
            import traceback
            traceback.print_exc()
    
    def handle_back_to_selection(self, dialog):
        """Handle BACK button - close dialog and return code for showing selection"""

        dialog.reject()  # This will trigger the show_services_p2() call
    
    def connect_form_buttons(self, form_widget, certificate_type, dialog=None):
        """Connect buttons in the certificate form"""
        try:
            # Find SUBMIT button (pushButton)
            submit_btn = form_widget.findChild(QtWidgets.QPushButton, "pushButton")
            if submit_btn:
                # Disconnect existing connections
                try:
                    submit_btn.clicked.disconnect()
                except:
                    pass
                submit_btn.clicked.connect(lambda: self.submit_certificate_request(certificate_type, form_widget, dialog))

            # Find UPLOAD button at TOP (pushButton_2) - for 2x2 photo
            upload_btn = form_widget.findChild(QtWidgets.QPushButton, "pushButton_2")
            if upload_btn:
                try:
                    upload_btn.clicked.disconnect()
                except:
                    pass
                # This uploads to label_14 (photo label at top)
                upload_btn.clicked.connect(lambda: self.upload_photo(form_widget))
            
            # Find UPLOAD button at BOTTOM (pushButton_3) - for Valid ID
            upload_btn_3 = form_widget.findChild(QtWidgets.QPushButton, "pushButton_3")
            if upload_btn_3:
                try:
                    upload_btn_3.clicked.disconnect()
                except:
                    pass
                # This uploads to label_12 (Valid ID label at bottom)
                upload_btn_3.clicked.connect(lambda: self.upload_valid_id(form_widget))
                
        except Exception as e:
            pass

    def upload_photo(self, form_widget):
        """Handle photo/valid ID upload"""
        try:
            # Open file dialog
            file_dialog = QtWidgets.QFileDialog()
            file_path, _ = file_dialog.getOpenFileName(
                self,
                "Select Photo or Valid ID",
                "",
                "Image Files (*.png *.jpg *.jpeg);;All Files (*)"
            )
            
            if file_path:
                # Try to find the photo label - different forms use different labels
                # Try label_14 first (ID form), then label_12 (Clearance form)
                img_label = form_widget.findChild(QtWidgets.QLabel, "label_14")
                if not img_label:
                    img_label = form_widget.findChild(QtWidgets.QLabel, "label_12")
                
                if img_label:
                    # Load and display image
                    pixmap = QtGui.QPixmap(file_path)
                    if not pixmap.isNull():
                        # Scale to fit the label
                        label_size = img_label.size()
                        scaled_pixmap = pixmap.scaled(
                            label_size.width(), label_size.height(),
                            QtCore.Qt.KeepAspectRatio,
                            QtCore.Qt.SmoothTransformation
                        )
                        img_label.setPixmap(scaled_pixmap)
                        img_label.setText("")
                        
                        # Store file path
                        form_widget.uploaded_photo_path = file_path
                        
                        self.notification.show_success("✅ Photo uploaded!")

                    else:
                        self.notification.show_error("❌ Failed to load photo")
                else:
                    self.notification.show_warning("⚠️ Photo label not found")
        except Exception as e:
            self.notification.show_error(f"❌ Upload error: {e}")

    def upload_valid_id(self, form_widget):
        """Handle Valid ID upload (bottom upload button)"""
        try:
            # Open file dialog
            file_dialog = QtWidgets.QFileDialog()
            file_path, _ = file_dialog.getOpenFileName(
                self,
                "Select Valid ID",
                "",
                "Image Files (*.png *.jpg *.jpeg *.pdf);;All Files (*)"
            )
            
            if file_path:
                # Find the Valid ID label (label_12) at bottom
                img_label = form_widget.findChild(QtWidgets.QLabel, "label_12")
                if img_label:
                    # Load and display image
                    pixmap = QtGui.QPixmap(file_path)
                    if not pixmap.isNull():
                        scaled_pixmap = pixmap.scaled(
                            200, 120,
                            QtCore.Qt.KeepAspectRatio,
                            QtCore.Qt.SmoothTransformation
                        )
                        img_label.setPixmap(scaled_pixmap)
                        img_label.setText("")
                        
                        # Store file path
                        form_widget.uploaded_valid_id_path = file_path
                        
                        self.notification.show_success("✅ Valid ID uploaded!")

                    else:
                        self.notification.show_error("❌ Failed to load Valid ID")
                else:
                    self.notification.show_warning("⚠️ Valid ID label not found")
        except Exception as e:
            self.notification.show_error(f"❌ Upload error: {e}")

    def submit_certificate_request(self, certificate_type, form_widget, dialog=None):
        """Handle certificate request submission"""

        try:
            # Import the model
            from app.models import CertificateRequest
            from datetime import datetime
            
            # Collect form data from input fields
            form_data = {}
            
            # Get all QLineEdit fields
            for line_edit in form_widget.findChildren(QtWidgets.QLineEdit):
                field_name = line_edit.objectName()
                field_value = line_edit.text().strip()
                form_data[field_name] = field_value

            # Get all QComboBox fields
            combo_data = {}
            for combo_box in form_widget.findChildren(QtWidgets.QComboBox):
                field_name = combo_box.objectName()
                field_value = combo_box.currentText()
                combo_data[field_name] = field_value

            # Smart field extraction based on actual UI forms
            # Barangay Clearance & Business Permit forms have:
            # - lineEdit = FULL NAME (single field)
            # - lineEdit_5 = PHONE NUMBER
            # - lineEdit_6 = QUANTITY (but we handle this via combo box)
            
            # Get the full name from lineEdit
            full_name = form_data.get('lineEdit', '').strip()
            
            # Split full name into parts (e.g., "John Kester A. Benitez" → first, middle, last)
            name_parts = full_name.split() if full_name else []
            
            if len(name_parts) >= 3:
                # Has first, middle, last (possibly with suffix)
                first_name = name_parts[0]
                last_name = name_parts[-1]
                # Everything in between is middle name
                middle_name = ' '.join(name_parts[1:-1])
            elif len(name_parts) == 2:
                # Just first and last
                first_name = name_parts[0]
                last_name = name_parts[1]
                middle_name = ''
            elif len(name_parts) == 1:
                # Only one name provided
                first_name = name_parts[0]
                last_name = ''
                middle_name = ''
            else:
                first_name = ''
                last_name = ''
                middle_name = ''
            
            suffix = ''  # Forms don't have a separate suffix field
            phone_number = form_data.get('lineEdit_5', '')  # Phone number field
            
            # For combo boxes, identify by content
            purpose = ''
            quantity = 1
            
            for key, value in combo_data.items():
                # If value is a number, it's likely quantity
                if value.isdigit():
                    quantity = int(value)
                # If value is "Select" or empty, skip
                elif value.lower() == 'select' or not value:
                    continue
                # Otherwise it's probably purpose
                else:
                    purpose = value

            # VALIDATION: Check if required fields are filled
            if not first_name and not last_name:
                self.notification.show_error("❌ Please enter your name!")

                return
            
            if not purpose or purpose.lower() == 'select':
                self.notification.show_error("❌ Please select a purpose!")

                return
            
            # Create database session
            db = SessionLocal()
            
            try:
                # Get the current user's resident_id
                if not self.username:
                    self.notification.show_error("❌ User not logged in")
                    return
                
                # Get resident_id from account
                from app.models import Account
                account = db.query(Account).filter(Account.username == self.username).first()
                if not account or not account.resident_id:
                    self.notification.show_error("❌ User account not found")
                    return
                
                # Create new certificate request
                new_request = CertificateRequest(
                    resident_id=account.resident_id,
                    certificate_type=certificate_type,
                    last_name=last_name,
                    first_name=first_name,
                    middle_name=middle_name,
                    suffix=suffix,
                    phone_number=phone_number,
                    purpose=purpose,
                    quantity=quantity,
                    uploaded_file_path=getattr(form_widget, 'uploaded_file_path', None),  # From upload
                    status='Pending',
                    created_at=get_philippine_time()
                )
                
                # Save to database
                db.add(new_request)
                db.commit()

                self.notification.show_success(f"✅ {certificate_type} request submitted successfully!")
                
                # Close the dialog if provided
                if dialog:
                    dialog.accept()
                
            except Exception as e:
                db.rollback()

                self.notification.show_error(f"❌ Failed to save request: {str(e)}")
                import traceback
                traceback.print_exc()
            finally:
                db.close()
                
        except Exception as e:

            self.notification.show_error(f"❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()

    
    def load_services_content(self, widget):
        """Load available services from database"""
        try:
            from app.models import Service
            
            db = SessionLocal()
            services = db.query(Service).all()
            db.close()
            
            
            # TODO: Populate service cards/buttons in the UI
            # This depends on how services_page1.ui is structured
            # You can add service cards dynamically here
            
        except Exception as e:
            pass

    def replace_content(self, new_widget):
        """Replace content in the main content area"""
        try:
            if isinstance(self.content_area, QtWidgets.QStackedWidget):
                # Clear existing pages
                while self.content_area.count() > 0:
                    old_widget = self.content_area.widget(0)
                    self.content_area.removeWidget(old_widget)
                    old_widget.deleteLater()
                
                # Add new widget
                self.content_area.addWidget(new_widget)
                self.content_area.setCurrentWidget(new_widget)

            elif isinstance(self.content_area, QtWidgets.QTabWidget):
                self.content_area.clear()
                self.content_area.addTab(new_widget, "Page")

            else:
                # Replace in layout
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

            # Force visibility
            new_widget.show()
            self.content_area.show()
            self.content_area.update()
            
        except Exception as e:
            pass

    def show_notifications_page(self):
        """Show user notifications from database"""
        try:
            # Import the notification viewer widget
            from gui.widgets.notification_viewer import NotificationViewerWidget
            
            # Create the notification viewer widget
            notifications_widget = NotificationViewerWidget(username=self.username, parent=self)
            
            # Set size policy to expand
            notifications_widget.setSizePolicy(
                QtWidgets.QSizePolicy.Expanding,
                QtWidgets.QSizePolicy.Expanding
            )
            
            # Replace content
            self.replace_content(notifications_widget)
            
            self.notification.show_success("🔔 Notifications loaded!")

        except Exception as e:
            self.notification.show_error(f"❌ Error loading Notifications: {e}")

            import traceback
            traceback.print_exc()
    
    def show_announcement_page(self):
        """Show announcements (user view from database)"""
        try:

            # Import the announcement viewer widget
            from gui.widgets.announcement_viewer import AnnouncementViewerWidget
            
            # Create the announcement viewer widget
            announcement_widget = AnnouncementViewerWidget(parent=self)
            
            # Set size policy to expand
            announcement_widget.setSizePolicy(
                QtWidgets.QSizePolicy.Expanding,
                QtWidgets.QSizePolicy.Expanding
            )
            
            # Replace content
            self.replace_content(announcement_widget)
            
            self.notification.show_success("📢 Announcements loaded!")

        except Exception as e:
            self.notification.show_error(f"❌ Error loading Announcements: {e}")

            import traceback
            traceback.print_exc()
    
    def show_my_request_page(self):
        """Show user's certificate requests (My Requests) - Shopee-style Status Tracker in Table"""
        try:
            # Load the status_user.ui file (with your table design)
            status_ui_path = Path(__file__).resolve().parent.parent / "ui" / "status_user.ui"
            
            if not status_ui_path.exists():
                self.notification.show_error(f"❌ Status UI not found: {status_ui_path}")

                return
            
            # Load the UI with the table/box design
            status_widget = QtWidgets.QWidget()
            uic.loadUi(str(status_ui_path), status_widget)
            
            # Find the scroll area inside the UI
            scroll_area = status_widget.findChild(QtWidgets.QScrollArea, "scrollArea_content")
            
            if scroll_area:
                # Import and create the custom status tracker widget
                from gui.widgets.request_status_tracker import RequestStatusWidget
                
                # Create the status tracker (this will go INSIDE the scroll area)
                tracker_widget = RequestStatusWidget(username=self.username, parent=status_widget)
                
                # Set the tracker as the widget for the scroll area
                scroll_area.setWidget(tracker_widget)

            else:

                # Fallback: use tracker directly if scroll area not found
                from gui.widgets.request_status_tracker import RequestStatusWidget
                status_widget = RequestStatusWidget(username=self.username, parent=self)
            
            # Set size policy to expand
            status_widget.setSizePolicy(
                QtWidgets.QSizePolicy.Expanding,
                QtWidgets.QSizePolicy.Expanding
            )
            
            # Replace content in main window
            self.replace_content(status_widget)
            
            self.notification.show_success("📋 My Requests loaded!")

        except Exception as e:
            self.notification.show_error(f"❌ Error loading My Requests: {e}")

            import traceback
            traceback.print_exc()
    
    def show_payment_page(self):
        """Show payment page"""
        self.notification.show_info("💳 Payment page")

    def show_history_page(self):
        """Show history page"""
        self.notification.show_info("📜 History page")

    def show_blotter_page(self):
        """Show blotter page"""
        try:

            # Path to user_blotter.ui
            blotter_ui_path = Path(__file__).resolve().parent.parent / "ui" / "user_blotter.ui"
            
            if not blotter_ui_path.exists():
                self.notification.show_error(f"❌ Blotter UI not found: {blotter_ui_path}")

                return
            
            # Load the UI
            temp_window = QtWidgets.QMainWindow()
            uic.loadUi(str(blotter_ui_path), temp_window)
            
            # Get central widget
            blotter_widget = temp_window.centralWidget()
            
            if not blotter_widget:
                # If no central widget, load as QWidget directly
                blotter_widget = QtWidgets.QWidget()
                uic.loadUi(str(blotter_ui_path), blotter_widget)
            else:
                # Reparent to prevent destruction
                blotter_widget.setParent(None)
            
            # Set size policy to expand
            blotter_widget.setSizePolicy(
                QtWidgets.QSizePolicy.Expanding,
                QtWidgets.QSizePolicy.Expanding
            )
            
            # Add light blue background (same as other pages)
            blotter_widget.setStyleSheet("""
                QWidget {
                    background-color: #BBDEFB;  /* Light blue */
                }
            """)
            
            # Replace content
            self.replace_content(blotter_widget)
            
            self.notification.show_success("🚨 Blotter loaded!")

        except Exception as e:
            self.notification.show_error(f"❌ Error loading Blotter: {e}")

            import traceback
            traceback.print_exc()
    
    def show_officials_page(self):
        """Show officials page - view only (same data as admin)"""
        try:
            from app.models import BarangayOfficial
            from app.db import SessionLocal
            
            # Create main container with scroll area for responsiveness
            main_widget = QtWidgets.QWidget()
            main_layout = QtWidgets.QVBoxLayout(main_widget)
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.setSpacing(0)
            
            # Blue header with title
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
                    no_data_label = QtWidgets.QLabel("No officials data yet.\nPlease contact the admin to add barangay officials.")
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
                        captain_card = self.create_official_card(captain.position, captain.full_name, captain.photo_path, is_captain=True)
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
                            card = self.create_official_card(official.position, official.full_name, official.photo_path)
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
                            card = self.create_official_card(official.position, official.full_name, official.photo_path)
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
    
    def create_official_card(self, position, name, photo_path=None, is_captain=False):
        """Create a card for an official"""
        import os
        
        card = QtWidgets.QFrame()
        card_width = 160 if is_captain else 130
        card_height = 160 if is_captain else 135
        card.setFixedSize(card_width, card_height)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {'#f8f9fa' if is_captain else '#fafafa'};
                border: {'3px' if is_captain else '2px'} solid #1e3c72;
                border-radius: 10px;
            }}
        """)
        
        card_layout = QtWidgets.QVBoxLayout(card)
        card_layout.setContentsMargins(0, 5, 0, 0)
        card_layout.setSpacing(0)
        
        # Photo
        photo_size = 80 if is_captain else 60
        photo_label = QtWidgets.QLabel()
        photo_label.setFixedSize(photo_size, photo_size)
        photo_label.setAlignment(QtCore.Qt.AlignCenter)
        photo_label.setStyleSheet(f"""
            QLabel {{
                background-color: #e8e8e8;
                border: 2px solid #1e3c72;
                border-radius: {photo_size // 2}px;
                font-size: {'24pt' if is_captain else '18pt'};
                color: #1e3c72;
            }}
        """)
        
        # Load photo if exists
        if photo_path and os.path.exists(photo_path):
            pixmap = QtGui.QPixmap(photo_path)
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
        
        card_layout.addStretch()
        
        # Position and name label
        info_label = QtWidgets.QLabel()
        info_label.setAlignment(QtCore.Qt.AlignCenter)
        info_label.setWordWrap(True)
        info_label.setFixedHeight(50 if is_captain else 45)
        font_size = "8pt" if is_captain else "7pt"
        info_label.setText(f"""
            <p style="margin:0; font-weight:bold; font-size:{font_size}; color:white;">{position}</p>
            <p style="margin:0; font-size:6pt; color:#e0e0e0;">{name}</p>
        """)
        info_label.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1e3c72, stop:1 #2a5298);
                border-bottom-left-radius: 8px; border-bottom-right-radius: 8px; padding: 5px 3px;
            }
        """)
        card_layout.addWidget(info_label)
        
        return card

    def show_allabout_page(self):
        """Show all about page"""
        try:
            # Use the fixed All About UI (clean file)
            about_ui_path = Path(__file__).resolve().parent.parent / "ui" / "ALL_ABOUT_user_fixed.ui"

            if not about_ui_path.exists():
                self.notification.show_error(f"❌ All About UI file not found: {about_ui_path}")
                return

            # Load the UI (designer saved as QMainWindow)
            temp_window = QtWidgets.QMainWindow()
            uic.loadUi(str(about_ui_path), temp_window)

            about_widget = temp_window.centralWidget()
            if not about_widget:
                self.notification.show_error("❌ No central widget found in All About UI")
                return

            # Detach from temp window
            about_widget.setParent(None)
            about_widget.setStyleSheet("background-color: white;")
            
            # Set expanding size policy to grow with window; keep sensible minimums
            about_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            about_widget.setMinimumSize(1024, 1366)

            # Add subtle fade-in animation for branding polish
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
            scroll_area.setWidgetResizable(True)  # Allow widget to expand with scroll area
            scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)
            scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
            scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
            scroll_area.setContentsMargins(0, 0, 0, 0)
            scroll_area.setViewportMargins(0, 0, 0, 0)
            scroll_area.setStyleSheet("QScrollArea { background-color: white; border: none; margin: 0px; padding: 0px; }")

            # Ensure all sections stretch with the viewport and shrink without clipping
            def resize_allabout(event):
                viewport_width = scroll_area.viewport().width()
                margin = 20  # consistent side margin
                body_width = max(800, viewport_width - 2 * margin)

                about_widget.setMinimumWidth(body_width)
                about_widget.resize(body_width, about_widget.height())

                # Hero background and overlay title
                bg_label = about_widget.findChild(QtWidgets.QLabel, "label_6")
                hero_label = about_widget.findChild(QtWidgets.QLabel, "label")
                if bg_label:
                    bg_label.setGeometry(0, bg_label.y(), body_width, bg_label.height())
                    bg_label.setScaledContents(True)
                if hero_label:
                    hero_label.setGeometry(0, hero_label.y(), body_width, hero_label.height())
                    hero_label.setAlignment(QtCore.Qt.AlignCenter)

                # Sections: headings and boxes
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
            self.notification.show_info("ℹ️ All About page")

        except Exception as e:
            self.notification.show_error(f"❌ Error loading All About page: {e}")
            import traceback
            traceback.print_exc()

    def handle_logout(self):
        """Handle logout"""
        reply = QtWidgets.QMessageBox.question(
            self,
            "Logout",
            "Are you sure you want to logout?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:

            self.notification.show_info("👋 Logging out...")
            
            # Close this window and return to login
            QtCore.QTimer.singleShot(1000, self.open_login)
    
    def open_login(self):
        """Return to login window"""
        try:
            # Save current window state before closing
            save_window_state(self)
            
            from gui.views.login_view import LoginWindow
            self.login_window = LoginWindow()
            apply_window_state(self.login_window)
            self.close()
        except Exception as e:
            pass

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = SidebarHomeUserWindow()
    window.showMaximized()
    sys.exit(app.exec_())
