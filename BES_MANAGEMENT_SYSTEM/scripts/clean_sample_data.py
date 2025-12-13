from app.db import SessionLocal
from app.models import CertificateRequest, CertificatePayment

def clean_sample_data():
    db = SessionLocal()
    try:
        # Find requests to delete
        requests_to_delete = db.query(CertificateRequest).filter(
            CertificateRequest.purpose.like("Sample request%")
        ).all()
        
        request_ids = [req.request_id for req in requests_to_delete]
        
        if not request_ids:
            print("No sample data found.")
            return

        # Delete associated payments first
        deleted_payments = db.query(CertificatePayment).filter(
            CertificatePayment.request_id.in_(request_ids)
        ).delete(synchronize_session=False)
        
        print(f"Deleted {deleted_payments} associated payments.")

        # Delete requests
        deleted_requests = db.query(CertificateRequest).filter(
            CertificateRequest.request_id.in_(request_ids)
        ).delete(synchronize_session=False)
        
        db.commit()
        print(f"✅ Deleted {deleted_requests} sample requests.")
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    clean_sample_data()
