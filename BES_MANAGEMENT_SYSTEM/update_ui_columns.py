import xml.etree.ElementTree as ET

ui_file = 'gui/ui/admin_residents.ui'
tree = ET.parse(ui_file)
root = tree.getroot()

# Define the new columns
new_columns = [
    "Last Name", "First Name", "Middle Name", "Suffix",
    "Gender", "Birth Date", "Birth Place", "Age", "Civil Status",
    "Spouse Name", "No. of Children", "No. of Siblings",
    "Mother's Full Name", "Father's Full Name",
    "Nationality", "Religion", "Occupation", "Highest Educational Attainment",
    "Contact Number", "Emergency Contact Name", "Emergency Contact Number",
    "Sitio", "Barangay", "Municipality",
    "Registered Voter", "Indigent", "Solo Parent", "Solo Parent ID No.", "4Ps Member"
]

# Find the tableWidget
table_widget = None
for widget in root.iter('widget'):
    if widget.get('class') == 'QTableWidget' and widget.get('name') == 'tableWidget':
        table_widget = widget
        break

if table_widget:
    # Remove existing columns
    for column in table_widget.findall('column'):
        table_widget.remove(column)

    # Add new columns
    for col_name in new_columns:
        column = ET.SubElement(table_widget, 'column')
        property_elem = ET.SubElement(column, 'property', name='text')
        string_elem = ET.SubElement(property_elem, 'string')
        string_elem.text = col_name

    # Write the changes back to the file
    tree.write(ui_file, encoding='UTF-8', xml_declaration=True)
    print("✅ Updated table columns in admin_residents.ui")
else:
    print("❌ Could not find tableWidget in admin_residents.ui")
