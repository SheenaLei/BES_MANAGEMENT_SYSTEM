import re

# Read the SQL file
with open('db/sample_residents_data.sql', 'r', encoding='utf-8') as f:
    content = f.read()

print("=" * 60)
print("VALIDATION REPORT: sample_residents_data.sql")
print("=" * 60)

# Check 1: Count opening and closing parentheses
open_paren = content.count('(')
close_paren = content.count(')')
if open_paren != close_paren:
    print(f'❌ ERROR: Mismatched parentheses: {open_paren} opening vs {close_paren} closing')
else:
    print(f'✅ Parentheses balanced: {open_paren} pairs')

# Check 2: Count INSERT rows
insert_rows = content.count('),\n') + content.count('),\r\n')
last_row = content.count(');')
total_rows = insert_rows + last_row
print(f'✅ Total INSERT rows: {total_rows} (Expected: 100)')

if total_rows != 100:
    print(f'⚠️  WARNING: Expected 100 rows, found {total_rows}')

# Check 3: Verify sitio names are updated
if "'Sitio 1'" in content or "'Sitio 2'" in content or "'Sitio 3'" in content:
    print('❌ ERROR: Still contains old sitio format (Sitio 1, 2, 3)')
else:
    print('✅ All sitios updated to new names')

# Check 4: Count each sitio
print("\n" + "=" * 60)
print("SITIO DISTRIBUTION:")
print("=" * 60)
sitios = ['Pandayan', 'Aplaya', 'Centro', 'Dita', 'Tulay na Bato', 'Kawayanan', 'Kudrado']
total_sitio_count = 0
for sitio in sitios:
    count = content.count(f"'{sitio}'")
    total_sitio_count += count
    print(f'  {sitio:20s}: {count:3d} residents')

print(f'  {"Total":20s}: {total_sitio_count:3d} residents')

# Check 5: Verify required columns
print("\n" + "=" * 60)
print("REQUIRED FIELDS CHECK:")
print("=" * 60)
required_fields = ['last_name', 'first_name', 'gender', 'birth_date', 'civil_status', 
                   'barangay', 'municipality', 'sitio']
all_fields_ok = True
for field in required_fields:
    if field in content:
        print(f'✅ {field}')
    else:
        print(f'❌ Missing: {field}')
        all_fields_ok = False

# Check 6: Look for common SQL syntax errors
print("\n" + "=" * 60)
print("SYNTAX CHECKS:")
print("=" * 60)

# Check for trailing commas before closing
if '),\n);' in content or '),\r\n);' in content:
    print('❌ ERROR: Trailing comma before final );')
else:
    print('✅ No trailing commas before final values')

# Check for NULL values
null_count = content.count('NULL')
print(f'✅ NULL values found: {null_count} (for optional fields)')

# Check for TRUE/FALSE boolean values
true_count = content.count('TRUE')
false_count = content.count('FALSE')
print(f'✅ Boolean values: {true_count} TRUE, {false_count} FALSE')

# Final verdict
print("\n" + "=" * 60)
if total_rows == 100 and all_fields_ok and "'Sitio 1'" not in content:
    print("✅ VALIDATION PASSED! File is ready to import.")
else:
    print("⚠️  VALIDATION HAS WARNINGS - Review above.")
print("=" * 60)
