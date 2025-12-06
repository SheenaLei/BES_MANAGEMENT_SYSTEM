"""
Announcement Viewer Widget - Displays announcements for users (read-only)
"""
from PyQt5 import QtWidgets, QtCore, QtGui
from pathlib import Path
from app.db import SessionLocal
from app.models import Announcement


class AnnouncementViewerWidget(QtWidgets.QWidget):
    """Widget for viewing announcements (user view - no edit/delete buttons)"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.load_announcements()
    
    def init_ui(self):
        """Initialize the UI"""
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Blue Header with Title (same as admin, but no add button)
        header = QtWidgets.QLabel()
        header.setMinimumHeight(81)
        header.setMaximumHeight(81)
        header.setStyleSheet("""
            QLabel {
                background: qlineargradient(
                    spread:pad,
                    x1:0, y1:0,
                    x2:0, y2:1,
                    stop:0 #0d47a1,
                    stop:1 #1976d2
                );
                color: white;
                font-weight: bold;
                padding: 15px;
            }
        """)
        header.setText("""
            <html>
                <head/>
                <body>
                    <p><span style="font-size:18pt;">ANNOUNCEMENTS</span></p>
                    <p><span style="font-size:11pt; font-weight:400;">Official Barangay Notices and Updates</span><br/></p>
                </body>
            </html>
        """)
        main_layout.addWidget(header)
        
        # Content container
        content_widget = QtWidgets.QWidget()
        content_layout = QtWidgets.QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)
        
        # Scroll Area for announcements
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        # Container for announcement cards
        self.announcements_container = QtWidgets.QWidget()
        self.announcements_layout = QtWidgets.QGridLayout(self.announcements_container)
        self.announcements_layout.setSpacing(20)
        self.announcements_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll_area.setWidget(self.announcements_container)
        content_layout.addWidget(scroll_area)
        
        # Add content widget to main layout
        main_layout.addWidget(content_widget)
        
        self.setStyleSheet("""
            AnnouncementViewerWidget {
                background-color: transparent;
            }
        """)
    
    def load_announcements(self):
        """Load announcements from database"""
        # Clear existing widgets
        while self.announcements_layout.count():
            item = self.announcements_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Fetch from database
        db = SessionLocal()
        try:
            announcements = db.query(Announcement).filter(
                Announcement.visible == True
            ).order_by(Announcement.posted_at.desc()).all()
            
            if not announcements:
                # Show "no announcements" message
                no_data_label = QtWidgets.QLabel("📢 No announcements at this time")
                no_data_label.setAlignment(QtCore.Qt.AlignCenter)
                no_data_label.setStyleSheet("""
                    QLabel {
                        font-size: 14pt;
                        color: #666;
                        padding: 40px;
                    }
                """)
                self.announcements_layout.addWidget(no_data_label, 0, 0, 1, 2)  # Changed from 1, 3 to 1, 2
                return
            
            # Display in grid (2 columns)
            row = 0
            col = 0
            for announcement in announcements:
                card = self.create_announcement_card(announcement)
                self.announcements_layout.addWidget(card, row, col)
                
                col += 1
                if col >= 2:  # Changed from 3 to 2 columns
                    col = 0
                    row += 1
            
            # Add spacer at the end
            self.announcements_layout.setRowStretch(row + 1, 1)
            
        except Exception as e:
            print(f"Error loading announcements: {e}")
            import traceback
            traceback.print_exc()
        finally:
            db.close()
    
    def create_announcement_card(self, announcement):
        """Create a card widget for an announcement"""
        card = QtWidgets.QFrame()
        card.setMinimumSize(200, 150)
        card.setStyleSheet("""
            QFrame {
                background-color: rgb(229, 229, 229);
                border-radius: 10px;
            }
        """)
        
        card_layout = QtWidgets.QVBoxLayout(card)
        card_layout.setSpacing(0)
        card_layout.setContentsMargins(0, 0, 0, 0)
        
        # Header with title (no buttons)
        header = QtWidgets.QLabel(announcement.title or "Untitled")
        header.setMinimumHeight(31)
        header.setMaximumHeight(31)
        header.setAlignment(QtCore.Qt.AlignCenter)
        header.setStyleSheet("""
            QLabel {
                background-color: qlineargradient(spread:pad, x1:0.231, y1:0.310227, x2:1, y2:1, 
                    stop:0 rgba(0, 98, 255, 239), stop:1 rgba(240, 240, 240, 255));
                font-weight: bold;
                color: #000;
                padding: 5px;
            }
        """)
        card_layout.addWidget(header)
        
        # Photo (if exists)
        if hasattr(announcement, 'image_path') and announcement.image_path and Path(announcement.image_path).exists():
            photo_label = QtWidgets.QLabel()
            photo_label.setAlignment(QtCore.Qt.AlignCenter)
            photo_label.setStyleSheet("padding: 10px; background-color: transparent;")
            
            pixmap = QtGui.QPixmap(announcement.image_path)
            if not pixmap.isNull():
                # Scale to fit card width (max 300px width)
                scaled_pixmap = pixmap.scaled(
                    300, 200,
                    QtCore.Qt.KeepAspectRatio,
                    QtCore.Qt.SmoothTransformation
                )
                photo_label.setPixmap(scaled_pixmap)
                card_layout.addWidget(photo_label)
        
        # Content
        content_label = QtWidgets.QLabel(announcement.content or "No content")
        content_label.setWordWrap(True)
        content_label.setStyleSheet("""
            QLabel {
                padding: 10px;
                background-color: transparent;
                color: #333;
            }
        """)
        card_layout.addWidget(content_label)
        
        # Date
        date_label = QtWidgets.QLabel(
            announcement.posted_at.strftime("%b %d, %Y") if announcement.posted_at else ""
        )
        date_label.setStyleSheet("""
            QLabel {
                padding: 5px 10px;
                background-color: transparent;
                color: #666;
                font-size: 9pt;
            }
        """)
        card_layout.addWidget(date_label)
        
        return card
