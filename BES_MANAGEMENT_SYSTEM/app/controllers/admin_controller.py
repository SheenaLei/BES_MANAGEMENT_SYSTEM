# app/controllers/admin_controller.py
from app.db import SessionLocal
from app.models import DocumentUpload, Resident, StaffAuditLog, Request, Payment, Announcement, Notification
from app.emailer import Emailer
from datetime import datetime

class AdminController:
    @staticmethod
    def list_pending_uploads():
        db = SessionLocal()
        try:
            uploads = db.query(DocumentUpload).filter(DocumentUpload.verified == 'Pending').all()
            return uploads
        finally:
            db.close()

    @staticmethod
    def verify_document(upload_id: int, admin_account_id: int, decision: str, reason: str = None):
        """
        decision: 'Approved' or 'Rejected'
        """
        db = SessionLocal()
        try:
            upload = db.query(DocumentUpload).filter(DocumentUpload.upload_id == upload_id).first()
            if not upload:
                return {"success": False, "error": "Upload not found"}
            upload.verified = 'Approved' if decision == 'Approved' else 'Rejected'
            upload.verifier_admin_id = admin_account_id
            upload.verifier_reason = reason
            db.commit()

            # Send email to resident
            resident = db.query(Resident).filter(Resident.resident_id == upload.resident_id).first()
            if upload.verified == 'Approved':
                Emailer.send_document_approved_email(resident.email, resident.first_name)
            else:
                Emailer.send_document_rejected_email(resident.email, resident.first_name, reason or "Not specified")

            # write staff audit log
            log = StaffAuditLog(
                admin_id=admin_account_id,
                action="Verify Document",
                description=f"Upload {upload.upload_id} marked {upload.verified} by admin {admin_account_id}",
                created_at=datetime.utcnow()
            )
            db.add(log)
            db.commit()
            return {"success": True}
        except Exception as e:
            db.rollback()
            return {"success": False, "error": str(e)}
        finally:
            db.close()

    @staticmethod
    def update_request_status(request_id: int, admin_account_id: int, new_status: str, pickup_datetime: datetime = None):
        db = SessionLocal()
        try:
            req = db.query(Request).filter(Request.request_id == request_id).first()
            if not req:
                return {"success": False, "error": "Request not found"}
            req.status = new_status
            if pickup_datetime:
                req.pickup_datetime = pickup_datetime
            db.commit()

            # notify user
            resident = db.query(Resident).filter(Resident.resident_id == req.resident_id).first()
            Emailer.send_request_status_update_email(resident.email, resident.first_name, "Service", new_status)
            # audit
            alog = StaffAuditLog(
                admin_id=admin_account_id,
                action="Update Request Status",
                description=f"Request {request_id} set to {new_status}",
                created_at=datetime.utcnow()
            )
            db.add(alog)
            db.commit()
            return {"success": True}
        except Exception as e:
            db.rollback()
            return {"success": False, "error": str(e)}
        finally:
            db.close()