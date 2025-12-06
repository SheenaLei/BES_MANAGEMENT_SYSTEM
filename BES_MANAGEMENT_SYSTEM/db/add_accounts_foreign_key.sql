-- ========================================
-- RE-ESTABLISH FOREIGN KEY CONNECTION
-- Run this AFTER creating the residents table
-- ========================================

USE barangay_db;

-- 1. Drop the constraint if it exists (to avoid errors)
-- Note: This might fail if it doesn't exist, which is fine.
SET @exist := (SELECT COUNT(*) FROM information_schema.TABLE_CONSTRAINTS WHERE TABLE_NAME = 'accounts' AND CONSTRAINT_NAME = 'accounts_ibfk_1' AND TABLE_SCHEMA = DATABASE());
SET @sql := IF(@exist > 0, 'ALTER TABLE accounts DROP FOREIGN KEY accounts_ibfk_1', 'SELECT "Constraint does not exist"');
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 2. Add the foreign key constraint
ALTER TABLE accounts
ADD CONSTRAINT accounts_ibfk_1
FOREIGN KEY (resident_id) REFERENCES residents(resident_id)
ON DELETE CASCADE ON UPDATE CASCADE;

SELECT 'Foreign key re-established successfully!' AS message;
