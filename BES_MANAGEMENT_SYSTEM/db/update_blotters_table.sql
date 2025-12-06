-- Update blotters table to add new columns
-- Run this script to update the database schema

USE barangay_db;

-- Add reason column (replace summary with reason)
ALTER TABLE blotters 
ADD COLUMN reason TEXT AFTER respondent_name;

-- Add location column
ALTER TABLE blotters 
ADD COLUMN location VARCHAR(255) AFTER incident_date;

-- Add handled_by column  
ALTER TABLE blotters 
ADD COLUMN handled_by VARCHAR(255) AFTER location;

-- Change incident_date from DATE to DATETIME
ALTER TABLE blotters 
MODIFY COLUMN incident_date DATETIME;

-- Copy summary to reason if it exists, then drop summary
UPDATE blotters SET reason = summary WHERE reason IS NULL AND summary IS NOT NULL;

-- Drop the old summary column (optional - uncomment if you want to remove it)
-- ALTER TABLE blotters DROP COLUMN summary;

-- Show updated table structure
DESCRIBE blotters;
