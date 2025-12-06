"""Add image_path column to announcements table"""
from app.db import engine
from sqlalchemy import text

try:
    with engine.connect() as connection:
        # Check if column exists first
        result = connection.execute(text("""
            SELECT COUNT(*) as count 
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = 'bes_management_db' 
            AND TABLE_NAME = 'announcements' 
            AND COLUMN_NAME = 'image_path'
        """))
        
        exists = result.fetchone()[0] > 0
        
        if not exists:
            # Add image_path column
            connection.execute(text("""
                ALTER TABLE announcements 
                ADD COLUMN image_path VARCHAR(500)
            """))
            connection.commit()
            print("✅ Successfully added image_path column to announcements table")
        else:
            print("✅ image_path column already exists in announcements table")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
