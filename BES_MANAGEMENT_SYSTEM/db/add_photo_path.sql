-- Add photo_path column to residents table
ALTER TABLE residents ADD COLUMN IF NOT EXISTS photo_path VARCHAR(500);
