"""
Script to create barangay_officials table and seed initial data
Run this once to set up the Officials feature
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import engine, SessionLocal
from app.models import BarangayOfficial, Base
from sqlalchemy import inspect

def create_officials_table():
    """Create the barangay_officials table if it doesn't exist"""
    inspector = inspect(engine)
    
    if 'barangay_officials' not in inspector.get_table_names():
        print("Creating barangay_officials table...")
        BarangayOfficial.__table__.create(engine)
        print("✅ Table created successfully!")
    else:
        print("ℹ️ Table barangay_officials already exists")
    
    return True

def seed_default_officials():
    """Seed the table with default officials if empty"""
    db = SessionLocal()
    
    try:
        # Check if there are any officials
        count = db.query(BarangayOfficial).count()
        
        if count == 0:
            print("Seeding default officials...")
            
            officials_data = [
                {"position": "Punong Barangay", "full_name": "Hon. Juan Dela Cruz", "display_order": 1, "category": "Sanggunian"},
                {"position": "Kagawad", "full_name": "Hon. Maria Santos", "display_order": 2, "category": "Sanggunian"},
                {"position": "Kagawad", "full_name": "Hon. Pedro Reyes", "display_order": 3, "category": "Sanggunian"},
                {"position": "Kagawad", "full_name": "Hon. Ana Garcia", "display_order": 4, "category": "Sanggunian"},
                {"position": "Kagawad", "full_name": "Hon. Jose Mendoza", "display_order": 5, "category": "Sanggunian"},
                {"position": "Kagawad", "full_name": "Hon. Rosa Flores", "display_order": 6, "category": "Sanggunian"},
                {"position": "Kagawad", "full_name": "Hon. Carlos Ramos", "display_order": 7, "category": "Sanggunian"},
                {"position": "Kagawad", "full_name": "Hon. Elena Cruz", "display_order": 8, "category": "Sanggunian"},
                {"position": "SK Chairman", "full_name": "Hon. Miguel Torres", "display_order": 9, "category": "Other"},
                {"position": "Secretary", "full_name": "Ms. Lorna Bautista", "display_order": 10, "category": "Other"},
                {"position": "Treasurer", "full_name": "Mr. Roberto Villanueva", "display_order": 11, "category": "Other"},
            ]
            
            for data in officials_data:
                official = BarangayOfficial(
                    position=data["position"],
                    full_name=data["full_name"],
                    display_order=data["display_order"],
                    category=data["category"],
                    is_active=True
                )
                db.add(official)
            
            db.commit()
            print(f"✅ Seeded {len(officials_data)} default officials!")
        else:
            print(f"ℹ️ Table already has {count} officials, skipping seed")
            
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding officials: {e}")
        raise
    finally:
        db.close()

def main():
    print("=" * 50)
    print("Barangay Officials Setup Script")
    print("=" * 50)
    
    try:
        # Create table
        create_officials_table()
        
        # Seed data
        seed_default_officials()
        
        print("\n✅ Officials setup complete!")
        print("You can now use the Officials page in admin and user views.")
        
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
