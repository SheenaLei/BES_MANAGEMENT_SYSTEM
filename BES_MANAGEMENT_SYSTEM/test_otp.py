# Quick OTP Test Script
# This shows you how the OTP system works

from app.db import SessionLocal
from app.models import Account
from app.auth import generate_and_send_otp

# Get the admin account
db = SessionLocal()
account = db.query(Account).filter(Account.username == "admin").first()

if account:
    print("\n" + "="*60)
    print("🔐 TESTING OTP GENERATION")
    print("="*60)
    print(f"Account: {account.username}")
    print(f"Role: {account.user_role}")
    
    # Generate OTP
    result = generate_and_send_otp(account, purpose='test')
    
    if result.get("success"):
        print("\n✅ OTP Generated Successfully!")
        print("\nIn DEV mode, the OTP is printed above.")
        print("In PRODUCTION mode, it would be emailed to the user.")
    else:
        print(f"\n❌ Error: {result.get('error')}")
    
    print("="*60 + "\n")
else:
    print("❌ Admin account not found!")

db.close()
