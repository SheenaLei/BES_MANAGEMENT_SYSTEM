"""Check actual columns in residents table"""
from app.db import engine
from sqlalchemy import text

try:
    with engine.connect() as connection:
        result = connection.execute(text("""
            SELECT COLUMN_NAME 
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = 'bes_management_db' 
            AND TABLE_NAME = 'residents'
            ORDER BY ORDINAL_POSITION
        """))
        
        print("✅ Columns in residents table:")
        for row in result:
            print(f"  - {row[0]}")
except Exception as e:
    print(f"❌ Error: {e}")
