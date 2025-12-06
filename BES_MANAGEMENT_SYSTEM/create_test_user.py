# create_test_user.py
"""
Create a test user account for testing the user dashboard
"""
from app.db import SessionLocal
from app.models import Account, Resident
from datetime import date

def create_test_user():
    """Create test user account"""
    db = SessionLocal()
    
    try:
        print("\n" + "="*60)
        print("CREATING TEST USER ACCOUNT")
        print("="*60 + "\n")
        
        # Check if there's a resident without an account
        all_residents = db.query(Resident).all()
        
        resident_for_account = None
        for res in all_residents:
            existing_account = db.query(Account).filter(
                Account.resident_id == res.resident_id
            ).first()
            if not existing_account:
                resident_for_account = res
                break
        
        if not resident_for_account:
            # Create a test resident
            print("📝 Creating test resident...")
            resident_for_account = Resident(
                first_name="Juan",
                last_name="Dela Cruz",
                middle_name="Santos",
                gender="Male",
                birth_date=date(1990, 1, 1),
                civil_status="Single",
                barangay="Barangay Balibago",
                municipality="Calatagan",
                contact_number="09123456789"
            )
            db.add(resident_for_account)
            db.flush()
            print(f"✅ Created resident: {resident_for_account.first_name} {resident_for_account.last_name}")
        else:
            print(f"✅ Found resident without account: {resident_for_account.first_name} {resident_for_account.last_name}")
        
        # Check if username 'user' already exists
        existing_user = db.query(Account).filter(Account.username == 'user').first()
        if existing_user:
            print("\n⚠️  Username 'user' already exists!")
            print(f"   Use these credentials to login:")
            print(f"   Username: user")
            print(f"   Password: UserPass123!")
            return
        
        # Create account
        print("\n📝 Creating user account...")
        account = Account(
            resident_id=resident_for_account.resident_id,
            username="user",
            user_role="Resident",
            account_status="Active"
        )
        account.set_password("UserPass123!")
        db.add(account)
        db.commit()
        
        print("\n" + "="*60)
        print("✅ TEST USER ACCOUNT CREATED SUCCESSFULLY!")
        print("="*60)
        print("\n🔑 LOGIN CREDENTIALS:")
        print(f"   Username: user")
        print(f"   Password: UserPass123!")
        print("\n📊 Resident Info:")
        print(f"   Name: {resident_for_account.first_name} {resident_for_account.middle_name or ''} {resident_for_account.last_name}")
        print(f"   Role: Resident")
        print(f"   Status: Active")
        print("\n💡 NEXT STEPS:")
        print("   1. Open the login page")
        print("   2. Enter username: user")
        print("   3. Enter password: UserPass123!")
        print("   4. Enter the OTP from console")
        print("   5. You should see the USER DASHBOARD (sidebarhomee_USER.ui)")
        print("\n" + "="*60 + "\n")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    create_test_user()
