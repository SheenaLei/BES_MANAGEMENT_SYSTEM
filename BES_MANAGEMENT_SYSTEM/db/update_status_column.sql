-- Update status column to VARCHAR to support new status values
-- Workflow: Pending -> Under Review -> Processing -> Ready for Pickup -> Completed (or Declined)

ALTER TABLE certificate_requests MODIFY COLUMN status VARCHAR(50) DEFAULT 'Pending';
