-- ========================================
-- ADD CRITICAL MISSING COLUMNS
-- Email is required for OTP/Login system
-- ========================================

USE barangay_db;

-- Add email column if it doesn't exist
ALTER TABLE residents ADD COLUMN IF NOT EXISTS email VARCHAR(255);

-- Add other potentially useful columns from old schema if needed
-- ALTER TABLE residents ADD COLUMN IF NOT EXISTS date_of_residency DATE;
-- ALTER TABLE residents ADD COLUMN IF NOT EXISTS resident_status ENUM('Permanent', 'Temporary', 'Boarder') DEFAULT 'Permanent';

SELECT 'Added email column to residents table' AS message;
