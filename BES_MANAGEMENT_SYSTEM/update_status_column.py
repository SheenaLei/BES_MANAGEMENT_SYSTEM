from sqlalchemy import text
from app.db import engine

with engine.connect() as conn:
    conn.execute(text("ALTER TABLE certificate_requests MODIFY COLUMN status VARCHAR(50) DEFAULT 'Pending'"))
    conn.commit()
    print("✅ Status column updated successfully!")
