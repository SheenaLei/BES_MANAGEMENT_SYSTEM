"""
Notification Viewer Widget
Displays user notifications from the database with visual styling
"""
from PyQt5 import QtWidgets, QtCore, QtGui
from pathlib import Path
from app.db import SessionLocal
from app.models import Notification, Account
from datetime import datetime


class NotificationViewerWidget(QtWidgets.QWidget):
    """Custom widget for displaying user notifications"""
    
    def __init__(self, username=None, parent=None):
        super().__init__(parent)
        self.username = username
        self.notifications = []
        
        self.init_ui()
        self.load_notifications()
    
    def init_ui(self):
        """Initialize the UI components"""
        # Main layout
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Set background
        self.setStyleSheet("""
            NotificationViewerWidget {
                background-color: #BBDEFB;
            }
        """)
        
        # Header
        header_layout = QtWidgets.QHBoxLayout()
        
        title_label = QtWidgets.QLabel("🔔 NOTIFICATIONS")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 20pt;
                font-weight: bold;
                color: #1565c0;
                background: transparent;
            }
        """)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Refresh button
        refresh_btn = QtWidgets.QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.load_notifications)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196f3;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 11pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976d2;
            }
        """)
        header_layout.addWidget(refresh_btn)
        
        # Mark all as read button
        mark_read_btn = QtWidgets.QPushButton("✓ Mark All as Read")
        mark_read_btn.clicked.connect(self.mark_all_as_read)
        mark_read_btn.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 11pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #388e3c;
            }
        """)
        header_layout.addWidget(mark_read_btn)
        
        main_layout.addLayout(header_layout)
        
        # Scroll area for notifications
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
        """)
        
        # Container for notification cards
        self.notifications_container = QtWidgets.QWidget()
        self.notifications_layout = QtWidgets.QVBoxLayout(self.notifications_container)
        self.notifications_layout.setContentsMargins(0, 0, 0, 0)
        self.notifications_layout.setSpacing(10)
        self.notifications_layout.addStretch()
        
        scroll_area.setWidget(self.notifications_container)
        main_layout.addWidget(scroll_area)
    
    def load_notifications(self):
        """Load notifications from database"""
        # Clear existing notifications
        while self.notifications_layout.count() > 1:  # Keep the stretch
            item = self.notifications_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if not self.username:
            self.add_empty_message("Please log in to view notifications.")
            return
        
        db = SessionLocal()
        try:
            # Get user account
            account = db.query(Account).filter(Account.username == self.username).first()
            if not account or not account.resident_id:
                self.add_empty_message("Account not found.")
                return
            
            # Get all notifications for this user
            notifications = db.query(Notification).filter(
                Notification.resident_id == account.resident_id
            ).order_by(Notification.created_at.desc()).all()
            
            if not notifications:
                self.add_empty_message("No notifications yet. 📭")
                return
            
            # Add notification cards
            for notif in notifications:
                card = self.create_notification_card(notif)
                # Insert before the stretch
                self.notifications_layout.insertWidget(self.notifications_layout.count() - 1, card)
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.add_empty_message(f"Error loading notifications: {e}")
        finally:
            db.close()
    
    def add_empty_message(self, message):
        """Add an empty state message"""
        empty_label = QtWidgets.QLabel(message)
        empty_label.setAlignment(QtCore.Qt.AlignCenter)
        empty_label.setStyleSheet("""
            QLabel {
                font-size: 14pt;
                color: #666;
                padding: 50px;
                background: transparent;
            }
        """)
        self.notifications_layout.insertWidget(0, empty_label)
    
    def create_notification_card(self, notification):
        """Create a styled notification card"""
        card = QtWidgets.QFrame()
        card.setObjectName(f"notification_{notification.notification_id}")
        
        # Style based on read status
        if notification.is_read:
            bg_color = "#f5f5f5"
            border_color = "#e0e0e0"
        else:
            bg_color = "#ffffff"
            border_color = "#2196f3"
        
        card.setStyleSheet(f"""
            QFrame#notification_{notification.notification_id} {{
                background-color: {bg_color};
                border: 2px solid {border_color};
                border-radius: 10px;
                padding: 15px;
            }}
        """)
        
        card_layout = QtWidgets.QVBoxLayout(card)
        card_layout.setContentsMargins(15, 15, 15, 15)
        card_layout.setSpacing(8)
        
        # Header row (title + time)
        header_layout = QtWidgets.QHBoxLayout()
        
        # Title with icon
        title_label = QtWidgets.QLabel(notification.title or "Notification")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 13pt;
                font-weight: bold;
                color: #333;
                background: transparent;
            }
        """)
        header_layout.addWidget(title_label)
        
        # Unread indicator
        if not notification.is_read:
            unread_badge = QtWidgets.QLabel("● NEW")
            unread_badge.setStyleSheet("""
                QLabel {
                    color: #f44336;
                    font-size: 9pt;
                    font-weight: bold;
                    background: transparent;
                }
            """)
            header_layout.addWidget(unread_badge)
        
        header_layout.addStretch()
        
        # Time
        time_str = ""
        if notification.created_at:
            time_str = notification.created_at.strftime("%m/%d/%Y %I:%M %p")
        time_label = QtWidgets.QLabel(time_str)
        time_label.setStyleSheet("""
            QLabel {
                font-size: 10pt;
                color: #999;
                background: transparent;
            }
        """)
        header_layout.addWidget(time_label)
        
        card_layout.addLayout(header_layout)
        
        # Message
        message_label = QtWidgets.QLabel(notification.message or "")
        message_label.setWordWrap(True)
        message_label.setStyleSheet("""
            QLabel {
                font-size: 11pt;
                color: #555;
                line-height: 1.4;
                background: transparent;
            }
        """)
        card_layout.addWidget(message_label)
        
        return card
    
    def mark_all_as_read(self):
        """Mark all notifications as read"""
        if not self.username:
            return
        
        db = SessionLocal()
        try:
            account = db.query(Account).filter(Account.username == self.username).first()
            if not account or not account.resident_id:
                return
            
            # Update all unread notifications
            db.query(Notification).filter(
                Notification.resident_id == account.resident_id,
                Notification.is_read == False
            ).update({Notification.is_read: True})
            
            db.commit()

            # Reload to update UI
            self.load_notifications()
            
        except Exception as e:
            pass
        finally:
            db.close()
