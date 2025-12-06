# app/auth.py
from datetime import datetime, timedelta
from .db import SessionLocal
from .models import Account, OTP, Resident, Admin, StaffAuditLog, ResidentLog
from .config import OTP_EXPIRY_SECONDS, DEV_PRINT_OTP
from .emailer import Emailer
import secrets


def register_account(resident_obj, username, password, role='Resident'):
    """
    Create a new account for a resident.
    Account status is 'Pending' until admin approves documents.
    """
    db = SessionLocal()
    try:
        account = Account(
            resident_id=resident_obj.resident_id,
            username=username,
            user_role=role,
            account_status='Pending'
        )
        account.set_password(password)
        db.add(account)
        db.commit()
        db.refresh(account)
        return {"success": True, "account": account}
    except Exception as e:
        db.rollback()
        return {"success": False, "error": str(e)}
    finally:
        db.close()


def generate_and_send_otp(account, purpose='login'):
    """
    Generate OTP and send to user's email.
    In DEV mode, prints OTP to console instead.
    """
    db = SessionLocal()
    try:
        # Generate 6-digit code
        code = f"{secrets.randbelow(900000) + 100000}"
        expires = datetime.utcnow() + timedelta(seconds=OTP_EXPIRY_SECONDS)

        # Save OTP to database
        otp = OTP(
            account_id=account.account_id,
            code=code,
            purpose=purpose,
            expires_at=expires
        )
        db.add(otp)
        db.commit()
        db.refresh(otp)

        # DEV MODE: Print to console
        if DEV_PRINT_OTP:
            print(f"\n{'=' * 50}")
            print(f"🔐 [DEV OTP] Username: {account.username}")
            print(f"🔐 Code: {code}")
            print(f"🔐 Purpose: {purpose}")
            print(f"🔐 Expires: {expires}")
            print(f"{'=' * 50}\n")
            # RETURN OTP CODE HERE for GUI display
            return {"success": True, "otp": otp, "otp_code": code}

        # PRODUCTION: Email removed as requested
        # Just return the code (it will be displayed in console or UI if needed)
        return {"success": True, "otp": otp, "otp_code": code}

    except Exception as e:
        db.rollback()
        return {"success": False, "error": str(e)}
    finally:
        db.close()


def verify_otp(account, code):
    """Verify OTP code for account"""
    db = SessionLocal()
    try:
        otp = db.query(OTP).filter(
            OTP.account_id == account.account_id,
            OTP.code == code,
            OTP.is_used == False
        ).order_by(OTP.created_at.desc()).first()

        if not otp:
            return {"success": False, "error": "Invalid OTP code"}

        if otp.expires_at < datetime.utcnow():
            return {"success": False, "error": "OTP has expired"}

        # Mark as used
        otp.is_used = True
        account.last_login = datetime.utcnow()
        
        # LOGGING: Record the login action
        if account.user_role in ['Admin', 'Staff']:
            admin = db.query(Admin).filter(Admin.account_id == account.account_id).first()
            if admin:
                log = StaffAuditLog(
                    admin_id=admin.admin_id,
                    action="Login",
                    description="User logged in via OTP",
                    ip_address="127.0.0.1"
                )
                db.add(log)
        else:
            # Resident
            if account.resident_id:
                log = ResidentLog(
                    resident_id=account.resident_id,
                    action="Login",
                    details="Resident logged in via OTP"
                )
                db.add(log)
        
        db.commit()

        return {"success": True, "message": "OTP verified successfully"}

    except Exception as e:
        db.rollback()
        return {"success": False, "error": str(e)}
    finally:
        db.close()


def reset_password_request(username_or_email):
    """Send OTP for password reset"""
    db = SessionLocal()
    try:
        account = db.query(Account).join(Resident).filter(
            (Account.username == username_or_email) | (Resident.email == username_or_email)
        ).first()

        if not account:
            return {"success": False, "error": "Account not found"}

        result = generate_and_send_otp(account, purpose='password_reset')
        return result

    finally:
        db.close()


def reset_password(account, new_password):
    """Reset account password after OTP verification"""
    db = SessionLocal()
    try:
        acc = db.query(Account).filter_by(account_id=account.account_id).first()
        acc.set_password(new_password)
        db.commit()
        return {"success": True, "message": "Password reset successful"}
    except Exception as e:
        db.rollback()
        return {"success": False, "error": str(e)}
    finally:
        db.close()