"""
Announcement Viewer Widget - Displays announcements for users (read-only)
"""
from PyQt5 import QtWidgets, QtCore, QtGui
from pathlib import Path
from app.db import SessionLocal
from app.models import Announcement


class FlowLayout(QtWidgets.QLayout):
    """A flow layout that arranges widgets like text, wrapping to next line when needed"""
    def __init__(self, parent=None, margin=0, spacing=-1):
        super().__init__(parent)
        self.setContentsMargins(margin, margin, margin, margin)
        self.setSpacing(spacing if spacing >= 0 else 20)
        self._items = []

    def addItem(self, item):
        self._items.append(item)

    def count(self):
        return len(self._items)

    def itemAt(self, index):
        if 0 <= index < len(self._items):
            return self._items[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self._items):
            return self._items.pop(index)
        return None

    def expandingDirections(self):
        return QtCore.Qt.Orientations(QtCore.Qt.Orientation(0))

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self._doLayout(QtCore.QRect(0, 0, width, 0), True)

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self._doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QtCore.QSize()
        for item in self._items:
            size = size.expandedTo(item.minimumSize())
        margin = self.contentsMargins()
        size += QtCore.QSize(margin.left() + margin.right(), margin.top() + margin.bottom())
        return size

    def _doLayout(self, rect, testOnly):
        left, top, right, bottom = self.getContentsMargins()
        effectiveRect = rect.adjusted(left, top, -right, -bottom)
        x = effectiveRect.x()
        y = effectiveRect.y()
        lineHeight = 0

        for item in self._items:
            widget = item.widget()
            spaceX = self.spacing()
            spaceY = self.spacing()
            
            nextX = x + item.sizeHint().width() + spaceX
            if nextX - spaceX > effectiveRect.right() and lineHeight > 0:
                x = effectiveRect.x()
                y = y + lineHeight + spaceY
                nextX = x + item.sizeHint().width() + spaceX
                lineHeight = 0

            if not testOnly:
                item.setGeometry(QtCore.QRect(QtCore.QPoint(x, y), item.sizeHint()))

            x = nextX
            lineHeight = max(lineHeight, item.sizeHint().height())

        return y + lineHeight - rect.y() + bottom


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
        
        # Container for announcement cards with Flow Layout
        self.announcements_container = QtWidgets.QWidget()
        self.announcements_layout = FlowLayout(self.announcements_container, margin=0, spacing=15)
        
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
                self.announcements_layout.addWidget(no_data_label)
                return
            
            # Add cards with flow layout (each card has its own natural size)
            for announcement in announcements:
                card = self.create_announcement_card(announcement)
                self.announcements_layout.addWidget(card)
            
        except Exception as e:

            import traceback
            traceback.print_exc()
        finally:
            db.close()
    
    def create_announcement_card(self, announcement):
        """Create a card widget for an announcement"""
        card = QtWidgets.QFrame()
        card.setFixedWidth(280)  # Fixed width, flexible height based on content
        card.setStyleSheet("""
            QFrame {
                background-color: rgb(229, 229, 229);
                border-radius: 10px;
            }
            QFrame:hover {
                background-color: rgb(220, 220, 220);
            }
        """)
        card.setCursor(QtCore.Qt.PointingHandCursor)
        
        # Make card clickable to view full announcement
        card.mousePressEvent = lambda event: self.view_full_announcement(announcement)
        
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
        
        # Image indicator
        if announcement.image_path and Path(announcement.image_path).exists():
            image_indicator = QtWidgets.QLabel("📷 Has Image")
            image_indicator.setStyleSheet("""
                QLabel {
                    padding: 5px 10px;
                    background-color: #e3f2fd;
                    color: #1976d2;
                    font-size: 9pt;
                    border-radius: 5px;
                    margin: 5px 10px;
                }
            """)
        else:
            image_indicator = QtWidgets.QLabel("🚫 No Image")
            image_indicator.setStyleSheet("""
                QLabel {
                    padding: 5px 10px;
                    background-color: #f5f5f5;
                    color: #999;
                    font-size: 9pt;
                    border-radius: 5px;
                    margin: 5px 10px;
                }
            """)
        image_indicator.setAlignment(QtCore.Qt.AlignCenter)
        card_layout.addWidget(image_indicator)
        
        # Content Preview (limited to ~100 characters for 3 lines)
        content_text = announcement.content or "No content"
        preview_text = content_text[:100] + "..." if len(content_text) > 100 else content_text
        content_label = QtWidgets.QLabel(preview_text)
        content_label.setWordWrap(True)
        content_label.setMaximumHeight(60)
        content_label.setStyleSheet("""
            QLabel {
                padding: 10px;
                background-color: transparent;
                color: #333;
            }
        """)
        card_layout.addWidget(content_label)
        
        # Click hint - separate and visible
        click_hint = QtWidgets.QLabel("📖 Click to view full details")
        click_hint.setAlignment(QtCore.Qt.AlignCenter)
        click_hint.setStyleSheet("""
            QLabel {
                padding: 8px;
                background-color: #e3f2fd;
                color: #1976d2;
                font-size: 10pt;
                font-weight: bold;
                border-radius: 5px;
                margin: 5px 10px;
            }
        """)
        card_layout.addWidget(click_hint)
        
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
    
    def view_full_image(self, image_path):
        """View full-size image in a dialog"""
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("View Image")
        dialog.setModal(True)
        
        layout = QtWidgets.QVBoxLayout(dialog)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Scroll area for large images
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        # Image label
        image_label = QtWidgets.QLabel()
        image_label.setAlignment(QtCore.Qt.AlignCenter)
        
        pixmap = QtGui.QPixmap(image_path)
        if not pixmap.isNull():
            # Scale to fit screen while maintaining aspect ratio
            screen = QtWidgets.QApplication.primaryScreen().geometry()
            max_width = int(screen.width() * 0.8)
            max_height = int(screen.height() * 0.8)
            
            scaled_pixmap = pixmap.scaled(
                max_width, max_height,
                QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation
            )
            image_label.setPixmap(scaled_pixmap)
        
        scroll_area.setWidget(image_label)
        layout.addWidget(scroll_area)
        
        # Close button
        close_btn = QtWidgets.QPushButton("Close")
        close_btn.clicked.connect(dialog.close)
        close_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 30px;
                font-size: 11pt;
                background-color: #1976d2;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
        """)
        layout.addWidget(close_btn, alignment=QtCore.Qt.AlignCenter)
        
        dialog.resize(scaled_pixmap.width() + 20, scaled_pixmap.height() + 80)
        dialog.exec_()
    
    def view_full_announcement(self, announcement):
        """View full announcement details in a dialog"""
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Announcement Details")
        dialog.setModal(True)
        
        # Make dialog 80% of screen size for better readability
        screen = QtWidgets.QApplication.primaryScreen().geometry()
        dialog_width = int(screen.width() * 0.7)
        dialog_height = int(screen.height() * 0.8)
        dialog.resize(dialog_width, dialog_height)
        
        layout = QtWidgets.QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QtWidgets.QLabel(announcement.title or "Untitled")
        title_label.setWordWrap(True)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 20pt;
                font-weight: bold;
                color: #1976d2;
                padding: 10px;
            }
        """)
        layout.addWidget(title_label)
        
        # Date
        if announcement.posted_at:
            date_label = QtWidgets.QLabel(
                announcement.posted_at.strftime("Posted on %B %d, %Y at %I:%M %p")
            )
            date_label.setStyleSheet("""
                QLabel {
                    font-size: 11pt;
                    color: #666;
                    padding: 0px 10px;
                }
            """)
            layout.addWidget(date_label)
        
        # Separator
        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.HLine)
        separator.setStyleSheet("background-color: #ccc;")
        layout.addWidget(separator)
        
        # Scroll area for content (vertical scroll only)
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: white;
            }
        """)
        
        content_widget = QtWidgets.QWidget()
        content_layout = QtWidgets.QVBoxLayout(content_widget)
        content_layout.setContentsMargins(10, 10, 10, 10)
        
        # Image (if exists)
        if announcement.image_path and Path(announcement.image_path).exists():
            image_label = QtWidgets.QLabel()
            image_label.setAlignment(QtCore.Qt.AlignCenter)
            image_label.setCursor(QtCore.Qt.PointingHandCursor)
            
            pixmap = QtGui.QPixmap(announcement.image_path)
            if not pixmap.isNull():
                # Scale image to fit dialog width
                max_img_width = dialog_width - 80
                scaled_pixmap = pixmap.scaled(
                    max_img_width, 500,
                    QtCore.Qt.KeepAspectRatio,
                    QtCore.Qt.SmoothTransformation
                )
                image_label.setPixmap(scaled_pixmap)
                image_label.mousePressEvent = lambda event: self.view_full_image(announcement.image_path)
                image_label.setToolTip("Click to view full size")
                content_layout.addWidget(image_label)
        
        # Content - full text display
        content_label = QtWidgets.QLabel(announcement.content or "No content")
        content_label.setWordWrap(True)
        content_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        content_label.setStyleSheet("""
            QLabel {
                font-size: 12pt;
                color: #333;
                padding: 15px;
                background-color: white;
                line-height: 1.5;
            }
        """)
        content_layout.addWidget(content_label)
        
        content_layout.addStretch()
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)
        
        dialog.exec_()
