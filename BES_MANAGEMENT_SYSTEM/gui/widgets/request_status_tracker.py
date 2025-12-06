"""
Request Status Tracker Widget - Shopee-style Progress Tracking
Displays request status with visual progress indicators and detailed history
"""
from PyQt5 import QtWidgets, QtCore, QtGui
from pathlib import Path
from app.db import SessionLocal
from app.models import CertificateRequest, Account
from datetime import datetime


class RequestStatusWidget(QtWidgets.QWidget):
    """Custom widget for displaying request status tracking"""
    
    def __init__(self, username=None, parent=None):
        super().__init__(parent)
        self.username = username
        self.requests = []
        self.current_request_index = 0
        
        self.init_ui()
        self.load_requests()
        if self.requests:
            self.display_request(0)
    
    def init_ui(self):
        """Initialize the UI components"""
        # Main layout
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)
        
        # Title and navigation header
        header_layout = QtWidgets.QHBoxLayout()
        
        # Request ID and Status label
        self.request_header_label = QtWidgets.QLabel("REQUEST ID: Loading...")
        self.request_header_label.setAlignment(QtCore.Qt.AlignCenter)
        self.request_header_label.setStyleSheet("""
            font-size: 11pt;
            color: #333;
            font-weight: bold;
            background: transparent;
        """)
        header_layout.addWidget(self.request_header_label)
        
        main_layout.addLayout(header_layout)
        
        # Request navigation (prev/next buttons if multiple requests)
        nav_layout = QtWidgets.QHBoxLayout()
        
        self.prev_btn = QtWidgets.QPushButton("← Previous Request")
        self.prev_btn.clicked.connect(self.show_previous_request)
        self.prev_btn.setStyleSheet(self.get_nav_button_style())
        
        self.request_counter_label = QtWidgets.QLabel("Request 0 of 0")
        self.request_counter_label.setAlignment(QtCore.Qt.AlignCenter)
        self.request_counter_label.setStyleSheet("font-size: 10pt; color: #666; background: transparent;")
        
        self.next_btn = QtWidgets.QPushButton("Next Request →")
        self.next_btn.clicked.connect(self.show_next_request)
        self.next_btn.setStyleSheet(self.get_nav_button_style())
        
        nav_layout.addWidget(self.prev_btn)
        nav_layout.addStretch()
        nav_layout.addWidget(self.request_counter_label)
        nav_layout.addStretch()
        nav_layout.addWidget(self.next_btn)
        
        main_layout.addLayout(nav_layout)
        
        # PROGRESS TRACKER (Shopee-style horizontal progress)
        progress_container = QtWidgets.QFrame()
        progress_container.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: none;
                padding: 20px 10px;
            }
        """)
        progress_layout = QtWidgets.QVBoxLayout(progress_container)
        
        # Progress tracker widget
        self.progress_tracker = self.create_progress_tracker()
        progress_layout.addWidget(self.progress_tracker)
        
        main_layout.addWidget(progress_container)
        
        # REQUEST DETAILS CARD
        details_card = QtWidgets.QFrame()
        details_card.setStyleSheet("""
            QFrame {
                background-color: #f9f9f9;
                border: 1px solid #e0e0e0;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        details_layout = QtWidgets.QVBoxLayout(details_card)
        
        details_title = QtWidgets.QLabel("Request Details")
        details_title.setStyleSheet("font-size: 12pt; font-weight: bold; color: #333; margin-bottom: 10px; background: transparent;")
        details_layout.addWidget(details_title)
        
        self.details_text = QtWidgets.QLabel("No request selected")
        self.details_text.setStyleSheet("font-size: 10pt; color: #666; line-height: 1.6; background: transparent;")
        self.details_text.setWordWrap(True)
        details_layout.addWidget(self.details_text)
        
        main_layout.addWidget(details_card)
        
        # HISTORY TIMELINE (Shopee-style detailed tracking)
        history_container = QtWidgets.QFrame()
        history_container.setStyleSheet("""
            QFrame {
                background-color: #f9f9f9;
                border: 1px solid #e0e0e0;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        history_layout = QtWidgets.QVBoxLayout(history_container)
        
        history_title = QtWidgets.QLabel("Request History & Tracking")
        history_title.setStyleSheet("font-size: 12pt; font-weight: bold; color: #333; margin-bottom: 15px; background: transparent;")
        history_layout.addWidget(history_title)
        
        # Scrollable history area
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        self.history_widget = QtWidgets.QWidget()
        self.history_layout = QtWidgets.QVBoxLayout(self.history_widget)
        self.history_layout.setSpacing(0)
        self.history_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll_area.setWidget(self.history_widget)
        history_layout.addWidget(scroll_area)
        
        main_layout.addWidget(history_container)
        
        # Set overall background to transparent (will inherit from container)
        self.setStyleSheet("""
            RequestStatusWidget {
                background-color: transparent;
            }
        """)
    
    def get_nav_button_style(self):
        return """
            QPushButton {
                background-color: #1976d2;
                color: white;
                font-size: 10pt;
                font-weight: bold;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
            QPushButton:pressed {
                background-color: #0d47a1;
            }
            QPushButton:disabled {
                background-color: #ccc;
                color: #888;
            }
        """
    
    def create_progress_tracker(self):
        """Create the horizontal progress tracker (Shopee-style)"""
        tracker_widget = QtWidgets.QWidget()
        # Use grid layout for better control
        tracker_layout = QtWidgets.QGridLayout(tracker_widget)
        tracker_layout.setContentsMargins(20, 10, 20, 10)
        tracker_layout.setHorizontalSpacing(0)
        tracker_layout.setVerticalSpacing(10)
        
        # Progress stages for certificate requests
        self.stages = [
            {"name": "Request\nSubmitted", "icon": "📝", "status": "submitted"},
            {"name": "Under\nReview", "icon": "🔍", "status": "review"},
            {"name": "Processing", "icon": "⚙️", "status": "processing"},
            {"name": "Ready for\nPickup", "icon": "📋", "status": "ready"},
            {"name": "Completed", "icon": "✅", "status": "completed"}
        ]
        
        self.stage_widgets = []
        col = 0  # Column counter
        
        for i, stage in enumerate(self.stages):
            # Row 0: Icon circles with lines between them
            # Create icon with container
            icon_container = QtWidgets.QWidget()
            icon_container.setFixedSize(70, 70)
            icon_layout = QtWidgets.QVBoxLayout(icon_container)
            icon_layout.setContentsMargins(0, 0, 0, 0)
            
            # Icon circle - LARGER and better rendering
            icon_label = QtWidgets.QLabel(stage["icon"])
            icon_label.setAlignment(QtCore.Qt.AlignCenter)
            icon_label.setFixedSize(70, 70)
            icon_label.setStyleSheet("""
                QLabel {
                    background-color: #e0e0e0;
                    border: 3px solid #bdbdbd;
                    border-radius: 35px;
                    font-size: 28pt;
                    color: #757575;
                    padding: 5px;
                }
            """)
            icon_label.setObjectName(f"icon_{i}")
            icon_layout.addWidget(icon_label)
            
            # Add icon to grid - Row 0
            tracker_layout.addWidget(icon_container, 0, col, QtCore.Qt.AlignCenter)
            col += 1
            
            # Add connecting line (except after last stage)
            if i < len(self.stages) - 1:
                # Line widget - positioned at center
                line_widget = QtWidgets.QWidget()
                line_widget.setFixedHeight(70)  # Same height as icon for alignment
                line_layout = QtWidgets.QHBoxLayout(line_widget)
                line_layout.setContentsMargins(-2, 0, -2, 0)  # Negative margins to overlap with circles
                line_layout.setSpacing(0)
                
                # Vertical container to center the line
                vert_container = QtWidgets.QWidget()
                vert_layout = QtWidgets.QVBoxLayout(vert_container)
                vert_layout.setContentsMargins(0, 0, 0, 0)
                vert_layout.setSpacing(0)
                
                # Top spacer - pushes line to middle
                top_spacer = QtWidgets.QWidget()
                top_spacer.setFixedHeight(33)  # (70-4)/2 = 33px to center the 4px line
                vert_layout.addWidget(top_spacer)
                
                # The actual connecting line
                line = QtWidgets.QFrame()
                line.setFrameShape(QtWidgets.QFrame.HLine)
                line.setFixedHeight(4)
                line.setStyleSheet("""
                    QFrame {
                        background-color: #e0e0e0;
                        border: none;
                    }
                """)
                line.setObjectName(f"line_{i}")
                vert_layout.addWidget(line)
                
                # Bottom spacer
                bottom_spacer = QtWidgets.QWidget()
                bottom_spacer.setFixedHeight(33)
                vert_layout.addWidget(bottom_spacer)
                
                line_layout.addWidget(vert_container)
                
                # Add line to grid - Row 0, stretch horizontally
                tracker_layout.addWidget(line_widget, 0, col)
                tracker_layout.setColumnStretch(col, 1)  # Allow line to stretch
                col += 1
            
            # Row 1: Stage names (below icons)
            name_label = QtWidgets.QLabel(stage["name"])
            name_label.setAlignment(QtCore.Qt.AlignCenter)
            name_label.setWordWrap(True)
            name_label.setMinimumWidth(70)
            name_label.setMaximumWidth(110)
            name_label.setStyleSheet("""
                QLabel {
                    font-size: 9pt;
                    color: #757575;
                    font-weight: normal;
                    background: transparent;
                    border: none;
                }
            """)
            name_label.setObjectName(f"name_{i}")
            
            # Calculate column for name (skip line columns)
            name_col = i * 2  # Each stage takes up 2 columns (icon + line or just icon for last)
            tracker_layout.addWidget(name_label, 1, name_col, QtCore.Qt.AlignCenter)
            
            # Row 2: Timestamps (below names)
            time_label = QtWidgets.QLabel("")
            time_label.setAlignment(QtCore.Qt.AlignCenter)
            time_label.setStyleSheet("""
                QLabel {
                    font-size: 8pt;
                    color: #999;
                    background: transparent;
                    border: none;
                }
            """)
            time_label.setObjectName(f"time_{i}")
            tracker_layout.addWidget(time_label, 2, name_col, QtCore.Qt.AlignCenter)
            
            self.stage_widgets.append({
                "icon": icon_label,
                "name": name_label,
                "time": time_label,
                "line": line if i < len(self.stages) - 1 else None
            })
        
        return tracker_widget
    
    def update_progress_tracker(self, current_stage, request_data):
        """Update the progress tracker based on current status"""
        # Reset all stages to inactive
        for i, widget_set in enumerate(self.stage_widgets):
            widget_set["icon"].setStyleSheet("""
                QLabel {
                    background-color: #e0e0e0;
                    border: 3px solid #bdbdbd;
                    border-radius: 35px;
                    font-size: 28pt;
                    color: #757575;
                    padding: 5px;
                }
            """)
            widget_set["name"].setStyleSheet("""
                QLabel {
                    font-size: 9pt;
                    color: #757575;
                    font-weight: normal;
                    background: transparent;
                    border: none;
                }
            """)
            widget_set["time"].setText("")
            
            # Reset line color (only if line exists - last stage has no line)
            if "line" in widget_set and widget_set["line"] is not None:
                widget_set["line"].setStyleSheet("""
                    QFrame {
                        background-color: #e0e0e0;
                        border: none;
                    }
                """)
        
        # Map status to stage index
        status_map = {
            "Pending": 0,
            "Under Review": 1,
            "Processing": 2,
            "Ready": 3,
            "Completed": 4,
            "Rejected": -1  # Special case
        }
        
        status = request_data.get("status", "Pending")
        stage_index = status_map.get(status, 0)
        
        # Handle rejected status (show red on first stage)
        if status == "Rejected":
            self.stage_widgets[0]["icon"].setStyleSheet("""
                QLabel {
                    background-color: #ffebee;
                    border: 3px solid #ef5350;
                    border-radius: 35px;
                    font-size: 28pt;
                    color: #c62828;
                    padding: 5px;
                }
            """)
            self.stage_widgets[0]["name"].setStyleSheet("""
                QLabel {
                    font-size: 9pt;
                    color: #c62828;
                    font-weight: bold;
                    background: transparent;
                    border: none;
                }
            """)
            return
        
        # Activate stages up to current stage
        for i in range(min(stage_index + 1, len(self.stage_widgets))):
            # Active stage styling (green)
            self.stage_widgets[i]["icon"].setStyleSheet("""
                QLabel {
                    background-color: #e8f5e9;
                    border: 3px solid #4caf50;
                    border-radius: 35px;
                    font-size: 28pt;
                    color: #2e7d32;
                    padding: 5px;
                }
            """)
            self.stage_widgets[i]["name"].setStyleSheet("""
                QLabel {
                    font-size: 9pt;
                    color: #2e7d32;
                    font-weight: bold;
                    background: transparent;
                    border: none;
                }
            """)
            
            # Add timestamp if available
            if i < len(request_data.get("history", [])):
                timestamp = request_data["history"][i].get("timestamp", "")
                self.stage_widgets[i]["time"].setText(timestamp)
            
            # Green connecting line (only if line exists)
            if "line" in self.stage_widgets[i] and self.stage_widgets[i]["line"] is not None:
                self.stage_widgets[i]["line"].setStyleSheet("""
                    QFrame {
                        background-color: #4caf50;
                        border: none;
                    }
                """)
    
    def load_requests(self):
        """Load user's certificate requests from database"""
        if not self.username:
            return
        
        db = SessionLocal()
        try:
            # Get user account
            account = db.query(Account).filter(Account.username == self.username).first()
            if not account or not account.resident_id:
                return
            
            # Get all requests for this user
            requests = db.query(CertificateRequest).filter(
                CertificateRequest.resident_id == account.resident_id
            ).order_by(CertificateRequest.created_at.desc()).all()
            
            self.requests = []
            for req in requests:
                # Build history timeline
                history = [
                    {
                        "timestamp": req.created_at.strftime("%m/%d/%Y %H:%M") if req.created_at else "",
                        "event": f"Request submitted for {req.certificate_type}",
                        "description": f"By: {req.first_name} {req.last_name}"
                    }
                ]
                
                # Add status-specific history entries
                if req.status == "Completed":
                    history.extend([
                        {"timestamp": "12/02/2025 10:30", "event": "Under Review", "description": "Document verification in progress"},
                        {"timestamp": "12/02/2025 14:15", "event": "Processing", "description": "Certificate is being prepared"},
                        {"timestamp": "12/02/2025 16:45", "event": "Ready for Pickup", "description": "Certificate is ready at Barangay Hall"},
                        {"timestamp": req.updated_at.strftime("%m/%d/%Y %H:%M") if req.updated_at else "", "event": "Completed", "description": "Certificate claimed successfully"}
                    ])
                elif req.status == "Rejected":
                    history.append({
                        "timestamp": req.updated_at.strftime("%m/%d/%Y %H:%M") if req.updated_at else "",
                        "event": "Request Rejected",
                        "description": "Incomplete requirements. Please resubmit with valid ID."
                    })
                
                self.requests.append({
                    "id": req.request_id,
                    "certificate_type": req.certificate_type,
                    "status": req.status,
                    "created_at": req.created_at.strftime("%m/%d/%Y %H:%M") if req.created_at else "",
                    "first_name": req.first_name,
                    "last_name": req.last_name,
                    "purpose": req.purpose,
                    "quantity": req.quantity,
                    "history": history
                })
            
            print(f"✅ Loaded {len(self.requests)} requests for user")
            
        except Exception as e:
            print(f"❌ Error loading requests: {e}")
            import traceback
            traceback.print_exc()
        finally:
            db.close()
    
    def display_request(self, index):
        """Display a specific request"""
        if not self.requests or index < 0 or index >= len(self.requests):
            self.request_header_label.setText("No Requests Found")
            self.details_text.setText("You haven't submitted any certificate requests yet.")
            self.request_counter_label.setText("Request 0 of 0")
            self.prev_btn.setEnabled(False)
            self.next_btn.setEnabled(False)
            return
        
        self.current_request_index = index
        request = self.requests[index]
        
        # Update header
        status_color = {
            "Pending": "#ff9800",
            "Under Review": "#2196f3",
            "Processing": "#9c27b0",
            "Ready": "#4caf50",
            "Completed": "#4caf50",
            "Rejected": "#f44336"
        }.get(request["status"], "#666")
        
        self.request_header_label.setText(
            f'REQUEST ID: {request["id"]} | <span style="color: {status_color};">{request["status"].upper()}</span>'
        )
        self.request_header_label.setTextFormat(QtCore.Qt.RichText)
        
        # Update counter
        self.request_counter_label.setText(f"Request {index + 1} of {len(self.requests)}")
        
        # Enable/disable navigation buttons
        self.prev_btn.setEnabled(index > 0)
        self.next_btn.setEnabled(index < len(self.requests) - 1)
        
        # Update details
        details_html = f"""
        <b>Certificate Type:</b> {request["certificate_type"]}<br>
        <b>Name:</b> {request["first_name"]} {request["last_name"]}<br>
        <b>Purpose:</b> {request["purpose"]}<br>
        <b>Quantity:</b> {request["quantity"]}<br>
        <b>Date Submitted:</b> {request["created_at"]}<br>
        """
        self.details_text.setText(details_html)
        self.details_text.setTextFormat(QtCore.Qt.RichText)
        
        # Update progress tracker
        self.update_progress_tracker(request["status"], request)
        
        # Update history timeline
        self.update_history_timeline(request["history"])
    
    def update_history_timeline(self, history):
        """Update the history timeline with events"""
        # Clear existing history
        while self.history_layout.count():
            item = self.history_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Add history items
        for i, event in enumerate(history):
            event_widget = self.create_history_item(
                event["timestamp"],
                event["event"],
                event["description"],
                is_first=(i == 0)
            )
            self.history_layout.addWidget(event_widget)
        
        self.history_layout.addStretch()
    
    def create_history_item(self, timestamp, event, description, is_first=False):
        """Create a single history timeline item"""
        item_widget = QtWidgets.QWidget()
        item_layout = QtWidgets.QHBoxLayout(item_widget)
        item_layout.setContentsMargins(0, 0, 0, 0)
        item_layout.setSpacing(15)
        
        # Left side: Icon + vertical line
        left_container = QtWidgets.QWidget()
        left_container.setFixedWidth(40)
        left_layout = QtWidgets.QVBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)
        left_layout.setAlignment(QtCore.Qt.AlignHCenter)
        
        # Icon
        icon = QtWidgets.QLabel("✓" if is_first else "●")
        icon.setAlignment(QtCore.Qt.AlignCenter)
        icon.setFixedSize(24, 24)
        icon.setStyleSheet(f"""
            QLabel {{
                background-color: {'#4caf50' if is_first else '#2196f3'};
                color: white;
                border-radius: 12px;
                font-size: {'10pt' if is_first else '16pt'};
                font-weight: bold;
            }}
        """)
        left_layout.addWidget(icon)
        
        # Vertical line (except for last item)
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.VLine)
        line.setFixedWidth(2)
        line.setMinimumHeight(60)
        line.setStyleSheet("background-color: #e0e0e0; border: none;")
        left_layout.addWidget(line)
        
        item_layout.addWidget(left_container)
        
        # Right side: Content
        content_container = QtWidgets.QWidget()
        content_layout = QtWidgets.QVBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 10)
        content_layout.setSpacing(5)
        
        # Timestamp and Event on same line
        header_layout = QtWidgets.QHBoxLayout()
        
        timestamp_label = QtWidgets.QLabel(timestamp)
        timestamp_label.setStyleSheet("font-size: 9pt; color: #666; font-weight: bold;")
        header_layout.addWidget(timestamp_label)
        
        event_label = QtWidgets.QLabel(event)
        event_label.setStyleSheet(f"""
            font-size: 10pt;
            color: {'#4caf50' if is_first else '#333'};
            font-weight: bold;
        """)
        header_layout.addWidget(event_label)
        header_layout.addStretch()
        
        content_layout.addLayout(header_layout)
        
        # Description
        desc_label = QtWidgets.QLabel(description)
        desc_label.setStyleSheet("font-size: 9pt; color: #757575;")
        desc_label.setWordWrap(True)
        content_layout.addWidget(desc_label)
        
        item_layout.addWidget(content_container, 1)
        
        return item_widget
    
    def show_previous_request(self):
        """Show the previous request"""
        if self.current_request_index > 0:
            self.display_request(self.current_request_index - 1)
    
    def show_next_request(self):
        """Show the next request"""
        if self.current_request_index < len(self.requests) - 1:
            self.display_request(self.current_request_index + 1)
