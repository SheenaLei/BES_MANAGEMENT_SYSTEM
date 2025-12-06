-- ========================================
-- FINAL FIX: RECREATE RESIDENTS TABLE (BIGINT)
-- ========================================

USE barangay_db;

-- 1. Disable foreign key checks
SET FOREIGN_KEY_CHECKS = 0;

-- 2. Drop the table if it exists
DROP TABLE IF EXISTS residents;

-- 3. Create the table with BIGINT (Matching original schema)
CREATE TABLE residents (
    -- Primary Key (MUST BE BIGINT TO MATCH ACCOUNTS TABLE)
    resident_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    
    -- Personal Information
    last_name VARCHAR(100) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    middle_name VARCHAR(100),
    suffix VARCHAR(20),
    
    -- Demographics
    gender ENUM('Male', 'Female', 'Other') NOT NULL,
    birth_date DATE NOT NULL,
    birth_place VARCHAR(255),
    age INT,
    civil_status ENUM('Single', 'Married', 'Widowed', 'Divorced', 'Separated', 'Live-in') NOT NULL,
    
    -- Family Information
    spouse_name VARCHAR(255),
    no_of_children INT DEFAULT 0,
    no_of_siblings INT DEFAULT 0,
    mother_full_name VARCHAR(255),
    father_full_name VARCHAR(255),
    
    -- Personal Details
    nationality VARCHAR(100) DEFAULT 'Filipino',
    religion VARCHAR(100),
    occupation VARCHAR(150),
    highest_educational_attainment VARCHAR(100),
    email VARCHAR(255),
    
    -- Contact Information
    contact_number VARCHAR(20),
    emergency_contact_name VARCHAR(255),
    emergency_contact_number VARCHAR(20),
    
    -- Address Information
    sitio VARCHAR(100),
    barangay VARCHAR(100) NOT NULL,
    municipality VARCHAR(100) NOT NULL,
    
    -- Government Programs & Status
    registered_voter BOOLEAN DEFAULT FALSE,
    indigent BOOLEAN DEFAULT FALSE,
    solo_parent BOOLEAN DEFAULT FALSE,
    solo_parent_id_no VARCHAR(50),
    fourps_member BOOLEAN DEFAULT FALSE,
    
    -- System Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Indexes
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

-- 4. Re-enable foreign key checks
SET FOREIGN_KEY_CHECKS = 1;

SELECT 'Residents table recreated successfully with BIGINT!' AS message;
