-- ========================================
-- RESIDENTS TABLE SCHEMA
-- BES Management System
-- ========================================
/*
CREATE TABLE IF NOT EXISTS residents (
    -- Primary Key
    resident_id INT PRIMARY KEY AUTO_INCREMENT,
    
    -- ========================================
    -- PERSONAL INFORMATION
    -- ========================================
    last_name VARCHAR(100) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    middle_name VARCHAR(100),
    suffix VARCHAR(20),
    
    -- ========================================
    -- DEMOGRAPHICS
    -- ========================================
    gender ENUM('Male', 'Female', 'Other') NOT NULL,
    birth_date DATE NOT NULL,
    birth_place VARCHAR(255),
    age INT,
    civil_status ENUM('Single', 'Married', 'Widowed', 'Divorced', 'Separated', 'Live-in') NOT NULL,
    
    -- ========================================
    -- FAMILY INFORMATION
    -- ========================================
    spouse_name VARCHAR(255),
    no_of_children INT DEFAULT 0,
    no_of_siblings INT DEFAULT 0,
    
    -- Parents Information
    mother_full_name VARCHAR(255),
    father_full_name VARCHAR(255),
    
    -- ========================================
    -- PERSONAL DETAILS
    -- ========================================
    nationality VARCHAR(100) DEFAULT 'Filipino',
    religion VARCHAR(100),
    occupation VARCHAR(150),
    highest_educational_attainment VARCHAR(100),
    
    -- ========================================
    -- CONTACT INFORMATION
    -- ========================================
    contact_number VARCHAR(20),
    
    -- Emergency Contact
    emergency_contact_name VARCHAR(255),
    emergency_contact_number VARCHAR(20),
    
    -- ========================================
    -- ADDRESS INFORMATION
    -- ========================================
    sitio VARCHAR(100),
    barangay VARCHAR(100) NOT NULL,
    municipality VARCHAR(100) NOT NULL,
    
    -- ========================================
    -- GOVERNMENT PROGRAMS & STATUS
    -- ========================================
    registered_voter BOOLEAN DEFAULT FALSE,
    indigent BOOLEAN DEFAULT FALSE,
    solo_parent BOOLEAN DEFAULT FALSE,
    solo_parent_id_no VARCHAR(50),
    fourps_member BOOLEAN DEFAULT FALSE,
    
    -- ========================================
    -- SYSTEM TIMESTAMPS
    -- ========================================
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- ========================================
    -- INDEXES FOR PERFORMANCE
    -- ========================================
    INDEX idx_last_name (last_name),
    INDEX idx_first_name (first_name),
    INDEX idx_full_name (last_name, first_name),
    INDEX idx_barangay (barangay),
    INDEX idx_municipality (municipality),
    INDEX idx_registered_voter (registered_voter),
    INDEX idx_indigent (indigent),
    INDEX idx_solo_parent (solo_parent),
    INDEX idx_fourps (fourps_member),
    INDEX idx_birth_date (birth_date)
    
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ========================================
-- ALTER TABLE STATEMENTS
-- Use these if the table already exists
-- ========================================

/*
-- Add columns to existing residents table
ALTER TABLE residents
    ADD COLUMN IF NOT EXISTS last_name VARCHAR(100) NOT NULL AFTER resident_id,
    ADD COLUMN IF NOT EXISTS first_name VARCHAR(100) NOT NULL AFTER last_name,
    ADD COLUMN IF NOT EXISTS middle_name VARCHAR(100) AFTER first_name,
    ADD COLUMN IF NOT EXISTS suffix VARCHAR(20) AFTER middle_name,
    ADD COLUMN IF NOT EXISTS gender ENUM('Male', 'Female', 'Other') NOT NULL AFTER suffix,
    ADD COLUMN IF NOT EXISTS birth_date DATE NOT NULL AFTER gender,
    ADD COLUMN IF NOT EXISTS birth_place VARCHAR(255) AFTER birth_date,
    ADD COLUMN IF NOT EXISTS age INT AFTER birth_place,
    ADD COLUMN IF NOT EXISTS civil_status ENUM('Single', 'Married', 'Widowed', 'Divorced', 'Separated', 'Live-in') NOT NULL AFTER age,
    ADD COLUMN IF NOT EXISTS spouse_name VARCHAR(255) AFTER civil_status,
    ADD COLUMN IF NOT EXISTS no_of_children INT DEFAULT 0 AFTER spouse_name,
    ADD COLUMN IF NOT EXISTS no_of_siblings INT DEFAULT 0 AFTER no_of_children,
    ADD COLUMN IF NOT EXISTS mother_full_name VARCHAR(255) AFTER no_of_siblings,
    ADD COLUMN IF NOT EXISTS father_full_name VARCHAR(255) AFTER mother_full_name,
    ADD COLUMN IF NOT EXISTS nationality VARCHAR(100) DEFAULT 'Filipino' AFTER father_full_name,
    ADD COLUMN IF NOT EXISTS religion VARCHAR(100) AFTER nationality,
    ADD COLUMN IF NOT EXISTS occupation VARCHAR(150) AFTER religion,
    ADD COLUMN IF NOT EXISTS highest_educational_attainment VARCHAR(100) AFTER occupation,
    ADD COLUMN IF NOT EXISTS contact_number VARCHAR(20) AFTER highest_educational_attainment,
    ADD COLUMN IF NOT EXISTS emergency_contact_name VARCHAR(255) AFTER contact_number,
    ADD COLUMN IF NOT EXISTS emergency_contact_number VARCHAR(20) AFTER emergency_contact_name,
    ADD COLUMN IF NOT EXISTS sitio VARCHAR(100) AFTER emergency_contact_number,
    ADD COLUMN IF NOT EXISTS barangay VARCHAR(100) NOT NULL AFTER sitio,
    ADD COLUMN IF NOT EXISTS municipality VARCHAR(100) NOT NULL AFTER barangay,
    ADD COLUMN IF NOT EXISTS registered_voter BOOLEAN DEFAULT FALSE AFTER municipality,
    ADD COLUMN IF NOT EXISTS indigent BOOLEAN DEFAULT FALSE AFTER registered_voter,
    ADD COLUMN IF NOT EXISTS solo_parent BOOLEAN DEFAULT FALSE AFTER indigent,
    ADD COLUMN IF NOT EXISTS solo_parent_id_no VARCHAR(50) AFTER solo_parent,
    ADD COLUMN IF NOT EXISTS fourps_member BOOLEAN DEFAULT FALSE AFTER solo_parent_id_no,
    ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP AFTER fourps_member,
    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP AFTER created_at;

-- Add indexes
CREATE INDEX IF NOT EXISTS idx_last_name ON residents(last_name);
CREATE INDEX IF NOT EXISTS idx_first_name ON residents(first_name);
CREATE INDEX IF NOT EXISTS idx_full_name ON residents(last_name, first_name);
CREATE INDEX IF NOT EXISTS idx_barangay ON residents(barangay);
CREATE INDEX IF NOT EXISTS idx_municipality ON residents(municipality);
CREATE INDEX IF NOT EXISTS idx_registered_voter ON residents(registered_voter);
CREATE INDEX IF NOT EXISTS idx_indigent ON residents(indigent);
CREATE INDEX IF NOT EXISTS idx_solo_parent ON residents(solo_parent);
CREATE INDEX IF NOT EXISTS idx_fourps ON residents(fourps_member);
CREATE INDEX IF NOT EXISTS idx_birth_date ON residents(birth_date);
*/


-- ========================================
-- SAMPLE INSERT STATEMENT
-- ========================================

/*
INSERT INTO residents (
    last_name, first_name, middle_name, suffix,
    gender, birth_date, birth_place, age, civil_status,
    spouse_name, no_of_children, no_of_siblings,
    mother_full_name, father_full_name,
    nationality, religion, occupation, highest_educational_attainment,
    contact_number, emergency_contact_name, emergency_contact_number,
    sitio, barangay, municipality,
    registered_voter, indigent, solo_parent, solo_parent_id_no, fourps_member
) VALUES (
    'Dela Cruz', 'Juan', 'Santos', 'Jr.',
    'Male', '1985-05-15', 'Manila', 39, 'Married',
    'Maria Dela Cruz', 3, 2,
    'Ana Santos Dela Cruz', 'Pedro Dela Cruz',
    'Filipino', 'Roman Catholic', 'Construction Worker', 'High School Graduate',
    '09171234567', 'Maria Dela Cruz', '09179876543',
    'Purok 1', 'Barangay Poblacion', 'Manila City',
    TRUE, FALSE, FALSE, NULL, TRUE
);
*/


-- ========================================
-- FIELD DESCRIPTIONS
-- ========================================

/*
FIELD NAME                      | TYPE          | DESCRIPTION
--------------------------------|---------------|--------------------------------------------
resident_id                     | INT           | Primary key, auto-increment
last_name                       | VARCHAR(100)  | Last name/Surname (Required)
first_name                      | VARCHAR(100)  | First name (Required)
middle_name                     | VARCHAR(100)  | Middle name (Optional)
suffix                          | VARCHAR(20)   | Jr., Sr., III, etc. (Optional)
gender                          | ENUM          | Male, Female, Other (Required)
birth_date                      | DATE          | Date of birth (Required)
birth_place                     | VARCHAR(255)  | Place of birth (Optional)
age                             | INT           | Current age (Optional, can be calculated)
civil_status                    | ENUM          | Single, Married, Widowed, etc. (Required)
spouse_name                     | VARCHAR(255)  | Full name of spouse (Optional)
no_of_children                  | INT           | Number of children (Default: 0)
no_of_siblings                  | INT           | Number of siblings (Default: 0)
mother_full_name                | VARCHAR(255)  | Mother's complete name (Optional)
father_full_name                | VARCHAR(255)  | Father's complete name (Optional)
nationality                     | VARCHAR(100)  | Nationality (Default: Filipino)
religion                        | VARCHAR(100)  | Religion (Optional)
occupation                      | VARCHAR(150)  | Current occupation (Optional)
highest_educational_attainment  | VARCHAR(100)  | Highest education level (Optional)
contact_number                  | VARCHAR(20)   | Primary contact number (Optional)
emergency_contact_name          | VARCHAR(255)  | Emergency contact person (Optional)
emergency_contact_number        | VARCHAR(20)   | Emergency contact number (Optional)
sitio                           | VARCHAR(100)  | Sitio/Purok (Optional)
barangay                        | VARCHAR(100)  | Barangay (Required)
municipality                    | VARCHAR(100)  | Municipality/City (Required)
registered_voter                | BOOLEAN       | Is registered voter (Default: FALSE)
indigent                        | BOOLEAN       | Is indigent (Default: FALSE)
solo_parent                     | BOOLEAN       | Is solo parent (Default: FALSE)
solo_parent_id_no               | VARCHAR(50)   | Solo Parent ID Number (Optional)
fourps_member                   | BOOLEAN       | Is 4Ps member (Default: FALSE)
created_at                      | TIMESTAMP     | Record creation timestamp
updated_at                      | TIMESTAMP     | Last update timestamp
*/
