from datetime import datetime
from sqlalchemy import Column, Integer, BigInteger, String, Date, DateTime, Boolean, Text, ForeignKey, Enum, JSON, \
    DECIMAL
from sqlalchemy.orm import relationship
from .db import Base
from passlib.hash import pbkdf2_sha256


class Resident(Base):
    __tablename__ = "residents"

    resident_id = Column(BigInteger, primary_key=True, autoincrement=True)
    first_name = Column(String(100), nullable=False)
    middle_name = Column(String(100))
    last_name = Column(String(100), nullable=False)
    suffix = Column(String(20))
    gender = Column(Enum('Male', 'Female', 'Other'), nullable=False)
    birthdate = Column(Date, nullable=False)
    age = Column(Integer)
    civil_status = Column(Enum('Single', 'Married', 'Widowed', 'Separated'), default='Single')
    occupation = Column(String(150))
    is_registered_voter = Column(Boolean, default=False)
    phone_number = Column(String(25))
    email = Column(String(255), unique=True)
    purok_zone = Column(String(100))
    barangay = Column(String(100), default='Barangay Balibago')
    date_of_residency = Column(Date)
    resident_status = Column(Enum('Permanent', 'Temporary', 'Boarder'), default='Permanent')
    remarks_set = Column(JSON)  # ["Senior Citizen", "PWD", "4Ps", "Voter", "Minor"]
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    account = relationship("Account", uselist=False, back_populates="resident")

    def full_name(self):
        """Encapsulation: Get full name"""
        parts = [self.first_name, self.middle_name, self.last_name, self.suffix]
        return " ".join([p for p in parts if p])

    def get_remarks(self):
        """Get remarks as list"""
        return self.remarks_set if self.remarks_set else []


class Account(Base):
    __tablename__ = "accounts"

    account_id = Column(BigInteger, primary_key=True, autoincrement=True)
    resident_id = Column(BigInteger, ForeignKey('residents.resident_id'))
    username = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    user_role = Column(Enum('Resident', 'Staff', 'Admin'), default='Resident')
    account_status = Column(Enum('Active', 'Deactivated', 'Pending'), default='Pending')
    last_login = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

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
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class OTP(Base):
    __tablename__ = "otps"

    otp_id = Column(BigInteger, primary_key=True, autoincrement=True)
    account_id = Column(BigInteger, ForeignKey('accounts.account_id'))
    code = Column(String(10))
    purpose = Column(Enum('login', 'password_reset', 'email_verification'), default='login')
    expires_at = Column(DateTime)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def is_valid(self):
        """Check if OTP is still valid"""
        return (not self.is_used) and (self.expires_at >= datetime.utcnow())


class DocumentUpload(Base):
    __tablename__ = "document_uploads"

    upload_id = Column(BigInteger, primary_key=True, autoincrement=True)
    resident_id = Column(BigInteger, ForeignKey('residents.resident_id'), nullable=False)
    request_id = Column(BigInteger)
    doc_type = Column(Enum('PSA', 'Birth Certificate', 'ID', 'PaymentProof', 'Other'), nullable=False)
    id_type = Column(String(100))  # National ID, Voter's ID, etc.
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
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
    created_at = Column(DateTime, default=datetime.utcnow)


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
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    pickup_datetime = Column(DateTime)


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
    created_at = Column(DateTime, default=datetime.utcnow)


class Announcement(Base):
    __tablename__ = "announcements"

    announcement_id = Column(BigInteger, primary_key=True, autoincrement=True)
    title = Column(String(255))
    content = Column(Text)
    posted_by_admin_id = Column(BigInteger)
    posted_at = Column(DateTime, default=datetime.utcnow)
    visible = Column(Boolean, default=True)


class Blotter(Base):
    __tablename__ = "blotters"

    blotter_id = Column(BigInteger, primary_key=True, autoincrement=True)
    complainant_name = Column(String(255))
    respondent_name = Column(String(255))
    incident_date = Column(Date)
    summary = Column(Text)
    posted_by_admin_id = Column(BigInteger)
    created_at = Column(DateTime, default=datetime.utcnow)


class Notification(Base):
    __tablename__ = "notifications"

    notification_id = Column(BigInteger, primary_key=True, autoincrement=True)
    resident_id = Column(BigInteger)
    title = Column(String(255))
    message = Column(Text)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class StaffAuditLog(Base):
    __tablename__ = "staff_audit_logs"

    log_id = Column(BigInteger, primary_key=True, autoincrement=True)
    admin_id = Column(BigInteger)
    action = Column(String(255))
    description = Column(Text)
    ip_address = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)


class ResidentLog(Base):
    __tablename__ = "resident_logs"

    log_id = Column(BigInteger, primary_key=True, autoincrement=True)
    resident_id = Column(BigInteger, ForeignKey('residents.resident_id'))
    request_id = Column(BigInteger)
    action_time = Column(DateTime, default=datetime.utcnow)
    action = Column(String(255))
    details = Column(Text)


class Backup(Base):
    __tablename__ = "backups"

    backup_id = Column(BigInteger, primary_key=True, autoincrement=True)
    filename = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by_admin_id = Column(BigInteger)