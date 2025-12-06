"""
Announcement Manager Widget - Displays announcements with admin controls
"""
from PyQt5 import QtWidgets, QtCore, QtGui
from pathlib import Path
from app.db import SessionLocal
from app.models import Announcement
from app.config import get_philippine_time
from datetime import datetime


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


class AnnouncementManagerWidget(QtWidgets.QWidget):
    """Widget for managing announcements (admin view with edit/delete buttons)"""
    
    def __init__(self, admin_id=None, parent=None):
        super().__init__(parent)
        self.admin_id = admin_id
        self.init_ui()
        self.load_announcements()
    
    def init_ui(self):
        """Initialize the UI"""
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Blue Header with Title
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
        
        # Add New Announcement Button
        add_btn = QtWidgets.QPushButton("+ Add New Announcement")
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #1976d2;
                color: white;
                font-size: 12pt;
                font-weight: bold;
                padding: 15px;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
            QPushButton:pressed {
                background-color: #0d47a1;
            }
        """)
        add_btn.setCursor(QtCore.Qt.PointingHandCursor)
        add_btn.clicked.connect(self.add_announcement)
        content_layout.addWidget(add_btn)
        
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
            AnnouncementManagerWidget {
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
            
            # Add cards with flow layout (no grid, each card has its own size)
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
        card.setFixedWidth(280)  # Fixed width, flexible height
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
        
        # Header with title and action buttons
        header = QtWidgets.QWidget()
        header.setMinimumHeight(31)
        header.setMaximumHeight(31)
        header.setStyleSheet("""
            QWidget {
                background-color: qlineargradient(spread:pad, x1:0.231, y1:0.310227, x2:1, y2:1, 
                    stop:0 rgba(0, 98, 255, 239), stop:1 rgba(240, 240, 240, 255));
                border-radius: 0px;
            }
        """)
        header_layout = QtWidgets.QHBoxLayout(header)
        header_layout.setContentsMargins(10, 5, 10, 5)
        header_layout.setSpacing(5)
        
        # Title label
        title_label = QtWidgets.QLabel(announcement.title or "Untitled")
        title_label.setStyleSheet("""
            QLabel {
                background: transparent;
                font-weight: bold;
                color: #000;
            }
        """)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Edit button (pencil icon in circle)
        edit_btn = QtWidgets.QPushButton()
        edit_btn.setFixedSize(24, 24)
        edit_btn.setIcon(self.create_edit_icon())
        edit_btn.setIconSize(QtCore.QSize(14, 14))
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196f3;
                border: none;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: #1976d2;
            }
            QPushButton:pressed {
                background-color: #0d47a1;
            }
        """)
        edit_btn.setCursor(QtCore.Qt.PointingHandCursor)
        edit_btn.setToolTip("Edit Announcement")
        edit_btn.clicked.connect(lambda: self.edit_announcement(announcement.announcement_id))
        header_layout.addWidget(edit_btn)
        
        # Delete button (trash icon in circle)
        delete_btn = QtWidgets.QPushButton()
        delete_btn.setFixedSize(24, 24)
        delete_btn.setIcon(self.create_delete_icon())
        delete_btn.setIconSize(QtCore.QSize(14, 14))
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                border: none;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
            QPushButton:pressed {
                background-color: #b71c1c;
            }
        """)
        delete_btn.setCursor(QtCore.Qt.PointingHandCursor)
        delete_btn.setToolTip("Delete Announcement")
        delete_btn.clicked.connect(lambda: self.delete_announcement(announcement.announcement_id))
        header_layout.addWidget(delete_btn)
        
        card_layout.addWidget(header)
        
        # Image indicator (show for all cards to keep uniform height)
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
    
    def create_edit_icon(self):
        """Create pencil edit icon"""
        pixmap = QtGui.QPixmap(16, 16)
        pixmap.fill(QtCore.Qt.transparent)
        painter = QtGui.QPainter(pixmap)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        # Draw pencil
        pen = QtGui.QPen(QtGui.QColor(255, 255, 255), 2)
        pen.setCapStyle(QtCore.Qt.RoundCap)
        painter.setPen(pen)
        painter.drawLine(12, 4, 4, 12)
        
        # Pencil tip
        painter.setBrush(QtGui.QBrush(QtGui.QColor(255, 255, 255)))
        painter.setPen(QtCore.Qt.NoPen)
        tip = QtGui.QPolygon([
            QtCore.QPoint(4, 12),
            QtCore.QPoint(2, 14),
            QtCore.QPoint(6, 14)
        ])
        painter.drawPolygon(tip)
        
        painter.end()
        return QtGui.QIcon(pixmap)
    
    def create_delete_icon(self):
        """Create trash/delete icon"""
        pixmap = QtGui.QPixmap(16, 16)
        pixmap.fill(QtCore.Qt.transparent)
        painter = QtGui.QPainter(pixmap)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        # Draw trash can
        painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255), 2))
        # Lid
        painter.drawLine(3, 4, 13, 4)
        # Body
        painter.drawRect(5, 5, 6, 8)
        # Vertical lines in body
        painter.drawLine(7, 6, 7, 12)
        painter.drawLine(9, 6, 9, 12)
        
        painter.end()
        return QtGui.QIcon(pixmap)
    
    def add_announcement(self):
        """Open dialog to add new announcement"""
        dialog = AnnouncementDialog(parent=self)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            title, content, image_path = dialog.get_data()
            
            # Save to database
            db = SessionLocal()
            try:
                new_announcement = Announcement(
                    title=title,
                    content=content,
                    image_path=image_path,
                    posted_by_admin_id=self.admin_id,
                    posted_at=get_philippine_time(),
                    visible=True
                )
                db.add(new_announcement)
                db.commit()
                
                self.load_announcements()  # Refresh display
                
            except Exception as e:
                db.rollback()
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to add announcement: {e}")
            finally:
                db.close()
    
    def edit_announcement(self, announcement_id):
        """Open dialog to edit announcement"""
        db = SessionLocal()
        try:
            announcement = db.query(Announcement).filter(
                Announcement.announcement_id == announcement_id
            ).first()
            
            if not announcement:
                QtWidgets.QMessageBox.warning(self, "Not Found", "Announcement not found!")
                return
            
            dialog = AnnouncementDialog(
                title=announcement.title,
                content=announcement.content,
                image_path=announcement.image_path or "",
                parent=self
            )
            
            if dialog.exec_() == QtWidgets.QDialog.Accepted:
                title, content, image_path = dialog.get_data()
                
                announcement.title = title
                announcement.content = content
                announcement.image_path = image_path
                db.commit()
                
                self.load_announcements()  # Refresh display
                
        except Exception as e:
            db.rollback()
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to edit announcement: {e}")
        finally:
            db.close()
    
    def delete_announcement(self, announcement_id):
        """Delete announcement"""
        reply = QtWidgets.QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this announcement?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            db = SessionLocal()
            try:
                announcement = db.query(Announcement).filter(
                    Announcement.announcement_id == announcement_id
                ).first()
                
                if announcement:
                    announcement.visible = False  # Soft delete
                    db.commit()
                    
                    self.load_announcements()  # Refresh display
                    
            except Exception as e:
                db.rollback()
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to delete announcement: {e}")
            finally:
                db.close()
    
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
        
        # Action buttons row
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        
        # Edit button
        edit_btn = QtWidgets.QPushButton("✏️ Edit")
        edit_btn.clicked.connect(lambda: (dialog.close(), self.edit_announcement(announcement.announcement_id)))
        edit_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                font-size: 11pt;
                background-color: #2196f3;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #1976d2;
            }
        """)
        button_layout.addWidget(edit_btn)
        
        # Delete button
        delete_btn = QtWidgets.QPushButton("🗑️ Delete")
        delete_btn.clicked.connect(lambda: (dialog.close(), self.delete_announcement(announcement.announcement_id)))
        delete_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                font-size: 11pt;
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        button_layout.addWidget(delete_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        dialog.exec_()


class AnnouncementDialog(QtWidgets.QDialog):
    """Dialog for adding/editing announcements"""
    
    def __init__(self, title="", content="", image_path="", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Announcement")
        self.setModal(True)
        self.setMinimumSize(500, 500)
        
        self.image_path = image_path  # Store selected image path
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Title
        layout.addWidget(QtWidgets.QLabel("Title:"))
        self.title_edit = QtWidgets.QLineEdit()
        self.title_edit.setText(title)
        self.title_edit.setStyleSheet("padding: 8px; font-size: 11pt;")
        layout.addWidget(self.title_edit)
        
        # Content
        layout.addWidget(QtWidgets.QLabel("Content:"))
        self.content_edit = QtWidgets.QTextEdit()
        self.content_edit.setText(content)
        self.content_edit.setStyleSheet("padding: 8px; font-size: 11pt;")
        layout.addWidget(self.content_edit)
        
        # Photo Upload Section
        photo_label = QtWidgets.QLabel("Photo (Optional):")
        layout.addWidget(photo_label)
        
        # Photo container
        photo_container = QtWidgets.QWidget()
        photo_layout = QtWidgets.QHBoxLayout(photo_container)
        photo_layout.setContentsMargins(0, 0, 0, 0)
        
        # Upload button
        upload_btn = QtWidgets.QPushButton("📷 Upload Photo")
        upload_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                font-size: 10pt;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        upload_btn.clicked.connect(self.upload_photo)
        photo_layout.addWidget(upload_btn)
        
        # Photo preview label
        self.photo_preview_label = QtWidgets.QLabel("No photo selected")
        self.photo_preview_label.setStyleSheet("""
            QLabel {
                padding: 10px;
                background-color: #f5f5f5;
                border: 1px dashed #ccc;
                border-radius: 5px;
                min-height: 100px;
            }
        """)
        self.photo_preview_label.setAlignment(QtCore.Qt.AlignCenter)
        photo_layout.addWidget(self.photo_preview_label, 1)
        
        layout.addWidget(photo_container)
        
        # Load existing image if provided
        if image_path and Path(image_path).exists():
            self.display_photo(image_path)
        
        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                font-size: 11pt;
                background-color: #ccc;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #bbb;
            }
        """)
        button_layout.addWidget(cancel_btn)
        
        save_btn = QtWidgets.QPushButton("Save")
        save_btn.clicked.connect(self.accept)
        save_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
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
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
    
    def upload_photo(self):
        """Open file dialog to select photo"""
        file_dialog = QtWidgets.QFileDialog(self)
        file_path, _ = file_dialog.getOpenFileName(
            self,
            "Select Photo",
            "",
            "Image Files (*.png *.jpg *.jpeg *.gif *.bmp);;All Files (*)"
        )
        
        if file_path:
            self.image_path = file_path
            self.display_photo(file_path)
    
    def display_photo(self, file_path):
        """Display photo preview"""
        try:
            pixmap = QtGui.QPixmap(file_path)
            if not pixmap.isNull():
                # Scale to fit preview (max 150x150)
                scaled_pixmap = pixmap.scaled(
                    150, 150,
                    QtCore.Qt.KeepAspectRatio,
                    QtCore.Qt.SmoothTransformation
                )
                self.photo_preview_label.setPixmap(scaled_pixmap)
                self.photo_preview_label.setText("")
            else:
                self.photo_preview_label.setText("Failed to load image")
        except Exception as e:
            self.photo_preview_label.setText(f"Error: {e}")
    
    def get_data(self):
        """Return title, content, and image path"""
        return (
            self.title_edit.text().strip(),
            self.content_edit.toPlainText().strip(),
            self.image_path if self.image_path else None
        )
