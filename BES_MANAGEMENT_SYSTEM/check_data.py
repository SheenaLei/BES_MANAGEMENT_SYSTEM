"""Check if residents data exists"""
from app.db import engine
from sqlalchemy import text

try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT COUNT(*) FROM residents"))
        count = result.fetchone()[0]
        print(f"✅ Residents in database: {count}")
        
        if count > 0:
            result = connection.execute(text("SELECT last_name, first_name FROM residents LIMIT 5"))
            print("\n📋 Sample residents:")
            for row in result:
                print(f"  - {row[0]}, {row[1]}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
