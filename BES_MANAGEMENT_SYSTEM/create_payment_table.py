"""
Create the certificate_payments table in the database
"""
from app.db import engine, Base
from app.models import CertificatePayment

def create_payment_table():
    """Create the certificate_payments table if it doesn't exist"""
    try:
        # Create only the CertificatePayment table
        CertificatePayment.__table__.create(engine, checkfirst=True)
        print("✅ certificate_payments table created successfully!")
    except Exception as e:
        print(f"❌ Error creating table: {e}")

if __name__ == "__main__":
    create_payment_table()
