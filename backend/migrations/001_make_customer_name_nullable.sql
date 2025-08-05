-- Migration: Make customer name field nullable
-- Date: 2025-08-05
-- Description: Allow customer name to be null to support Firebase users without names

BEGIN;

-- Remove NOT NULL constraint from name column
ALTER TABLE customers ALTER COLUMN name DROP NOT NULL;

-- Add a comment to document the change
COMMENT ON COLUMN customers.name IS 'Customer name - nullable to support Firebase users without display names';

COMMIT;
