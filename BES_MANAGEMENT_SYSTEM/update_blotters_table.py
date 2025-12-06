"""
Update blotters table to add missing columns
"""
from app.db import SessionLocal
from sqlalchemy import text

def update_blotters_table():
    db = SessionLocal()
    try:
        # Check existing columns
        result = db.execute(text("SHOW COLUMNS FROM blotters"))
        existing_columns = [row[0] for row in result.fetchall()]
        print(f"Existing columns: {existing_columns}")
        
        # Add reason column if not exists
        if 'reason' not in existing_columns:
            db.execute(text("ALTER TABLE blotters ADD COLUMN reason TEXT"))
            print("✅ Added 'reason' column")
        else:
            print("ℹ️ 'reason' column already exists")
        
        # Add location column if not exists
        if 'location' not in existing_columns:
            db.execute(text("ALTER TABLE blotters ADD COLUMN location VARCHAR(255)"))
            print("✅ Added 'location' column")
        else:
            print("ℹ️ 'location' column already exists")
        
        # Add handled_by column if not exists
        if 'handled_by' not in existing_columns:
            db.execute(text("ALTER TABLE blotters ADD COLUMN handled_by VARCHAR(255)"))
            print("✅ Added 'handled_by' column")
        else:
            print("ℹ️ 'handled_by' column already exists")
        
        db.commit()
        print("\n✅ Blotters table updated successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_blotters_table()
