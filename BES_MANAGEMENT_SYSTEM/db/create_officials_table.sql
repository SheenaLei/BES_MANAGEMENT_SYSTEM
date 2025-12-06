-- Create barangay_officials table
-- This table stores information about barangay officials for display on the Officials page

CREATE TABLE IF NOT EXISTS barangay_officials (
    official_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    position VARCHAR(100) NOT NULL COMMENT 'Position/title of the official (e.g., Punong Barangay, Kagawad)',
    full_name VARCHAR(255) NOT NULL COMMENT 'Full name of the official',
    photo_path VARCHAR(500) NULL COMMENT 'Path to the photo file',
    display_order INT DEFAULT 0 COMMENT 'Order for display sorting',
    category VARCHAR(50) DEFAULT 'Sanggunian' COMMENT 'Category: Sanggunian or Other',
    is_active BOOLEAN DEFAULT TRUE COMMENT 'Whether the official is currently active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Insert default officials data
INSERT INTO barangay_officials (position, full_name, display_order, category, is_active) VALUES
('Punong Barangay', 'Hon. Juan Dela Cruz', 1, 'Sanggunian', TRUE),
('Kagawad', 'Hon. Maria Santos', 2, 'Sanggunian', TRUE),
('Kagawad', 'Hon. Pedro Reyes', 3, 'Sanggunian', TRUE),
('Kagawad', 'Hon. Ana Garcia', 4, 'Sanggunian', TRUE),
('Kagawad', 'Hon. Jose Mendoza', 5, 'Sanggunian', TRUE),
('Kagawad', 'Hon. Rosa Flores', 6, 'Sanggunian', TRUE),
('Kagawad', 'Hon. Carlos Ramos', 7, 'Sanggunian', TRUE),
('Kagawad', 'Hon. Elena Cruz', 8, 'Sanggunian', TRUE),
('SK Chairman', 'Hon. Miguel Torres', 9, 'Other', TRUE),
('Secretary', 'Ms. Lorna Bautista', 10, 'Other', TRUE),
('Treasurer', 'Mr. Roberto Villanueva', 11, 'Other', TRUE);
