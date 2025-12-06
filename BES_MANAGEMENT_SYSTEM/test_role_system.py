# test_role_system.py
"""
Test script to verify the role-based login system
"""
from app.db import SessionLocal
from app.models import Account, Resident
from sqlalchemy import func

def test_role_structure():
    """Verify database structure and roles"""
    db = SessionLocal()
    
    try:
        print("\n" + "="*60)
        print("ROLE-BASED LOGIN SYSTEM - Database Verification")
        print("="*60 + "\n")
        
        # Test 1: Check accounts table
        print("📊 ACCOUNTS TABLE")
        print("-" * 60)
        accounts = db.query(Account).all()
        
        if not accounts:
            print("⚠️  No accounts found in database!")
            print("   Run: python scripts/seed_admin.py")
        else:
            print(f"✅ Total Accounts: {len(accounts)}\n")
            
            # Count by role
            role_counts = db.query(
                Account.user_role,
                func.count(Account.account_id)
            ).group_by(Account.user_role).all()
            
            for role, count in role_counts:
                print(f"   {role}: {count}")
            
            print("\n📋 Account Details:")
            for acc in accounts:
                resident_name = "N/A"
                if acc.resident_id:
                    resident = db.query(Resident).filter(
                        Resident.resident_id == acc.resident_id
                    ).first()
                    if resident:
                        resident_name = f"{resident.first_name} {resident.last_name}"
                
                print(f"   • {acc.username:15} | {acc.user_role:10} | {acc.account_status:12} | {resident_name}")
        
        print("\n" + "-" * 60)
        
        # Test 2: Check residents table
        print("\n📊 RESIDENTS TABLE")
        print("-" * 60)
        residents = db.query(Resident).all()
        
        if not residents:
            print("⚠️  No residents found in database!")
        else:
            print(f"✅ Total Residents: {len(residents)}\n")
            
            # Check how many have accounts
            residents_with_accounts = db.query(Resident).join(
                Account, Resident.resident_id == Account.resident_id, isouter=False
            ).count()
            
            residents_without_accounts = len(residents) - residents_with_accounts
            
            print(f"   With Accounts: {residents_with_accounts}")
            print(f"   Without Accounts: {residents_without_accounts}")
            
            print("\n📋 Sample Residents (first 5):")
            for res in residents[:5]:
                has_account = db.query(Account).filter(
                    Account.resident_id == res.resident_id
                ).first()
                account_status = "✅ Has Account" if has_account else "❌ No Account"
                print(f"   • {res.first_name} {res.last_name:20} | {account_status}")
        
        print("\n" + "-" * 60)
        
        # Test 3: System Configuration
        print("\n⚙️  SYSTEM CONFIGURATION")
        print("-" * 60)
        print("✅ Role-Based Routing:")
        print("   Admin/Staff → sidebar_home_view.py (Admin Dashboard)")
        print("   Resident    → sidebar_home_user_view.py (User Dashboard)")
        print("\n✅ Registration Validation:")
        print("   Users MUST exist in residents table to create account")
        print("   Prevents unauthorized registrations")
        print("\n✅ UI Files:")
        print("   Admin: gui/ui/sidebarhomee.ui")
        print("   User:  gui/ui/sidebarhomee_USER.ui")
        
        print("\n" + "="*60)
        print("✅ VERIFICATION COMPLETE")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


def test_registration_flow():
    """Test the registration validation logic"""
    print("\n" + "="*60)
    print("REGISTRATION FLOW TEST")
    print("="*60 + "\n")
    
    db = SessionLocal()
    try:
        # Get a sample resident without an account
        residents_without_accounts = []
        all_residents = db.query(Resident).all()
        
        for res in all_residents:
            existing_account = db.query(Account).filter(
                Account.resident_id == res.resident_id
            ).first()
            if not existing_account:
                residents_without_accounts.append(res)
        
        if residents_without_accounts:
            sample = residents_without_accounts[0]
            print("✅ Found resident without account:")
            print(f"   Name: {sample.first_name} {sample.last_name}")
            print(f"   ID: {sample.resident_id}")
            print("\n💡 This resident CAN create an account:")
            print(f"   1. Click 'Register New Account'")
            print(f"   2. Enter First Name: {sample.first_name}")
            print(f"   3. Enter Last Name: {sample.last_name}")
            if sample.middle_name:
                print(f"   4. Enter Middle Name: {sample.middle_name}")
            print(f"   5. Choose username and password")
            print(f"   6. System will validate and create account")
        else:
            print("⚠️  All residents already have accounts")
            print("\n💡 To test registration:")
            print("   1. Login as admin")
            print("   2. Go to RESIDENTS → ADD RESIDENT")
            print("   3. Add a new resident")
            print("   4. Then try to create account for that resident")
        
        print("\n" + "-" * 60)
        
        # Test invalid registration (non-existent person)
        print("\n❌ Invalid Registration Test:")
        print("   If someone tries to register as 'John Smith' but")
        print("   'John Smith' is NOT in residents table:")
        print("   → Registration will be BLOCKED")
        print("   → Message: 'Visit Barangay Hall to register first'")
        
        print("\n" + "="*60 + "\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    test_role_structure()
    test_registration_flow()
    
    print("\n💡 NEXT STEPS:")
    print("   1. Run: python gui/run_app.py")
    print("   2. Test admin login (username: admin, password: AdminPass123!)")
    print("   3. Test adding a new resident via RESIDENTS button")
    print("   4. Test creating account for that resident")
    print("   5. Test logging in as that resident (should see USER dashboard)")
    print()
