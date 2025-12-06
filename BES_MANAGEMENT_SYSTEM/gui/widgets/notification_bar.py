from PyQt5 import QtWidgets, QtCore, QtGui

class NotificationBar(QtWidgets.QWidget):
    """
    Universal Notification Bar
    A long rectangular notification that slides down from the top of the window.
    Supports: Success, Error, Warning, Info.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)  # Required for background color to show!
        self.setFixedHeight(60)  # Sleek height
        
        # Shadow effect for depth
        self.shadow = QtWidgets.QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(20)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(5)
        self.shadow.setColor(QtGui.QColor(0, 0, 0, 80))
        self.setGraphicsEffect(self.shadow)
        
        # Layout
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(15)
        
        # Icon Label
        self.icon_label = QtWidgets.QLabel()
        self.icon_label.setFixedSize(30, 30)
        self.icon_label.setAlignment(QtCore.Qt.AlignCenter)
        
        # Message Label
        self.message_label = QtWidgets.QLabel()
        self.message_label.setWordWrap(True)
        
        # Close Button
        self.close_btn = QtWidgets.QPushButton("×")
        self.close_btn.setFixedSize(30, 30)
        self.close_btn.setCursor(QtCore.Qt.PointingHandCursor)
        self.close_btn.clicked.connect(self.hide_notification)
        
        layout.addWidget(self.icon_label)
        layout.addWidget(self.message_label, 1)
        layout.addWidget(self.close_btn)
        
        self.hide()
        
        # Animation setup
        self.animation = QtCore.QPropertyAnimation(self, b"pos")
        self.animation.setDuration(500)
        self.animation.setEasingCurve(QtCore.QEasingCurve.OutCubic)
        
        # Auto-hide timer
        self.hide_timer = QtCore.QTimer()
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.hide_notification)

    def _apply_style(self, theme_color, icon_text):
        """Apply the specific color theme (White background, colored text/border)"""
        # Main Widget Style (White Background)
        self.setStyleSheet(f"""
            QWidget {{
                background-color: #FFFFFF;
                border-bottom-left-radius: 10px;
                border-bottom-right-radius: 10px;
                border: 2px solid {theme_color};
                border-top: none;
            }}
        """)
        
        # Icon Style
        self.icon_label.setText(icon_text)
        self.icon_label.setStyleSheet(f"""
            QLabel {{
                color: {theme_color};
                font-size: 18pt;
                font-weight: bold;
                background: transparent;
                border: none;
            }}
        """)
        
        # Message Style
        self.message_label.setStyleSheet(f"""
            QLabel {{
                color: #333333;
                font-size: 12pt;
                font-family: 'Segoe UI', sans-serif;
                font-weight: 600;
                background: transparent;
                border: none;
            }}
        """)
        
        # Close Button Style
        self.close_btn.setStyleSheet(f"""
            QPushButton {{
                color: #999999;
                background: transparent;
                border: none;
                font-size: 20pt;
                font-weight: bold;
                padding-bottom: 3px;
            }}
            QPushButton:hover {{
                color: {theme_color};
            }}
        """)

    def show_success(self, message, duration=60000):
        """Show Green Success Notification"""
        self._apply_style("#27ae60", "✓")
        self.message_label.setText(message)
        self._show_animated(duration)

    def show_error(self, message, duration=60000):
        """Show Red Error Notification"""
        self._apply_style("#c0392b", "✕")
        self.message_label.setText(message)
        self._show_animated(duration)

    def show_warning(self, message, duration=60000):
        """Show Orange Warning Notification"""
        self._apply_style("#e67e22", "⚠")
        self.message_label.setText(message)
        self._show_animated(duration)

    def show_info(self, message, duration=60000):
        """Show Blue Info Notification"""
        self._apply_style("#2980b9", "ℹ")
        self.message_label.setText(message)
        self._show_animated(duration)

    def _show_animated(self, duration):
        """Handle the slide-down animation and positioning"""
        if not self.parent():
            return

        parent_width = self.parent().width()
        
        # Calculate width: 95% of parent width (Almost full width)
        width = int(parent_width * 0.95)
        self.setFixedWidth(width)
        
        # Center horizontally
        x = (parent_width - width) // 2
        
        # Start position (hidden above top edge)
        start_pos = QtCore.QPoint(x, -self.height())
        # End position (just below top edge)
        end_pos = QtCore.QPoint(x, 10)
        
        self.move(start_pos)
        self.show()
        self.raise_()  # Ensure it's on top of everything
        
        # Animate
        self.animation.setStartValue(start_pos)
        self.animation.setEndValue(end_pos)
        self.animation.start()
        
        # Start auto-hide timer
        self.hide_timer.start(duration)

    def hide_notification(self):
        """Slide up and hide"""
        if not self.parent():
            return
            
        x = self.pos().x()
        start_pos = self.pos()
        end_pos = QtCore.QPoint(x, -self.height() - 10)
        
        self.animation.setStartValue(start_pos)
        self.animation.setEndValue(end_pos)
        self.animation.finished.connect(self.hide)
        self.animation.start()
