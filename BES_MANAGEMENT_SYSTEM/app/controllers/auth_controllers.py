# app/controllers/auth_controller.py
from app.db import SessionLocal
from app.models import Account, Resident, DocumentUpload
from app.auth import generate_and_send_otp, register_account, verify_otp
from app.emailer import Emailer
from sqlalchemy.exc import IntegrityError
import shutil
from pathlib import Path
from app.config import UPLOAD_FOLDER

UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

class AuthController:
    @staticmethod
    def register_resident(personal_info: dict, files: list):
        """
        personal_info: dict with resident fields (first_name, last_name, birthdate, email, etc.)
        files: list of dicts: [{"path": "/local/path/to/file", "doc_type":"PSA" or "ID", "id_type":"National ID"}]
        Flow:
          - create resident row
          - save uploaded files into uploads/ and create DocumentUpload rows with verified='Pending'
          - return resident object or error
        """
        db = SessionLocal()
        try:
            # create resident
            resident = Resident(
                first_name=personal_info.get("first_name"),
                middle_name=personal_info.get("middle_name"),
                last_name=personal_info.get("last_name"),
                suffix=personal_info.get("suffix"),
                gender=personal_info.get("gender"),
                birthdate=personal_info.get("birthdate"),
                civil_status=personal_info.get("civil_status"),
                occupation=personal_info.get("occupation"),
                is_registered_voter=personal_info.get("is_registered_voter", False),
                phone_number=personal_info.get("phone_number"),
                email=personal_info.get("email"),
                purok_zone=personal_info.get("purok_zone"),
                barangay=personal_info.get("barangay", "Barangay Balibago"),
                date_of_residency=personal_info.get("date_of_residency"),
                resident_status=personal_info.get("resident_status", "Permanent"),
                remarks_set=personal_info.get("remarks_set", [])
            )
            db.add(resident)
            db.flush()  # to get resident_id

            # handle files
            saved_uploads = []
            for f in files:
                src = Path(f["path"])
                if not src.exists():
                    continue
                dest_name = f"{resident.resident_id}_{src.name}"
                dest = UPLOAD_FOLDER / dest_name
                shutil.copy(src, dest)
                upload = DocumentUpload(
                    resident_id=resident.resident_id,
                    doc_type=f.get("doc_type", "Other"),
                    id_type=f.get("id_type"),
                    filename=src.name,
                    file_path=str(dest),
                    verified='Pending'
                )
                db.add(upload)
                saved_uploads.append(upload)

            db.commit()
            # refresh resident
            db.refresh(resident)
            return {"success": True, "resident": resident, "uploads": saved_uploads}
        except IntegrityError as e:
            db.rollback()
            return {"success": False, "error": "Integrity error: " + str(e)}
        except Exception as e:
            db.rollback()
            return {"success": False, "error": str(e)}
        finally:
            db.close()

    @staticmethod
    def start_login(username: str, password: str):
        """
        Validate username/password and generate OTP (2FA).
        """
        db = SessionLocal()
        try:
            account = db.query(Account).filter(Account.username == username).first()
            if not account:
                return {"success": False, "error": "Account not found"}
            if not account.verify_password(password):
                return {"success": False, "error": "Invalid credentials"}
            # generate and send OTP
            res = generate_and_send_otp(account, purpose='login')
            if res.get("success"):
                return {"success": True, "message": "OTP sent"}
            return {"success": False, "error": res.get("error", "Failed to generate OTP")}
        finally:
            db.close()

    @staticmethod
    def verify_login_otp(username: str, code: str):
        db = SessionLocal()
        try:
            account = db.query(Account).filter(Account.username == username).first()
            if not account:
                return {"success": False, "error": "Account not found"}
            res = verify_otp(account, code)
            return res
        finally:
            db.close()

    @staticmethod
    def create_account_after_verification(resident_id: int, username: str, password: str):
        """
        Called when admin approves user's documents and instructs user to create an account.
        """
        db = SessionLocal()
        try:
            resident = db.query(Resident).filter(Resident.resident_id == resident_id).first()
            if not resident:
                return {"success": False, "error": "Resident not found"}
            # create account
            account = Account(resident_id=resident.resident_id, username=username, account_status='Active', user_role='Resident')
            account.set_password(password)
            db.add(account)
            db.commit()
            db.refresh(account)
            # send welcome email
            Emailer.send_email(resident.email, "Account Created", f"Good day {resident.full_name()}! Your account has been created. You can now log in.")
            return {"success": True, "account": account}
        except IntegrityError:
            db.rollback()
            return {"success": False, "error": "Username or email already exists"}
        except Exception as e:
            db.rollback()
            return {"success": False, "error": str(e)}
        finally:
            db.close()