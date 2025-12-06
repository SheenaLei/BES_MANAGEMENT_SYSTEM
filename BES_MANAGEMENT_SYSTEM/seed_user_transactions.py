"""
Seed user transaction data for dashboard testing
"""
from app.db import SessionLocal
from app.models import CertificateRequest, Account, Resident
from app.config import get_philippine_time
from datetime import datetime, timedelta
import random

def seed_transactions():
    """Add sample certificate requests to database"""
    db = SessionLocal()
    
    try:
        # Find the first account (default test user)
        account = db.query(Account).first()
        if not account:
            print("❌ No account found. Please create an account first.")
            return
        
        # Get resident associated with account
        resident = account.resident
        if not resident:
            print("❌ Account has no associated resident.")
            return
        
        resident_id = resident.resident_id
        print(f"📊 Using resident: {resident.first_name} {resident.last_name} (ID: {resident_id})")
        
        # Sample data
        cert_types = [
            "Barangay ID",
            "Barangay Indigency",
            "Barangay Clearance",
            "Business Permit"
        ]
        
        statuses = ["Pending", "Completed", "Declined", "Processing"]
        
        # Count existing data for this resident
        existing = db.query(CertificateRequest).filter(
            CertificateRequest.resident_id == resident_id
        ).all()
        print(f"Found {len(existing)} existing requests for this resident")
        
        # Create sample transactions for the past 3 months
        today = datetime.now().date()
        start_date = today - timedelta(days=90)
        
        sample_requests = []
        
        # Generate 30 sample requests with distribution
        cert_count = {
            "Barangay ID": 8,
            "Barangay Indigency": 10,
            "Barangay Clearance": 7,
            "Business Permit": 5
        }
        
        status_distribution = {
            "Pending": 8,
            "Completed": 12,
            "Declined": 2,
            "Processing": 8
        }
        
        cert_idx = 0
        status_idx = 0
        
        for i in range(30):
            # Random date within the last 90 days
            days_offset = random.randint(0, 90)
            request_date = start_date + timedelta(days=days_offset)
            
            # Distribute cert types
            cert_types_list = []
            for ctype, count in cert_count.items():
                cert_types_list.extend([ctype] * count)
            cert_type = cert_types_list[i % len(cert_types_list)]
            
            # Distribute statuses
            statuses_list = []
            for status, count in status_distribution.items():
                statuses_list.extend([status] * count)
            status = statuses_list[i % len(statuses_list)]
            
            req = CertificateRequest(
                resident_id=resident_id,
                certificate_type=cert_type,
                status=status,
                created_at=datetime.combine(request_date, datetime.min.time()),
                updated_at=datetime.combine(request_date, datetime.min.time()),
                purpose=f"Sample request for {cert_type}",
                first_name=resident.first_name,
                last_name=resident.last_name,
                phone_number="09123456789"
            )
            sample_requests.append(req)
        
        # Add all to database
        db.add_all(sample_requests)
        db.commit()
        
        print(f"\n✅ Successfully added {len(sample_requests)} sample transactions!")
        
        # Display summary by certificate type
        print("\n📋 Certificate Type Breakdown:")
        for cert_type in cert_types:
            count = db.query(CertificateRequest).filter(
                CertificateRequest.resident_id == resident_id,
                CertificateRequest.certificate_type == cert_type
            ).count()
            print(f"  - {cert_type}: {count}")
        
        print("\n📊 Status Breakdown:")
        for status in ["Pending", "Completed", "Declined", "Processing"]:
            count = db.query(CertificateRequest).filter(
                CertificateRequest.resident_id == resident_id,
                CertificateRequest.status == status
            ).count()
            print(f"  - {status}: {count}")
        
        total = db.query(CertificateRequest).filter(
            CertificateRequest.resident_id == resident_id
        ).count()
        print(f"\n📈 Total transactions: {total}")
        
    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🌱 Seeding user transaction data for dashboard testing...\n")
    seed_transactions()
    print("\n✅ Done!")
