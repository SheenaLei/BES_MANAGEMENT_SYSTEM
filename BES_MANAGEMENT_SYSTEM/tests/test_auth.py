# tests/test_auth.py
import os
import pytest
from app.config import DEV_PRINT_OTP
from app.models import Account, Resident
from app.db import Base, engine, SessionLocal

@pytest.mark.skipif(not os.environ.get("RUN_DB_TESTS"), reason="DB tests disabled")
def test_register_and_otp_flow():
    # create tables in test DB
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        r = Resident(first_name="Test", last_name="User", gender="Other", birthdate="2000-01-01", email="test@example.com")
        db.add(r)
        db.flush()
        acc = Account(resident_id=r.resident_id, username="testuser")
        acc.set_password("password123")
        db.add(acc)
        db.commit()

        # generate OTP (prints in DEV mode)
        from app.auth import generate_and_send_otp, verify_otp
        res = generate_and_send_otp(acc, purpose='login')
        assert res.get("success") is True

        # cannot easily capture printed OTP here; this is scaffold only
    finally:
        db.close()