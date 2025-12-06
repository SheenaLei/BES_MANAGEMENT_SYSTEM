# gui/views/sidebar_home_user_view.py
from PyQt5 import uic, QtWidgets, QtCore, QtGui
from pathlib import Path
from gui.widgets.notification_bar import NotificationBar
from app.db import SessionLocal
from app.models import Resident, Account

UI_PATH = Path(__file__).resolve().parent.parent / "ui" / "sidebarhomee_USER.ui"


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
            print(f"❌ Error loading user data: {e}")
        finally:
            db.close()
    
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
        
        # DASHBOARD button (pushButton_15)
        if hasattr(self, 'pushButton_15'):
            self.pushButton_15.clicked.connect(self.show_dashboard_page)
            print(f"✅ Connected DASHBOARD button")
        
        # SERVICES button (pushButton_13)
        if hasattr(self, 'pushButton_13'):
            self.pushButton_13.clicked.connect(self.show_services_page)
            print(f"✅ Connected SERVICES button")
        
        # NOTIFICATIONS button (pushButton_17)
        if hasattr(self, 'pushButton_17'):
            self.pushButton_17.clicked.connect(self.show_notifications_page)
            print(f"✅ Connected NOTIFICATIONS button")
        
        # ANNOUNCEMENT button (pushButton_18)
        if hasattr(self, 'pushButton_18'):
            self.pushButton_18.clicked.connect(self.show_announcement_page)
            print(f"✅ Connected ANNOUNCEMENT button")
        
        # MY REQUEST button (pushButton_14)
        if hasattr(self, 'pushButton_14'):
            self.pushButton_14.clicked.connect(self.show_my_request_page)
            print(f"✅ Connected MY REQUEST button")
        
        # PAYMENT button (pushButton_16)
        if hasattr(self, 'pushButton_16'):
            self.pushButton_16.clicked.connect(self.show_payment_page)
            print(f"✅ Connected PAYMENT button")
        
        # HISTORY button (pushButton_19)
        if hasattr(self, 'pushButton_19'):
            self.pushButton_19.clicked.connect(self.show_history_page)
            print(f"✅ Connected HISTORY button")
        
        # BLOTTER button (pushButton_20)
        if hasattr(self, 'pushButton_20'):
            self.pushButton_20.clicked.connect(self.show_blotter_page)
            print(f"✅ Connected BLOTTER button")
        
        # OFFICIALS button (pushButton_11)
        if hasattr(self, 'pushButton_11'):
            self.pushButton_11.clicked.connect(self.show_officials_page)
            print(f"✅ Connected OFFICIALS button")
        
        # ALL ABOUT button (pushButton_24)
        if hasattr(self, 'pushButton_24'):
            self.pushButton_24.clicked.connect(self.show_allabout_page)
            print(f"✅ Connected ALL ABOUT button")
        
        # PROFILE button (pushButton_12) - Logout
        if hasattr(self, 'pushButton_12'):
            self.pushButton_12.clicked.connect(self.handle_logout)
            print(f"✅ Connected PROFILE/LOGOUT button")
    
    def show_dashboard_page(self):
        """Show dashboard page"""
        self.notification.show_info("📊 Dashboard page")
        print("📊 Dashboard clicked")
    
    def show_services_page(self):
        """Load and display services page"""
        try:
            print("🛎️ Loading Services page...")
            
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
            
            # Set size policy to expand
            services_widget.setSizePolicy(
                QtWidgets.QSizePolicy.Expanding,
                QtWidgets.QSizePolicy.Expanding
            )
            
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
                print("✅ Connected REQUEST button to load services_p2")
            else:
                print("⚠️ REQUEST button not found in services_page1")
            
            # Load services into the widget (if there are service buttons/cards)
            self.load_services_content(services_widget)
            
            # Replace content in the stacked widget
            self.replace_content(services_widget)
            
            self.notification.show_success("🛎️ Services page loaded")
            print("✅ Services page loaded successfully!")
            
        except Exception as e:
            self.notification.show_error(f"❌ Error loading services: {e}")
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    def show_services_p2(self):
        """Show services_p2.ui as a centered popup dialog"""
        try:
            print("📋 Opening Services P2 (Certificate Selection) as popup...")
            
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
                print("✅ Connected Indigency button")
            if clearance_btn:
                clearance_btn.clicked.connect(lambda: self.handle_certificate_request("Barangay Clearance", dialog))
                print("✅ Connected Clearance button")
            if id_btn:
                id_btn.clicked.connect(lambda: self.handle_certificate_request("Barangay ID", dialog))
                print("✅ Connected ID button")
            if permit_btn:
                permit_btn.clicked.connect(lambda: self.handle_certificate_request("Business Permit", dialog))
                print("✅ Connected Permit button")
            
            # Center the dialog on screen
            dialog.move(
                self.geometry().center() - dialog.rect().center()
            )
            
            # Show as modal dialog (blocks interaction with parent)
            dialog.exec_()
            
            print("✅ Services P2 popup displayed!")
            
        except Exception as e:
            self.notification.show_error(f"❌ Error loading services P2: {e}")
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    def handle_certificate_request(self, certificate_type, dialog):
        """Handle certificate request and load appropriate form"""
        print(f"📝 Requesting: {certificate_type}")
        
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
            print(f"📋 Loading form for {certificate_type}...")
            
            # Path to the UI file
            form_ui_path = Path(__file__).resolve().parent.parent / "ui" / ui_filename
            
            if not form_ui_path.exists():
                self.notification.show_error(f"❌ Form UI not found: {ui_filename}")
                print(f"❌ File not found: {form_ui_path}")
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
                
                print(f"✅ Successfully created floating form dialog")
                
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
                print(f"✅ Form submitted successfully")
            elif result == QtWidgets.QDialog.Rejected:
                # User clicked BACK - show certificate selection again
                print(f"↩️ User went back to certificate selection")
                self.show_services_p2()
            
        except Exception as e:
            self.notification.show_error(f"❌ Error loading form: {e}")
            print(f"❌ Error loading {ui_filename}: {e}")
            import traceback
            traceback.print_exc()
    
    def handle_back_to_selection(self, dialog):
        """Handle BACK button - close dialog and return code for showing selection"""
        print("⬅ BACK button clicked")
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
                print(f"✅ Connected SUBMIT button for {certificate_type}")
            
            # Find UPLOAD button (pushButton_2) if exists
            upload_btn = form_widget.findChild(QtWidgets.QPushButton, "pushButton_2")
            if upload_btn:
                try:
                    upload_btn.clicked.disconnect()
                except:
                    pass
                upload_btn.clicked.connect(lambda: self.upload_document(form_widget))
                print(f"✅ Connected UPLOAD button")
                
        except Exception as e:
            print(f"⚠️ Error connecting form buttons: {e}")
    
    def upload_document(self, form_widget):
        """Handle document upload"""
        try:
            # Open file dialog
            file_dialog = QtWidgets.QFileDialog()
            file_path, _ = file_dialog.getOpenFileName(
                self,
                "Select Document",
                "",
                "Image Files (*.png *.jpg *.jpeg *.pdf);;All Files (*)"
            )
            
            if file_path:
                # Find the image label (label_12)
                img_label = form_widget.findChild(QtWidgets.QLabel, "label_12")
                if img_label:
                    # Load and display image
                    pixmap = QtGui.QPixmap(file_path)
                    if not pixmap.isNull():
                        scaled_pixmap = pixmap.scaled(
                            250, 100,
                            QtCore.Qt.KeepAspectRatio,
                            QtCore.Qt.SmoothTransformation
                        )
                        img_label.setPixmap(scaled_pixmap)
                        img_label.setText("")
                        
                        # Store file path
                        form_widget.uploaded_file_path = file_path
                        
                        self.notification.show_success("✅ Document uploaded!")
                        print(f"✅ Document uploaded: {file_path}")
                    else:
                        self.notification.show_error("❌ Failed to load document")
                else:
                    self.notification.show_warning("⚠️ Image label not found")
        except Exception as e:
            self.notification.show_error(f"❌ Upload error: {e}")
            print(f"❌ Upload error: {e}")
    
    def submit_certificate_request(self, certificate_type, form_widget, dialog=None):
        """Handle certificate request submission"""
        print(f"📤 Submitting request for {certificate_type}")
        
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
                print(f"  📝 LineEdit {field_name}: {field_value}")
            
            # Get all QComboBox fields
            combo_data = {}
            for combo_box in form_widget.findChildren(QtWidgets.QComboBox):
                field_name = combo_box.objectName()
                field_value = combo_box.currentText()
                combo_data[field_name] = field_value
                print(f"  📝 ComboBox {field_name}: {field_value}")
            
            # Smart field extraction
            # Try to find fields by their likely names/positions
            last_name = form_data.get('lineEdit', '') or form_data.get('lineEdit_2', '')
            first_name = form_data.get('lineEdit_3', '') or form_data.get('lineEdit_4', '')
            middle_name = form_data.get('lineEdit_5', '') or form_data.get('lineEdit_6', '')
            suffix = form_data.get('lineEdit_7', '')
            phone_number = form_data.get('lineEdit_8', '') or form_data.get('lineEdit_9', '')
            
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
            
            print(f"  ✅ Extracted - Name: {first_name} {last_name}, Purpose: {purpose}, Qty: {quantity}")
            
            # VALIDATION: Check if required fields are filled
            if not first_name and not last_name:
                self.notification.show_error("❌ Please enter your name!")
                print("❌ Validation failed: Name is required")
                return
            
            if not purpose or purpose.lower() == 'select':
                self.notification.show_error("❌ Please select a purpose!")
                print("❌ Validation failed: Purpose is required")
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
                    created_at=datetime.utcnow()
                )
                
                # Save to database
                db.add(new_request)
                db.commit()
                
                print(f"✅ Certificate request saved! ID: {new_request.request_id}")
                self.notification.show_success(f"✅ {certificate_type} request submitted successfully!")
                
                # Close the dialog if provided
                if dialog:
                    dialog.accept()
                
            except Exception as e:
                db.rollback()
                print(f"❌ Database error: {e}")
                self.notification.show_error(f"❌ Failed to save request: {str(e)}")
                import traceback
                traceback.print_exc()
            finally:
                db.close()
                
        except Exception as e:
            print(f"❌ Error submitting request: {e}")
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
            
            print(f"📋 Found {len(services)} services")
            
            # TODO: Populate service cards/buttons in the UI
            # This depends on how services_page1.ui is structured
            # You can add service cards dynamically here
            
        except Exception as e:
            print(f"⚠️ Error loading services content: {e}")
    
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
                print(f"✅ Added to QStackedWidget")
            
            elif isinstance(self.content_area, QtWidgets.QTabWidget):
                self.content_area.clear()
                self.content_area.addTab(new_widget, "Page")
                print(f"✅ Added to QTabWidget")
            
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
                print(f"✅ Added to layout")
            
            # Force visibility
            new_widget.show()
            self.content_area.show()
            self.content_area.update()
            
        except Exception as e:
            print(f"❌ Error replacing content: {e}")

    
    def show_notifications_page(self):
        """Show user notifications"""
        try:
            print("🔔 Loading Notifications page...")
            
            # Path to user_notificationss.ui (note: double 's')
            notifications_ui_path = Path(__file__).resolve().parent.parent / "ui" / "user_notificationss.ui"
            
            if not notifications_ui_path.exists():
                self.notification.show_error(f"❌ Notifications UI not found: {notifications_ui_path}")
                print(f"❌ File not found: {notifications_ui_path}")
                return
            
            # Load the UI
            temp_window = QtWidgets.QMainWindow()
            uic.loadUi(str(notifications_ui_path), temp_window)
            
            # Get central widget
            notifications_widget = temp_window.centralWidget()
            
            if not notifications_widget:
                # If no central widget, load as QWidget directly
                notifications_widget = QtWidgets.QWidget()
                uic.loadUi(str(notifications_ui_path), notifications_widget)
            else:
                # Reparent to prevent destruction
                notifications_widget.setParent(None)
            
            # Set size policy to expand
            notifications_widget.setSizePolicy(
                QtWidgets.QSizePolicy.Expanding,
                QtWidgets.QSizePolicy.Expanding
            )
            
            # Add light blue background (same as My Requests)
            notifications_widget.setStyleSheet("""
                QWidget {
                    background-color: #BBDEFB;  /* Light blue - more visible */
                }
            """)
            
            # Replace content
            self.replace_content(notifications_widget)
            
            self.notification.show_success("🔔 Notifications loaded!")
            print("✅ Notifications page loaded successfully!")
            
        except Exception as e:
            self.notification.show_error(f"❌ Error loading Notifications: {e}")
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    def show_announcement_page(self):
        """Show announcements (user view from database)"""
        try:
            print("📢 Loading Announcements page...")
            
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
            print("✅ Announcements page loaded successfully!")
            
        except Exception as e:
            self.notification.show_error(f"❌ Error loading Announcements: {e}")
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    def show_my_request_page(self):
        """Show user's certificate requests (My Requests) - Shopee-style Status Tracker in Table"""
        try:
            print("📋 Loading My Requests page with status tracker...")
            
            # Load the status_user.ui file (with your table design)
            status_ui_path = Path(__file__).resolve().parent.parent / "ui" / "status_user.ui"
            
            if not status_ui_path.exists():
                self.notification.show_error(f"❌ Status UI not found: {status_ui_path}")
                print(f"❌ File not found: {status_ui_path}")
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
                
                print("✅ Status tracker inserted into scroll area")
            else:
                print("⚠️ Scroll area not found in UI, using tracker directly")
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
            print("✅ My Requests page with status tracker loaded successfully!")
            
        except Exception as e:
            self.notification.show_error(f"❌ Error loading My Requests: {e}")
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    def show_payment_page(self):
        """Show payment page"""
        self.notification.show_info("💳 Payment page")
        print("💳 Payment clicked")
    
    def show_history_page(self):
        """Show history page"""
        self.notification.show_info("📜 History page")
        print("📜 History clicked")
    
    def show_blotter_page(self):
        """Show blotter page"""
        try:
            print("🚨 Loading Blotter page...")
            
            # Path to user_blotter.ui
            blotter_ui_path = Path(__file__).resolve().parent.parent / "ui" / "user_blotter.ui"
            
            if not blotter_ui_path.exists():
                self.notification.show_error(f"❌ Blotter UI not found: {blotter_ui_path}")
                print(f"❌ File not found: {blotter_ui_path}")
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
            print("✅ Blotter page loaded successfully!")
            
        except Exception as e:
            self.notification.show_error(f"❌ Error loading Blotter: {e}")
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    def show_officials_page(self):
        """Show officials page"""
        self.notification.show_info("👔 Officials page")
        print("👔 Officials clicked")
    
    def show_allabout_page(self):
        """Show all about page"""
        self.notification.show_info("ℹ️ All About page")
        print("ℹ️ All About clicked")
    
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
            print("👋 User logged out")
            self.notification.show_info("👋 Logging out...")
            
            # Close this window and return to login
            QtCore.QTimer.singleShot(1000, self.open_login)
    
    def open_login(self):
        """Return to login window"""
        try:
            from gui.views.login_view import LoginWindow
            self.login_window = LoginWindow()
            self.login_window.show()
            self.close()
        except Exception as e:
            print(f"❌ Error opening login: {e}")


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = SidebarHomeUserWindow()
    window.showMaximized()
    sys.exit(app.exec_())
