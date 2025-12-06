"""Check photo_path in residents table"""
from app.db import engine
from sqlalchemy import text

try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT resident_id, first_name, last_name, photo_path FROM residents WHERE photo_path IS NOT NULL"))
        rows = result.fetchall()
        
        print(f"✅ Residents with photos: {len(rows)}")
        for row in rows:
            print(f"  - {row[1]} {row[2]}: {row[3]}")
            
except Exception as e:
    print(f"❌ Error: {e}")
