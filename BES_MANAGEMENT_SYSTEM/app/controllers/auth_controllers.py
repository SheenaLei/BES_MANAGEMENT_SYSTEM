# app/controllers/auth_controller.py
from app.db import SessionLocal
from app.models import Account, Resident, DocumentUpload
from app.auth import generate_and_send_otp, register_account, verify_otp
from app.emailer import Emailer
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import shutil
from pathlib import Path
from app.config import UPLOAD_FOLDER

UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

class AuthController:
    @staticmethod
    def register_resident(personal_info: dict, files: list):
        """
        personal_info: dict with resident fields (first_name, last_name, birthdate, etc.)
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
                birth_date=personal_info.get("birthdate"),
                civil_status=personal_info.get("civil_status"),
                occupation=personal_info.get("occupation"),
                registered_voter=personal_info.get("is_registered_voter", False),
                contact_number=personal_info.get("phone_number"),
                sitio=personal_info.get("purok_zone"),
                barangay=personal_info.get("barangay", "Barangay Balibago"),
                municipality=personal_info.get("municipality", "Calatagan"),
                nationality=personal_info.get("nationality", "Filipino"),
                religion=personal_info.get("religion"),
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
    def register_account(username: str, password: str, full_name: str):
        """
        Simple account registration for GUI.
        Creates a basic resident record and account.
        Account is created as 'Pending' until admin registers at Barangay Hall.
        NO EMAIL REQUIRED.
        """
        db = SessionLocal()
        try:
            # Check if username already exists
            existing_account = db.query(Account).filter(Account.username == username).first()
            if existing_account:
                return {"success": False, "error": "Username already exists"}
            
            # Parse full name (simple parsing)
            name_parts = full_name.strip().split()
            first_name = name_parts[0] if len(name_parts) > 0 else ""
            last_name = name_parts[-1] if len(name_parts) > 1 else ""
            middle_name = " ".join(name_parts[1:-1]) if len(name_parts) > 2 else ""
            
            # Create resident record (minimal required fields - NO EMAIL)
            resident = Resident(
                first_name=first_name,
                middle_name=middle_name,
                last_name=last_name,
                gender='Male',  # Default, will be updated by admin
                birth_date=datetime.utcnow().date(),  # Placeholder, will be updated by admin
                civil_status='Single',  # Default, will be updated by admin
                barangay="Barangay Balibago",
                municipality="Calatagan"
            )
            db.add(resident)
            db.flush()  # Get resident_id
            
            # Create account with PENDING status
            account = Account(
                resident_id=resident.resident_id,
                username=username,
                user_role='Resident',
                account_status='Pending'  # Pending until admin registers at Barangay Hall
            )
            account.set_password(password)
            db.add(account)
            db.commit()
            
            db.refresh(account)
            db.refresh(resident)
            
            return {"success": True, "account": account, "resident": resident}
            
        except IntegrityError as e:
            db.rollback()
            return {"success": False, "error": "Username already exists"}
        except Exception as e:
            db.rollback()
            return {"success": False, "error": str(e)}
        finally:
            db.close()

    @staticmethod
    def start_login(username: str, password: str):
        """
        Validate username/password and check account status.
        Block login if account is 'Pending' (not yet registered at Barangay Hall).
        """
        db = SessionLocal()
        try:
            account = db.query(Account).filter(Account.username == username).first()
            if not account:
                return {"success": False, "error": "Account not found"}
            if not account.verify_password(password):
                return {"success": False, "error": "Invalid credentials"}
            
            # CHECK ACCOUNT STATUS - Block if Pending
            if account.account_status == 'Pending':
                return {
                    "success": False, 
                    "error": "Your account is pending approval. Please visit the Barangay Hall to complete your registration."
                }
            
            # CHECK ACCOUNT STATUS - Block if Inactive
            if account.account_status != 'Active':
                return {
                    "success": False, 
                    "error": f"Account is {account.account_status}. Please contact the Barangay Hall."
                }
            
            # generate and send OTP
            res = generate_and_send_otp(account, purpose='login')
            if res.get("success"):
                # Pass the OTP code back to the view
                return {
                    "success": True, 
                    "message": "OTP sent", 
                    "otp_code": res.get("otp_code")
                }
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
            return {"success": True, "account": account}
        except IntegrityError:
            db.rollback()
            return {"success": False, "error": "Username already exists"}
        except Exception as e:
            db.rollback()
            return {"success": False, "error": str(e)}
        finally:
            db.close()
    
    @staticmethod
    def approve_account(account_id: int):
        """
        Called by admin to approve a pending account after registering at Barangay Hall.
        Changes account status from 'Pending' to 'Active'.
        """
        db = SessionLocal()
        try:
            account = db.query(Account).filter(Account.account_id == account_id).first()
            if not account:
                return {"success": False, "error": "Account not found"}
            
            account.account_status = 'Active'
            db.commit()
            db.refresh(account)
            
            return {"success": True, "account": account, "message": "Account approved successfully"}
        except Exception as e:
            db.rollback()
            return {"success": False, "error": str(e)}
        finally:
            db.close()