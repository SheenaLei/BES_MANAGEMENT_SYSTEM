# app/config.py
from pathlib import Path

BASE_DIR = Path(__file__). resolve().parent.parent

# Database connection
SQLALCHEMY_DATABASE_URI = "mysql+pymysql://barangay_user:StrongPass123! @127.0.0.1:3306/barangay_db"

# SMTP Email Settings (System sender email)
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "barangay.balibago.system@gmail.com"  # System email
SMTP_PASSWORD = "your_16_char_app_password_here"      # Gmail App Password
EMAIL_USE_TLS = True
EMAIL_FROM_NAME = "Barangay Balibago E-Services"

# Dev mode (print OTP to console instead of sending email)
DEV_PRINT_OTP = True  # Set to False in production

# OTP settings
OTP_EXPIRY_SECONDS = 600  # 10 minutes

# File upload settings
UPLOAD_FOLDER = BASE_DIR / "uploads"
MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

# Backup settings
BACKUP_FOLDER = BASE_DIR / "backups"

# QR Code for GCash payment (you can replace with actual image path)
GCASH_QR_IMAGE_PATH = BASE_DIR / "assets" / "gcash_qr.png"
GCASH_NUMBER = "09123456789"
GCASH_NAME = "BARANGAY BALIBAGO"