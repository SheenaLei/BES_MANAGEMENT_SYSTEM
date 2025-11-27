# app/controllers/request_controller.py
from app.db import SessionLocal
from app.models import Request, Service, DocumentUpload, Payment, Resident, ResidentLog
from app.emailer import Emailer
from datetime import datetime

class RequestController:
    @staticmethod
    def list_services():
        db = SessionLocal()
        try:
            services = db.query(Service).all()
            return services
        finally:
            db.close()

    @staticmethod
    def create_request(resident_id: int, service_id: int, fields: dict, payment_method: str = 'None', payment_proof_path: str = None):
        db = SessionLocal()
        try:
            service = db.query(Service).filter(Service.service_id == service_id).first()
            if not service:
                return {"success": False, "error": "Service not found"}

            req = Request(
                resident_id=resident_id,
                service_id=service_id,
                purpose=fields.get("purpose"),
                fields=fields,
                payment_method=payment_method,
                fee_amount=float(service.fee or 0.0),
                status='Payment Pending' if payment_method == 'GCash' and service.fee > 0 else 'Pending',
                created_at=datetime.utcnow()
            )
            db.add(req)
            db.flush()

            # if payment proof provided, save DocumentUpload
            if payment_proof_path:
                du = DocumentUpload(
                    resident_id=resident_id,
                    request_id=req.request_id,
                    doc_type='PaymentProof',
                    filename=payment_proof_path.split("/")[-1],
                    file_path=payment_proof_path,
                    verified='Pending'
                )
                db.add(du)
                db.flush()
                req.payment_proof_upload_id = du.upload_id

            # resident log
            rlog = ResidentLog(
                resident_id=resident_id,
                request_id=req.request_id,
                action="Submitted request",
                details=f"Service: {service.name}"
            )
            db.add(rlog)
            db.commit()
            db.refresh(req)
            return {"success": True, "request": req}
        except Exception as e:
            db.rollback()
            return {"success": False, "error": str(e)}
        finally:
            db.close()

    @staticmethod
    def upload_payment_proof(request_id: int, resident_id: int, src_path: str):
        # For simplicity assume file already saved to uploads and src_path is path in uploads
        db = SessionLocal()
        try:
            upload = DocumentUpload(
                resident_id=resident_id,
                request_id=request_id,
                doc_type='PaymentProof',
                filename=src_path.split("/")[-1],
                file_path=src_path,
                verified='Pending'
            )
            db.add(upload)
            db.flush()
            # attach to request
            req = db.query(Request).filter(Request.request_id == request_id).first()
            req.payment_proof_upload_id = upload.upload_id
            req.status = 'Payment Pending'
            db.commit()
            return {"success": True, "upload": upload}
        except Exception as e:
            db.rollback()
            return {"success": False, "error": str(e)}
        finally:
            db.close()