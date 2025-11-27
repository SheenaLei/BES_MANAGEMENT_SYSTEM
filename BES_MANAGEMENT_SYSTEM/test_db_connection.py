#!/usr/bin/env python3
"""
Quick database connection test for BES Management System
"""

import sys

def test_connection():
    """Test database connection"""
    print("=" * 60)
    print("Testing Database Connection")
    print("=" * 60)
    print()
    
    # Show current configuration
    try:
        from app.config import SQLALCHEMY_DATABASE_URI
        print("📋 Current Configuration:")
        # Hide password in output
        uri_parts = SQLALCHEMY_DATABASE_URI.split('@')
        if len(uri_parts) > 1:
            user_part = uri_parts[0].split('//')[1].split(':')[0]
            host_part = uri_parts[1]
            print(f"   User: {user_part}")
            print(f"   Host: {host_part}")
        print(f"   Full URI: {SQLALCHEMY_DATABASE_URI.replace(':StrongPass123!', ':***')}")
        print()
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return False
    
    # Test connection
    print("🔌 Attempting to connect...")
    try:
        from app.db import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT VERSION()"))
            version = result.fetchone()[0]
            print(f"✅ Connection successful!")
            print(f"   MySQL Version: {version}")
            
            # Check if database exists
            result = conn.execute(text("SHOW DATABASES LIKE 'barangay_db'"))
            if result.fetchone():
                print(f"✅ Database 'barangay_db' exists")
                
                # Check tables
                conn.execute(text("USE barangay_db"))
                result = conn.execute(text("SHOW TABLES"))
                tables = result.fetchall()
                if tables:
                    print(f"✅ Found {len(tables)} tables:")
                    for table in tables:
                        print(f"      - {table[0]}")
                else:
                    print(f"⚠️  Database exists but no tables found")
                    print(f"   Run: python scripts/seed_admin.py")
            else:
                print(f"⚠️  Database 'barangay_db' does not exist")
                print(f"   Create it in MySQL first")
            
            return True
            
    except Exception as e:
        print(f"❌ Connection failed!")
        print(f"   Error: {str(e)}")
        print()
        print("📝 Possible issues:")
        print("   1. MySQL is not running in Laragon")
        print("   2. MySQL is not accessible from WSL")
        print("   3. Wrong username/password")
        print("   4. Database doesn't exist yet")
        print()
        print("💡 Solutions:")
        print("   • Make sure Laragon is running and MySQL is started")
        print("   • Check if you can connect from Windows")
        print("   • Try using 'root' user instead (see config.py)")
        return False

if __name__ == "__main__":
    print()
    success = test_connection()
    print()
    print("=" * 60)
    if success:
        print("✅ Database is ready!")
        print()
        print("Next steps:")
        print("  1. Run: python3 scripts/seed_admin.py")
        print("  2. Run: python3 gui/run_app.py")
    else:
        print("❌ Database connection failed")
        print()
        print("Please fix the connection issue first")
    print("=" * 60)
    print()
    
    sys.exit(0 if success else 1)
