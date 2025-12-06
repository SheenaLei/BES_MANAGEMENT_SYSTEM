from datetime import datetime
from sqlalchemy import Column, Integer, BigInteger, String, Date, DateTime, Boolean, Text, ForeignKey, Enum, JSON, \
    DECIMAL
from sqlalchemy.orm import relationship
from .db import Base
from passlib.hash import pbkdf2_sha256
from .config import get_philippine_time


class Resident(Base):
    __tablename__ = "residents"

    # Primary Key
    resident_id = Column(BigInteger, primary_key=True, autoincrement=True)
    
    # Personal Information
    last_name = Column(String(100), nullable=False)
    first_name = Column(String(100), nullable=False)
    middle_name = Column(String(100))
    suffix = Column(String(20))
    
    # Demographics
    gender = Column(Enum('Male', 'Female', 'Other'), nullable=False)
    birth_date = Column(Date, nullable=False)
    birth_place = Column(String(255))
    age = Column(Integer)
    civil_status = Column(Enum('Single', 'Married', 'Widowed', 'Divorced', 'Separated', 'Live-in'), nullable=False)
    
    # Family Information
    spouse_name = Column(String(255))
    no_of_children = Column(Integer, default=0)
    no_of_siblings = Column(Integer, default=0)
    mother_full_name = Column(String(255))
    father_full_name = Column(String(255))
    
    # Personal Details
    nationality = Column(String(100), default='Filipino')
    religion = Column(String(100))
    occupation = Column(String(150))
    highest_educational_attainment = Column(String(100))
    
    # Contact Information
    contact_number = Column(String(20))
    emergency_contact_name = Column(String(255))
    emergency_contact_number = Column(String(20))
    
    # Address Information
    sitio = Column(String(100))
    barangay = Column(String(100), nullable=False)
    municipality = Column(String(100), nullable=False)
    
    # Government Programs & Status
    registered_voter = Column(Boolean, default=False)
    indigent = Column(Boolean, default=False)
    solo_parent = Column(Boolean, default=False)
    solo_parent_id_no = Column(String(50))
    fourps_member = Column(Boolean, default=False)
    
    # Photo
    photo_path = Column(String(500))
    
    # System Timestamps
    created_at = Column(DateTime, default=get_philippine_time)
    updated_at = Column(DateTime, default=get_philippine_time, onupdate=get_philippine_time)

    # Relationships
    account = relationship("Account", uselist=False, back_populates="resident")

    def full_name(self):
        """Encapsulation: Get full name"""
        parts = [self.first_name, self.middle_name, self.last_name, self.suffix]
        return " ".join([p for p in parts if p])

    def get_remarks(self):
        """Get remarks as list (Derived from boolean flags)"""
        remarks = []
        if self.indigent: remarks.append("Indigent")
        if self.solo_parent: remarks.append("Solo Parent")
        if self.fourps_member: remarks.append("4Ps Member")
        if self.registered_voter: remarks.append("Voter")
        return remarks


class Account(Base):
    __tablename__ = "accounts"

    account_id = Column(BigInteger, primary_key=True, autoincrement=True)
    resident_id = Column(BigInteger, ForeignKey('residents.resident_id'))
    username = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    user_role = Column(Enum('Resident', 'Staff', 'Admin'), default='Resident')
    account_status = Column(Enum('Active', 'Deactivated', 'Pending'), default='Pending')
    last_login = Column(DateTime)
    created_at = Column(DateTime, default=get_philippine_time)
    updated_at = Column(DateTime, default=get_philippine_time, onupdate=get_philippine_time)

    # Relationships
    resident = relationship("Resident", back_populates="account")

    def set_password(self, raw_password: str):
        """Encapsulation: Hash and set password"""
        self.password_hash = pbkdf2_sha256.hash(raw_password)

    def verify_password(self, raw_password: str) -> bool:
        """Encapsulation: Verify password"""
        return pbkdf2_sha256.verify(raw_password, self.password_hash)

    def is_admin(self) -> bool:
        """Check if account has admin privileges"""
        return self.user_role in ['Admin', 'Staff']


class Admin(Base):
    __tablename__ = "admins"

    admin_id = Column(BigInteger, primary_key=True, autoincrement=True)
    account_id = Column(BigInteger, ForeignKey('accounts.account_id'))
    username = Column(String(100), unique=True)
    email = Column(String(255))
    phone_number = Column(String(25))
    first_name = Column(String(100))
    middle_name = Column(String(100))
    last_name = Column(String(100))
    position = Column(String(50))  # Captain, Secretary, Treasurer, IT
    created_at = Column(DateTime, default=get_philippine_time)
    updated_at = Column(DateTime, default=get_philippine_time, onupdate=get_philippine_time)


class OTP(Base):
    __tablename__ = "otps"

    otp_id = Column(BigInteger, primary_key=True, autoincrement=True)
    account_id = Column(BigInteger, ForeignKey('accounts.account_id'))
    code = Column(String(10))
    purpose = Column(Enum('login', 'password_reset', 'email_verification'), default='login')
    expires_at = Column(DateTime)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=get_philippine_time)

    def is_valid(self):
        """Check if OTP is still valid"""
        return (not self.is_used) and (self.expires_at >= get_philippine_time())


class DocumentUpload(Base):
    __tablename__ = "document_uploads"

    upload_id = Column(BigInteger, primary_key=True, autoincrement=True)
    resident_id = Column(BigInteger, ForeignKey('residents.resident_id'), nullable=False)
    request_id = Column(BigInteger)
    doc_type = Column(Enum('PSA', 'Birth Certificate', 'ID', 'PaymentProof', 'Other'), nullable=False)
    id_type = Column(String(100))  # National ID, Voter's ID, etc.
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    uploaded_at = Column(DateTime, default=get_philippine_time)
    verified = Column(Enum('Pending', 'Approved', 'Rejected'), default='Pending')
    verifier_admin_id = Column(BigInteger)
    verifier_reason = Column(Text)


class Service(Base):
    __tablename__ = "services"

    service_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(150), nullable=False)
    description = Column(Text)
    fee = Column(DECIMAL(10, 2), default=0.00)
    requires_payment = Column(Boolean, default=True)
    requires_documents = Column(JSON)
    created_at = Column(DateTime, default=get_philippine_time)


class Request(Base):
    __tablename__ = "requests"

    request_id = Column(BigInteger, primary_key=True, autoincrement=True)
    resident_id = Column(BigInteger, ForeignKey('residents.resident_id'), nullable=False)
    service_id = Column(Integer, ForeignKey('services.service_id'), nullable=False)
    purpose = Column(Text)
    fields = Column(JSON)  # Additional form fields
    payment_method = Column(Enum('GCash', 'Cash', 'None'), default='None')
    payment_proof_upload_id = Column(BigInteger)
    status = Column(Enum('Pending', 'Payment Pending', 'Approved', 'Declined', 'Cancelled', 'Completed'),
                    default='Pending')
    fee_amount = Column(DECIMAL(10, 2), default=0.00)
    created_at = Column(DateTime, default=get_philippine_time)
    updated_at = Column(DateTime, default=get_philippine_time, onupdate=get_philippine_time)
    pickup_datetime = Column(DateTime)


# NEW MODEL FOR CERTIFICATE REQUESTS
class CertificateRequest(Base):
    __tablename__ = "certificate_requests"

    request_id = Column(BigInteger, primary_key=True, autoincrement=True)
    resident_id = Column(BigInteger, ForeignKey('residents.resident_id'), nullable=False)
    
    # Request Information
    certificate_type = Column(Enum('Barangay Indigency', 'Barangay Clearance', 'Barangay ID', 'Business Permit'), nullable=False)
    
    # Requestor Details (from form)
    last_name = Column(String(100))
    first_name = Column(String(100))
    middle_name = Column(String(100))
    suffix = Column(String(20))
    phone_number = Column(String(20))
    
    # Request Details
    purpose = Column(String(255))
    quantity = Column(Integer, default=1)
    
    # Upload
    uploaded_file_path = Column(String(500))  # Path to uploaded ID/document
    
    # Status Management - workflow: Pending -> Under Review -> Processing -> Ready for Pickup -> Completed (or Declined)
    status = Column(String(50), default='Pending')  # Pending, Under Review, Processing, Ready for Pickup, Completed, Declined
    
    # Timestamps
    created_at = Column(DateTime, default=get_philippine_time)
    updated_at = Column(DateTime, default=get_philippine_time, onupdate=get_philippine_time)
    reviewed_by_admin_id = Column(BigInteger)
    reviewed_at = Column(DateTime)
    
    # Relationship
    resident = relationship("Resident", backref="certificate_requests")


class CertificatePayment(Base):
    """Payment records for certificate requests - payments made at Barangay Hall or online"""
    __tablename__ = "certificate_payments"

    payment_id = Column(BigInteger, primary_key=True, autoincrement=True)
    request_id = Column(BigInteger, ForeignKey('certificate_requests.request_id'), nullable=False)
    resident_id = Column(BigInteger, ForeignKey('residents.resident_id'))
    
    # Certificate details (copied from request for easy display)
    certificate_type = Column(String(100))
    requestor_name = Column(String(255))
    
    # Payment details
    quantity = Column(Integer, default=1)
    unit_price = Column(DECIMAL(10, 2), default=0.00)  # Price per certificate
    total_amount = Column(DECIMAL(10, 2), default=0.00)  # quantity * unit_price
    
    # Payment status
    is_paid = Column(Boolean, default=False)
    payment_method = Column(String(50), default='Cash')  # Cash, GCash, etc.
    
    # Admin verification
    received_by_admin_id = Column(BigInteger)
    received_at = Column(DateTime)
    or_number = Column(String(50))  # Official Receipt number (for cash payments)
    reference_number = Column(String(100))  # Reference/Transaction number (for online payments like GCash)
    
    # Timestamps
    created_at = Column(DateTime, default=get_philippine_time)
    updated_at = Column(DateTime, default=get_philippine_time, onupdate=get_philippine_time)
    
    # Relationships
    certificate_request = relationship("CertificateRequest", backref="payment")
    resident = relationship("Resident", backref="certificate_payments")


class Payment(Base):
    __tablename__ = "payments"

    payment_id = Column(BigInteger, primary_key=True, autoincrement=True)
    request_id = Column(BigInteger, ForeignKey('requests.request_id'))
    resident_id = Column(BigInteger)
    amount = Column(DECIMAL(10, 2))
    method = Column(Enum('GCash', 'Cash'), default='Cash')
    proof_upload_id = Column(BigInteger)
    status = Column(Enum('Pending', 'Verified', 'Rejected'), default='Pending')
    verified_by_admin_id = Column(BigInteger)
    verified_at = Column(DateTime)
    created_at = Column(DateTime, default=get_philippine_time)


class Announcement(Base):
    __tablename__ = "announcements"

    announcement_id = Column(BigInteger, primary_key=True, autoincrement=True)
    title = Column(String(255))
    content = Column(Text)
    image_path = Column(String(500))  # Path to announcement image
    posted_by_admin_id = Column(BigInteger)
    posted_at = Column(DateTime, default=get_philippine_time)
    visible = Column(Boolean, default=True)


class Blotter(Base):
    __tablename__ = "blotters"

    blotter_id = Column(BigInteger, primary_key=True, autoincrement=True)
    complainant_name = Column(String(255))
    respondent_name = Column(String(255))
    reason = Column(Text)
    incident_date = Column(DateTime)
    location = Column(String(255))
    handled_by = Column(String(255))
    posted_by_admin_id = Column(BigInteger)
    created_at = Column(DateTime, default=get_philippine_time)


class Notification(Base):
    __tablename__ = "notifications"

    notification_id = Column(BigInteger, primary_key=True, autoincrement=True)
    resident_id = Column(BigInteger)
    title = Column(String(255))
    message = Column(Text)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=get_philippine_time)


class StaffAuditLog(Base):
    __tablename__ = "staff_audit_logs"

    log_id = Column(BigInteger, primary_key=True, autoincrement=True)
    admin_id = Column(BigInteger)
    action = Column(String(255))
    description = Column(Text)
    ip_address = Column(String(50))
    created_at = Column(DateTime, default=get_philippine_time)


class ResidentLog(Base):
    __tablename__ = "resident_logs"

    log_id = Column(BigInteger, primary_key=True, autoincrement=True)
    resident_id = Column(BigInteger, ForeignKey('residents.resident_id'))
    request_id = Column(BigInteger)
    action_time = Column(DateTime, default=get_philippine_time)
    action = Column(String(255))
    details = Column(Text)


class Backup(Base):
    __tablename__ = "backups"

    backup_id = Column(BigInteger, primary_key=True, autoincrement=True)
    filename = Column(String(500))
    created_at = Column(DateTime, default=get_philippine_time)
    created_by_admin_id = Column(BigInteger)


class BarangayOfficial(Base):
    """Model for Barangay Officials - editable by admin, viewable by users"""
    __tablename__ = "barangay_officials"

    official_id = Column(BigInteger, primary_key=True, autoincrement=True)
    position = Column(String(100), nullable=False)  # Punong Barangay, Kagawad, SK Chairman, Secretary, Treasurer
    full_name = Column(String(255), nullable=False)
    photo_path = Column(String(500))  # Path to official's photo
    display_order = Column(Integer, default=0)  # For ordering officials on display
    category = Column(String(50), default='Sanggunian')  # Sanggunian, Other
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=get_philippine_time)
    updated_at = Column(DateTime, default=get_philippine_time, onupdate=get_philippine_time)