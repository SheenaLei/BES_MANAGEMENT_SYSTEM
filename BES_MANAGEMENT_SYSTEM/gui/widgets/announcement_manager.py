"""
Announcement Manager Widget - Displays announcements with admin controls
"""
from PyQt5 import QtWidgets, QtCore, QtGui
from pathlib import Path
from app.db import SessionLocal
from app.models import Announcement
from datetime import datetime


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
                    posted_at=datetime.now(),
                    visible=True
                )
                db.add(new_announcement)
                db.commit()
                
                print(f"✅ Added announcement: {title}")
                self.load_announcements()  # Refresh display
                
            except Exception as e:
                db.rollback()
                print(f"Error adding announcement: {e}")
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
                image_path=announcement.image_path if hasattr(announcement, 'image_path') else "",
                parent=self
            )
            
            if dialog.exec_() == QtWidgets.QDialog.Accepted:
                title, content, image_path = dialog.get_data()
                
                announcement.title = title
                announcement.content = content
                if hasattr(announcement, 'image_path'):
                    announcement.image_path = image_path
                db.commit()
                
                print(f"✅ Updated announcement: {title}")
                self.load_announcements()  # Refresh display
                
        except Exception as e:
            db.rollback()
            print(f"Error editing announcement: {e}")
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
                    
                    print(f"✅ Deleted announcement")
                    self.load_announcements()  # Refresh display
                    
            except Exception as e:
                db.rollback()
                print(f"Error deleting announcement: {e}")
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to delete announcement: {e}")
            finally:
                db.close()


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
