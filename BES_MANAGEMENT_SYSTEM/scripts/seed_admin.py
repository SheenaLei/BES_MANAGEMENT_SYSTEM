# scripts/seed_admin.py
import sys
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

from app.db import engine, Base, SessionLocal
from app.models import Resident, Account, Service
from sqlalchemy.exc import IntegrityError

def seed():
    # create tables if not exist
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # seed admin resident/account
        existing = db.query(Account).filter(Account.username == 'admin').first()
        if existing:
            print("Admin already exists.")
            return

        r = Resident(
            first_name="Barangay",
            middle_name="",
            last_name="Captain",
            gender="Male",
            birthdate="1970-01-01",
            email="captain@balibago.local",
            phone_number="09170000000",
            purok_zone="Purok 1"
        )
        db.add(r)
        db.flush()

        acc = Account(
            resident_id=r.resident_id,
            username="admin",
            user_role="Admin",
            account_status="Active"
        )
        acc.set_password("AdminPass123!")
        db.add(acc)

        services = [
            Service(name="Barangay Clearance", description="For employment", fee=25.00),
            Service(name="Certificate of Indigency", description="Indigency certificate", fee=0.00),
            Service(name="Barangay ID", description="Barangay identification card", fee=50.00)
        ]
        db.add_all(services)
        db.commit()
        print("Seed complete: admin created (username=admin password=AdminPass123!)")
    except IntegrityError as e:
        db.rollback()
        print("Seed error:", e)
    finally:
        db.close()

if __name__ == "__main__":
    seed()