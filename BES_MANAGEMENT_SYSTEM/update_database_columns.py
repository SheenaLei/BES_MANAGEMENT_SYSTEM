import sys
import os
from sqlalchemy import text, inspect

# Add project root to path
sys.path.append(os.getcwd())

from app.db import engine

def update_database_columns():
    print("🔄 Checking database schema...")
    
    inspector = inspect(engine)
    existing_columns = [col['name'] for col in inspector.get_columns('residents')]
    
    # Define columns to add (name, definition)
    columns_to_add = [
        ('last_name', 'VARCHAR(100) NOT NULL'),
        ('first_name', 'VARCHAR(100) NOT NULL'),
        ('middle_name', 'VARCHAR(100)'),
        ('suffix', 'VARCHAR(20)'),
        ('gender', "ENUM('Male', 'Female', 'Other') NOT NULL"),
        ('birth_date', 'DATE NOT NULL'),
        ('birth_place', 'VARCHAR(255)'),
        ('age', 'INT'),
        ('civil_status', "ENUM('Single', 'Married', 'Widowed', 'Divorced', 'Separated', 'Live-in') NOT NULL"),
        ('spouse_name', 'VARCHAR(255)'),
        ('no_of_children', 'INT DEFAULT 0'),
        ('no_of_siblings', 'INT DEFAULT 0'),
        ('mother_full_name', 'VARCHAR(255)'),
        ('father_full_name', 'VARCHAR(255)'),
        ('nationality', "VARCHAR(100) DEFAULT 'Filipino'"),
        ('religion', 'VARCHAR(100)'),
        ('occupation', 'VARCHAR(150)'),
        ('highest_educational_attainment', 'VARCHAR(100)'),
        ('contact_number', 'VARCHAR(20)'),
        ('emergency_contact_name', 'VARCHAR(255)'),
        ('emergency_contact_number', 'VARCHAR(20)'),
        ('sitio', 'VARCHAR(100)'),
        ('barangay', 'VARCHAR(100) NOT NULL'),
        ('municipality', 'VARCHAR(100) NOT NULL'),
        ('registered_voter', 'BOOLEAN DEFAULT FALSE'),
        ('indigent', 'BOOLEAN DEFAULT FALSE'),
        ('solo_parent', 'BOOLEAN DEFAULT FALSE'),
        ('solo_parent_id_no', 'VARCHAR(50)'),
        ('fourps_member', 'BOOLEAN DEFAULT FALSE')
    ]
    
    with engine.connect() as connection:
        for col_name, col_def in columns_to_add:
            if col_name not in existing_columns:
                print(f"➕ Adding column: {col_name}")
                try:
                    # Construct ALTER TABLE statement
                    # Note: We don't use AFTER here to keep it simple, it appends to the end
                    sql = f"ALTER TABLE residents ADD COLUMN {col_name} {col_def};"
                    connection.execute(text(sql))
                    print(f"   ✅ Added {col_name}")
                except Exception as e:
                    print(f"   ❌ Failed to add {col_name}: {e}")
            else:
                print(f"   ✓ Column {col_name} already exists")
        
        # Commit changes (if transactional DDL is supported, though MySQL DDL is usually implicit commit)
        # connection.commit() 
        
    print("\n✅ Database schema check complete!")

if __name__ == "__main__":
    try:
        update_database_columns()
    except Exception as e:
        print(f"❌ Error: {e}")
