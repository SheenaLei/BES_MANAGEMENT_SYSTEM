import re

# Read the SQL file
with open('db/sample_residents_data.sql', 'r', encoding='utf-8') as f:
    content = f.read()

# New sitio names for Barangay Balibago, Calatagan
sitio_names = ['Pandayan', 'Aplaya', 'Centro', 'Dita', 'Tulay na Bato', 'Kawayanan', 'Kudrado']

# Replace all occurrences
# Distribute Sitio 1 residents across first 3 sitios
# Distribute Sitio 2 residents across next 2 sitios  
# Distribute Sitio 3 residents across last 2 sitios

# Simple replacement strategy
content = content.replace('-- SITIO 1 RESIDENTS (40 people)', '-- PANDAYAN, APLAYA, CENTRO RESIDENTS (40 people)')
content = content.replace('-- SITIO 2 RESIDENTS (35 people)', '-- DITA, TULAY NA BATO RESIDENTS (35 people)')
content = content.replace('-- SITIO 3 RESIDENTS (25 people)', '-- KAWAYANAN, KUDRADO RESIDENTS (25 people)')

# Replace sitios in data - distribute evenly
lines = content.split('\n')
sitio1_counter = 0
sitio2_counter = 0
sitio3_counter = 0

for i, line in enumerate(lines):
    if "'Sitio 1'" in line:
        # Distribute across Pandayan, Aplaya, Centro
        idx = sitio1_counter % 3
        lines[i] = line.replace("'Sitio 1'", f"'{sitio_names[idx]}'")
        sitio1_counter += 1
    elif "'Sitio 2'" in line:
        # Distribute across Dita, Tulay na Bato
        idx = 3 + (sitio2_counter % 2)
        lines[i] = line.replace("'Sitio 2'", f"'{sitio_names[idx]}'")
        sitio2_counter += 1
    elif "'Sitio 3'" in line:
        # Distribute across Kawayanan, Kudrado
        idx = 5 + (sitio3_counter % 2)
        lines[i] = line.replace("'Sitio 3'", f"'{sitio_names[idx]}'")
        sitio3_counter += 1

# Write back
with open('db/sample_residents_data.sql', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

print('✅ Updated sitio names successfully!')
print(f'Pandayan: {sitio1_counter // 3 + (1 if sitio1_counter % 3 > 0 else 0)} residents')
print(f'Aplaya: {sitio1_counter // 3 + (1 if sitio1_counter % 3 > 1 else 0)} residents')
print(f'Centro: {sitio1_counter // 3} residents')
print(f'Dita: {sitio2_counter // 2 + (sitio2_counter % 2)} residents')
print(f'Tulay na Bato: {sitio2_counter // 2} residents')
print(f'Kawayanan: {sitio3_counter // 2 + (sitio3_counter % 2)} residents')
print(f'Kudrado: {sitio3_counter // 2} residents')
