"""Add photo_path column to residents table"""
from app.db import engine
from sqlalchemy import text

try:
    with engine.connect() as connection:
        # Check if column exists first
        result = connection.execute(text("""
            SELECT COUNT(*) as count 
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = 'bes_management_db' 
            AND TABLE_NAME = 'residents' 
            AND COLUMN_NAME = 'photo_path'
        """))
        
        exists = result.fetchone()[0] > 0
        
        if not exists:
            # Add photo_path column
            connection.execute(text("""
                ALTER TABLE residents 
                ADD COLUMN photo_path VARCHAR(500)
            """))
            connection.commit()
            print("✅ Successfully added photo_path column to residents table")
        else:
            print("✅ photo_path column already exists")
except Exception as e:
    print(f"❌ Error: {e}")
