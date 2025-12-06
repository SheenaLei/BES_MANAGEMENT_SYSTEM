# gui/views/sidebar_home_view.py
from PyQt5 import uic, QtWidgets, QtCore, QtGui
from pathlib import Path
from gui.widgets.notification_bar import NotificationBar
from app.db import SessionLocal
from app.models import Resident

UI_PATH = Path(__file__).resolve().parent.parent / "ui" / "sidebarhomee.ui"
ADMIN_RESIDENTS_UI_PATH = Path(__file__).resolve().parent.parent / "ui" / "admin_residents.ui"


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
            print(f"✅ Found QStackedWidget as content area")
            return
        
        # Look for QTabWidget
        tab_widgets = self.findChildren(QtWidgets.QTabWidget)
        if tab_widgets:
            self.content_area = tab_widgets[0]
            print(f"✅ Found QTabWidget as content area")
            return
        
        # Look for a large QFrame or QWidget
        frames = self.findChildren(QtWidgets.QFrame)
        if frames:
            # Find the largest frame (likely the content area)
            self.content_area = max(frames, key=lambda f: f.width() * f.height())
            print(f"✅ Found QFrame as content area: {self.content_area.objectName()}")
            return
        
        # Fallback: use central widget
        self.content_area = self.centralWidget()
        print(f"⚠️ Using central widget as content area")
    
    def connect_buttons(self):
        """Connect sidebar buttons to their functions"""
        
        # RESIDENTS button (pushButton_24)
        if hasattr(self, 'pushButton_24'):
            self.pushButton_24.clicked.connect(self.show_residents_page)
            print(f"✅ Connected RESIDENTS button")
        
        # DASHBOARD button (pushButton_15)
        if hasattr(self, 'pushButton_15'):
            self.pushButton_15.clicked.connect(self.show_dashboard_page)
            print(f"✅ Connected DASHBOARD button")
        
        # SERVICES button - search through ALL buttons to find it
        services_connected = False
        for btn in self.findChildren(QtWidgets.QPushButton):
            if btn and hasattr(btn, 'text'):
                button_text = btn.text().upper()
                # Check if button text contains SERVICE or SERVICES
                if 'SERVICE' in button_text and '×' not in button_text:
                    btn.clicked.connect(self.show_services_page)
                    print(f"✅ Connected SERVICES button: {btn.objectName()} with text '{btn.text()}'")
                    services_connected = True
                    break
        
        if not services_connected:
            print(f"⚠️ SERVICES button not found - will print all buttons for debugging")
            # Debug: print all button names and texts
            for btn in self.findChildren(QtWidgets.QPushButton):
                if btn:
                    print(f"   Button: {btn.objectName()} - Text: '{btn.text()}'")
        
        # ANNOUNCEMENT button - search through ALL buttons to find it
        announcement_connected = False
        for btn in self.findChildren(QtWidgets.QPushButton):
            if btn and hasattr(btn, 'text'):
                button_text = btn.text().upper()
                # Check if button text contains ANNOUNCEMENT
                if 'ANNOUNCEMENT' in button_text and '×' not in button_text:
                    btn.clicked.connect(self.show_announcement_page)
                    print(f"✅ Connected ANNOUNCEMENT button: {btn.objectName()} with text '{btn.text()}'")
                    announcement_connected = True
                    break
        
        if not announcement_connected:
            print(f"⚠️ ANNOUNCEMENT button not found")
        
        # PROFILE button (pushButton_12) - could be logout
        if hasattr(self, 'pushButton_12'):
            self.pushButton_12.clicked.connect(self.show_profile_page)
            print(f"✅ Connected PROFILE button")
        
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
                print(f"✅ Connected logout button")
                break
    
    def show_residents_page(self):
        """Load admin_residents.ui into the content area"""
        try:
            print("📋 Loading Residents page...")
            
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
                        print(f"✅ Found inner content widget: {child.objectName()}")
                        break
                
                # If we didn't find it by name, try to get the first child widget with a layout
                if not residents_widget:
                    for child in central.findChildren(QtWidgets.QWidget):
                        if child.layout() and child.parent() == central:
                            residents_widget = child
                            print(f"✅ Found widget with layout: {child.objectName()}")
                            break
            
            # Fallback: use central widget if we couldn't find the inner one
            if not residents_widget:
                residents_widget = central
                print("⚠️ Using central widget as fallback")
            
            if not residents_widget:
                # Last resort: create wrapper
                residents_widget = QtWidgets.QWidget()
                layout = QtWidgets.QVBoxLayout(residents_widget)
                layout.addWidget(temp_window)
                print("⚠️ Created wrapper widget")
            
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
            print(f"📊 Residents widget: {residents_widget}")
            print(f"📊 Widget size: {residents_widget.size()}")
            print(f"📊 Content area: {self.content_area}")
            print(f"📊 Content area size: {self.content_area.size()}")
            
            # Clear existing content and add new widget
            if isinstance(self.content_area, QtWidgets.QStackedWidget):
                # If it's a stacked widget, add as new page
                while self.content_area.count() > 0:
                    old_widget = self.content_area.widget(0)
                    self.content_area.removeWidget(old_widget)
                    old_widget.deleteLater()
                self.content_area.addWidget(residents_widget)
                self.content_area.setCurrentWidget(residents_widget)
                print(f"📊 Added to QStackedWidget. Current index: {self.content_area.currentIndex()}")
                print(f"📊 Current widget: {self.content_area.currentWidget()}")
            
            elif isinstance(self.content_area, QtWidgets.QTabWidget):
                # If it's a tab widget, clear and add
                self.content_area.clear()
                self.content_area.addTab(residents_widget, "Residents")
                print(f"📊 Added to QTabWidget")
            
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
                print(f"📊 Added to layout")
            
            # Force visibility
            residents_widget.show()
            self.content_area.show()
            self.content_area.raise_()
            self.content_area.update()
            
            self.notification.show_success("✅ Residents page loaded")
            print("✅ Residents page loaded successfully!")
            
        except Exception as e:
            self.notification.show_error(f"❌ Error loading residents page: {e}")
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

    def load_residents_table(self, widget, search_text=""):
        """Fetch residents from DB and populate the table"""
        try:
            # Find the table widget
            table = widget.findChild(QtWidgets.QTableWidget, "tableWidget")
            if not table:
                print("❌ Table widget not found!")
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

            print(f"📊 Found {len(residents)} residents")
            
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
            
            print("✅ Table populated successfully")
            
        except Exception as e:
            print(f"❌ Error populating table: {e}")
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
            print(f"❌ Error: {e}")
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
                print(f"✅ Connected SUBMIT button (pushButton_2) for resident {resident_id}")
            else:
                print("❌ SUBMIT button (pushButton_2) not found!")
                # Try to find any button with SUBMIT text
                for btn in dialog.findChildren(QtWidgets.QPushButton):
                    if "submit" in btn.text().lower():
                        btn.clicked.connect(lambda: self.save_resident_edits(dialog, resident_id))
                        print(f"✅ Connected button with text: {btn.text()}")
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
                print(f"✅ Connected UPLOAD photo button")
            else:
                print(f"⚠️ Upload button or photo label not found")
            
            dialog.setWindowModality(QtCore.Qt.ApplicationModal)
            dialog.show()
            
            self.notification.show_info(f"✏️ Editing: {resident.first_name} {resident.last_name}")
            
        except Exception as e:
            self.notification.show_error(f"❌ Error opening edit dialog: {e}")
            print(f"❌ Error: {e}")
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
                print(f"📸 Selected photo: {file_path}")
                
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
                    print(f"✅ Photo loaded and displayed")
                else:
                    self.notification.show_error("❌ Failed to load image!")
                    print("❌ Failed to load pixmap")
            else:
                print("ℹ️ No photo selected")
                
        except Exception as e:
            self.notification.show_error(f"❌ Error uploading photo: {e}")
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    def save_resident_edits(self, dialog, resident_id):
        """Save edited resident data to database"""
        print(f"🔄 save_resident_edits called for resident {resident_id}")
        try:
            # Read all form fields
            data = {}
            
            print("📝 Reading form fields...")
            
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
                print(f"📸 Will save photo: {dialog.photo_path}")
            
            # Debug: Show collected data
            print(f"📊 Collected data: {data}")
            
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
                
                print(f"✅ Updated resident {resident_id}: {resident.first_name} {resident.last_name}")
                
                # Close dialog
                dialog.close()
                
                # Refresh the table
                if hasattr(self, 'current_residents_widget'):
                    self.load_residents_table(self.current_residents_widget)
                    self.notification.show_success(f"✅ Updated: {resident.first_name} {resident.last_name}")
                
            except Exception as e:
                db.rollback()
                self.notification.show_error(f"❌ Database error: {e}")
                print(f"❌ Database error: {e}")
                import traceback
                traceback.print_exc()
            finally:
                db.close()
                
        except Exception as e:
            self.notification.show_error(f"❌ Error saving data: {e}")
            print(f"❌ Error: {e}")
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
                
                print("✅ Connected search functionality")
            else:
                print("⚠️ Search button or input not found")
                
        except Exception as e:
            print(f"❌ Error connecting search: {e}")
    
    def perform_search(self, widget):
        """Perform search and refresh table"""
        try:
            search_text = self.search_input.text().strip()
            print(f"🔍 Searching for: '{search_text}'")
            
            # Reload table with search filter
            self.load_residents_table(widget, search_text)
            
            if search_text:
                self.notification.show_info(f"🔍 Search: '{search_text}'")
            else:
                self.notification.show_info("📋 Showing all residents")
                
        except Exception as e:
            print(f"❌ Error performing search: {e}")
    
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
                print(f"✅ Connected Add Resident button: {btn.objectName()}")
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
                print(f"✅ Connected SUBMIT button for adding new resident")
            else:
                print("❌ SUBMIT button (pushButton_2) not found!")
            
            # CONNECT UPLOAD PHOTO BUTTON
            upload_button = dialog.findChild(QtWidgets.QPushButton, "pushButton")
            photo_label = dialog.findChild(QtWidgets.QLabel, "label_11")
            
            if upload_button and photo_label:
                dialog.photo_label = photo_label
                dialog.photo_path = None
                upload_button.clicked.connect(lambda: self.upload_resident_photo(dialog))
                print(f"✅ Connected UPLOAD photo button")
            
            # Show as modal dialog
            dialog.setWindowModality(QtCore.Qt.ApplicationModal)
            dialog.show()
            
            self.notification.show_info("📝 Fill in resident information and click SUBMIT")
                
        except Exception as e:
            self.notification.show_error(f"❌ Error opening data collection: {e}")
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    def add_new_resident(self, dialog):
        """Save new resident to database"""
        print(f"🔄 add_new_resident called")
        try:
            # Read all form fields
            data = {}
            
            print("📝 Reading form fields...")
            
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
                print(f"📸 Will save photo: {dialog.photo_path}")
            
            # Debug: Show collected data
            print(f"📊 Collected data: {data}")
            
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
                
                print(f"✅ Added new resident ID {new_resident.resident_id}: {new_resident.first_name} {new_resident.last_name}")
                
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
                print(f"❌ Database error: {e}")
                import traceback
                traceback.print_exc()
            finally:
                db.close()
                
        except Exception as e:
            self.notification.show_error(f"❌ Error saving data: {e}")
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

    
    def show_dashboard_page(self):
        """Show dashboard/home page"""
        dashboard = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(dashboard)
        
        label = QtWidgets.QLabel("🏠 Dashboard")
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
        
        self.replace_content(dashboard)
        self.notification.show_info("🏠 Dashboard")
    
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
    
    def show_announcement_page(self):
        """Show admin announcements page with database-driven announcements"""
        try:
            print("📢 Loading Admin Announcements page...")
            
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
            print("✅ Admin Announcements page loaded successfully!")
            
        except Exception as e:
            self.notification.show_error(f"❌ Error loading Announcements: {e}")
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    def show_services_page(self):
        """Load and display admin services page (ADMIN_SERVICES_PG1.ui)"""
        try:
            print("🛎️ Loading Admin Services page...")
            
            # Path to ADMIN_SERVICES_PG1.ui
            services_ui_path = Path(__file__).resolve().parent.parent / "ui" / "ADMIN_SERVICES_PG1.ui"
            
            if not services_ui_path.exists():
                self.notification.show_error(f"❌ Admin Services UI not found: {services_ui_path}")
                print(f"❌ File not found: {services_ui_path}")
                return
            
            # ADMIN_SERVICES_PG1.ui might be a QMainWindow, handle it like other pages
            # Try to load it
            temp_window = QtWidgets.QMainWindow()
            uic.loadUi(str(services_ui_path), temp_window)
            
            # Try to get central widget
            services_widget = temp_window.centralWidget()
            
            if not services_widget:
                # If no central widget, load as QWidget directly
                services_widget = QtWidgets.QWidget()
                uic.loadUi(str(services_ui_path), services_widget)
            else:
                # Reparent to prevent destruction
                services_widget.setParent(None)
            
            # Set size policy to expand and fill the content area
            services_widget.setSizePolicy(
                QtWidgets.QSizePolicy.Expanding,
                QtWidgets.QSizePolicy.Expanding
            )
            
            # Find and populate the table with certificate requests
            self.load_certificate_requests_table(services_widget)
            
            # Replace content - uses UI file's own beautiful cyan background!
            self.replace_content(services_widget)
            
            self.notification.show_success("🛎️ Admin Services page loaded")
            print("✅ Admin Services page loaded successfully!")
            
        except Exception as e:
            self.notification.show_error(f"❌ Error loading admin services: {e}")
            print(f"❌ Error: {e}")
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
                    print(f"✅ Found table: {table_name}")
                    break
            
            if not table:
                # Try finding any QTableWidget
                tables = widget.findChildren(QtWidgets.QTableWidget)
                if tables:
                    table = tables[0]
                    print(f"✅ Found table widget")
            
            if not table:
                print("⚠️ No table widget found in services page")
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
                
                print(f"📊 Found {len(requests)} certificate requests")
                
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
                
                
                print(f"✅ Table populated with {len(requests)} requests")
                
            except Exception as e:
                print(f"❌ Database error: {e}")
                import traceback
                traceback.print_exc()
            finally:
                db.close()
                
        except Exception as e:
            print(f"❌ Error loading table: {e}")
            import traceback
            traceback.print_exc()
    
    
    def view_request_details(self, request):
        """View request details in a floating dialog"""
        try:
            print(f"\n👁 Viewing request details for Request ID: {request.request_id}")
            
            # Path to ADMIN_SERVICES_P2.ui
            details_ui_path = Path(__file__).resolve().parent.parent / "ui" / "ADMIN_SERVICES_P2.ui"
            
            if not details_ui_path.exists():
                self.notification.show_error(f"❌ UI file not found: {details_ui_path}")
                print(f"❌ File not found: {details_ui_path}")
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
            
            print(f"✅ Request details dialog displayed!")
            
        except Exception as e:
            self.notification.show_error(f"❌ Error loading request details: {e}")
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    def populate_dialog_with_data(self, dialog, request):
        """Populate the dialog with request data"""
        try:
            print(f"📋 Populating dialog with request data...")
            
            # Find all widgets
            all_labels = dialog.findChildren(QtWidgets.QLabel)
            all_line_edits = dialog.findChildren(QtWidgets.QLineEdit)
            all_text_edits = dialog.findChildren(QtWidgets.QTextEdit)
            all_buttons = dialog.findChildren(QtWidgets.QPushButton)
            
            print(f"  Found: {len(all_labels)} labels, {len(all_line_edits)} line edits, {len(all_text_edits)} text edits")
            
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
                        print(f"  ✅ {obj_name} = '{value}'")
                        fields_filled += 1
                        break
            
            # Fill QTextEdit fields
            for text_edit in all_text_edits:
                obj_name = text_edit.objectName().lower()
                
                for key, value in field_data.items():
                    if key in obj_name:
                        text_edit.setPlainText(value)
                        print(f"  ✅ {obj_name} = '{value}'")
                        fields_filled += 1
                        break
            
            print(f"  ✅ Filled {fields_filled} fields")
            
            # Display clickable ID photo
            if request.uploaded_file_path:
                print(f"\n🖼️ Loading uploaded ID photo...")
                
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
                            print(f"  ✅ ID photo displayed (clickable)")
                        else:
                            image_label.setText("❌ Invalid image")
                    else:
                        image_label.setText("❌ File not found")
                else:
                    print(f"  ⚠️ No image label found")
            else:
                print(f"  ℹ️ No uploaded photo")
            
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
                    print(f"  ✅ Connected APPROVE button")
                    
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
                    print(f"  ✅ Connected REJECT button")
            
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
                                print(f"  ✅ Centered button layout")
                            break
            
            print(f"✅ Dialog fully populated!")
            
        except Exception as e:
            print(f"⚠️ Error populating dialog: {e}")
            import traceback
            traceback.print_exc()
    
    def approve_request(self, request, dialog):
        """Approve the certificate request"""
        try:
            from app.database import SessionLocal
            db = SessionLocal()
            
            request.status = 'Approved'
            request.reviewed_at = datetime.utcnow()
            # request.reviewed_by_admin_id = self.current_admin_id  # Add if you have admin ID
            
            db.commit()
            db.close()
            
            self.notification.show_success(f"✅ Request #{request.request_id} APPROVED!")
            print(f"✅ Request #{request.request_id} approved")
            
            dialog.accept()  # Close dialog
            self.show_services_page()  # Refresh table
            
        except Exception as e:
            self.notification.show_error(f"❌ Error approving request: {e}")
            print(f"❌ Error: {e}")
    
    def reject_request(self, request, dialog):
        """Reject the certificate request"""
        try:
            from app.database import SessionLocal
            db = SessionLocal()
            
            request.status = 'Rejected'
            request.reviewed_at = datetime.utcnow()
            # request.reviewed_by_admin_id = self.current_admin_id  # Add if you have admin ID
            
            db.commit()
            db.close()
            
            self.notification.show_success(f"❌ Request #{request.request_id} REJECTED")
            print(f"❌ Request #{request.request_id} rejected")
            
            dialog.accept()  # Close dialog
            self.show_services_page()  # Refresh table
            
        except Exception as e:
            self.notification.show_error(f"❌ Error rejecting request: {e}")
            print(f"❌ Error: {e}")
    
    
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
        from gui.views.login_view import LoginWindow
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = SidebarHomeWindow()
    window.showMaximized()
    sys.exit(app.exec_())
