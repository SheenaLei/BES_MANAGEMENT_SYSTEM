SET FOREIGN_KEY_CHECKS = 0;

-- Create database (optional; comment out if DB already created)
CREATE DATABASE IF NOT EXISTS `barangay_db` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `barangay_db`;

-- Residents table (age is regular INT; triggers below compute it)
CREATE TABLE IF NOT EXISTS residents (
  resident_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  first_name VARCHAR(100) NOT NULL,
  middle_name VARCHAR(100),
  last_name VARCHAR(100) NOT NULL,
  suffix VARCHAR(20),
  gender ENUM('Male','Female','Other') NOT NULL,
  birthdate DATE NOT NULL,
  age INT DEFAULT NULL,
  civil_status ENUM('Single','Married','Widowed','Separated') DEFAULT 'Single',
  occupation VARCHAR(150),
  is_registered_voter BOOLEAN DEFAULT FALSE,
  phone_number VARCHAR(25),
  email VARCHAR(255),
  purok_zone VARCHAR(100),
  barangay VARCHAR(100) DEFAULT 'Barangay Balibago',
  date_of_residency DATE,
  resident_status ENUM('Permanent','Temporary','Boarder') DEFAULT 'Permanent',
  remarks_set JSON,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uq_resident_email (email),
  INDEX idx_lastname (last_name)
);

-- Accounts table
CREATE TABLE IF NOT EXISTS accounts (
  account_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  resident_id BIGINT,
  username VARCHAR(100) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  user_role ENUM('Resident','Staff','Admin') DEFAULT 'Resident',
  account_status ENUM('Active','Deactivated','Pending') DEFAULT 'Pending',
  last_login DATETIME,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (resident_id) REFERENCES residents(resident_id) ON DELETE SET NULL
);

-- Admins table (profile; admins should also have an account row pointing to residents)
CREATE TABLE IF NOT EXISTS admins (
  admin_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  account_id BIGINT,
  username VARCHAR(100) UNIQUE,
  email VARCHAR(255),
  phone_number VARCHAR(25),
  first_name VARCHAR(100),
  middle_name VARCHAR(100),
  last_name VARCHAR(100),
  position VARCHAR(50), -- Captain, Secretary, Treasurer, IT
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (account_id) REFERENCES accounts(account_id) ON DELETE CASCADE
);

-- Uploaded documents (PSA / birth cert / IDs / payment proofs)
CREATE TABLE IF NOT EXISTS document_uploads (
  upload_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  resident_id BIGINT NOT NULL,
  request_id BIGINT,
  doc_type ENUM('PSA','Birth Certificate','ID','PaymentProof','Other') NOT NULL,
  id_type VARCHAR(100),
  filename VARCHAR(255) NOT NULL,
  file_path VARCHAR(500) NOT NULL,
  uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  verified ENUM('Pending','Approved','Rejected') DEFAULT 'Pending',
  verifier_admin_id BIGINT,
  verifier_reason TEXT,
  FOREIGN KEY (resident_id) REFERENCES residents(resident_id) ON DELETE CASCADE
);

-- Services catalog
CREATE TABLE IF NOT EXISTS services (
  service_id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(150) NOT NULL,
  description TEXT,
  fee DECIMAL(10,2) DEFAULT 0.00,
  requires_payment BOOLEAN DEFAULT TRUE,
  requires_documents JSON,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Requests table (service requests)
CREATE TABLE IF NOT EXISTS requests (
  request_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  resident_id BIGINT NOT NULL,
  service_id INT NOT NULL,
  purpose TEXT,
  fields JSON,
  payment_method ENUM('GCash','Cash','None') DEFAULT 'None',
  payment_proof_upload_id BIGINT,
  status ENUM('Pending','Payment Pending','Approved','Declined','Cancelled','Completed') DEFAULT 'Pending',
  fee_amount DECIMAL(10,2) DEFAULT 0.00,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  pickup_datetime DATETIME,
  FOREIGN KEY (resident_id) REFERENCES residents(resident_id) ON DELETE CASCADE,
  FOREIGN KEY (service_id) REFERENCES services(service_id) ON DELETE CASCADE
);

-- Payments table
CREATE TABLE IF NOT EXISTS payments (
  payment_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  request_id BIGINT,
  resident_id BIGINT,
  amount DECIMAL(10,2),
  method ENUM('GCash','Cash') DEFAULT 'Cash',
  proof_upload_id BIGINT,
  status ENUM('Pending','Verified','Rejected') DEFAULT 'Pending',
  verified_by_admin_id BIGINT,
  verified_at DATETIME,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (request_id) REFERENCES requests(request_id) ON DELETE CASCADE
);

-- Announcements (admin posts)
CREATE TABLE IF NOT EXISTS announcements (
  announcement_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(255),
  content TEXT,
  posted_by_admin_id BIGINT,
  posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  visible BOOLEAN DEFAULT TRUE
);

-- Blotter records (admin only)
CREATE TABLE IF NOT EXISTS blotters (
  blotter_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  complainant_name VARCHAR(255),
  respondent_name VARCHAR(255),
  incident_date DATE,
  summary TEXT,
  posted_by_admin_id BIGINT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Notifications (in-system)
CREATE TABLE IF NOT EXISTS notifications (
  notification_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  resident_id BIGINT,
  title VARCHAR(255),
  message TEXT,
  is_read BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- OTPs for 2FA (login, password reset)
CREATE TABLE IF NOT EXISTS otps (
  otp_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  account_id BIGINT,
  code VARCHAR(10),
  purpose ENUM('login','password_reset','email_verification') DEFAULT 'login',
  expires_at DATETIME,
  is_used BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (account_id) REFERENCES accounts(account_id) ON DELETE CASCADE
);

-- Audit logs (staff/admin logs)
CREATE TABLE IF NOT EXISTS staff_audit_logs (
  log_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  admin_id BIGINT,
  action VARCHAR(255),
  description TEXT,
  ip_address VARCHAR(50),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Resident activity logs
CREATE TABLE IF NOT EXISTS resident_logs (
  log_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  resident_id BIGINT,
  request_id BIGINT,
  action_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  action VARCHAR(255),
  details TEXT,
  FOREIGN KEY (resident_id) REFERENCES residents(resident_id) ON DELETE CASCADE
);

-- Backup history
CREATE TABLE IF NOT EXISTS backups (
  backup_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  filename VARCHAR(500),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  created_by_admin_id BIGINT
);

SET FOREIGN_KEY_CHECKS = 1;


-- =========================
-- Triggers to maintain 'age' column on INSERT / UPDATE
-- (Triggers use CURDATE() which is allowed; they compute age at row change)
-- =========================

DELIMITER $$

DROP TRIGGER IF EXISTS trg_residents_age_before_insert $$
CREATE TRIGGER trg_residents_age_before_insert
BEFORE INSERT ON residents
FOR EACH ROW
BEGIN
  IF NEW.birthdate IS NOT NULL THEN
    SET NEW.age = TIMESTAMPDIFF(YEAR, NEW.birthdate, CURDATE());
  ELSE
    SET NEW.age = NULL;
  END IF;
END $$

DROP TRIGGER IF EXISTS trg_residents_age_before_update $$
CREATE TRIGGER trg_residents_age_before_update
BEFORE UPDATE ON residents
FOR EACH ROW
BEGIN
  IF NEW.birthdate IS NOT NULL THEN
    SET NEW.age = TIMESTAMPDIFF(YEAR, NEW.birthdate, CURDATE());
  ELSE
    SET NEW.age = NULL;
  END IF;
END $$

DELIMITER ;

-- =========================
-- View for always-correct computed age (use this for reports / UI if preferred)
-- =========================

DROP VIEW IF EXISTS residents_with_age;
CREATE VIEW residents_with_age AS
SELECT
  resident_id,
  first_name,
  middle_name,
  last_name,
  suffix,
  gender,
  birthdate,
  TIMESTAMPDIFF(YEAR, birthdate, CURDATE()) AS computed_age,
  civil_status,
  occupation,
  is_registered_voter,
  phone_number,
  email,
  purok_zone,
  barangay,
  date_of_residency,
  resident_status,
  remarks_set,
  created_at,
  updated_at
FROM residents;
