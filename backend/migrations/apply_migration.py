#!/usr/bin/env python3
"""
Quick script to apply the customer name nullable migration
"""
import sys
import os
from pathlib import Path

# Add the backend src to the path
backend_path = Path(__file__).parent.parent.parent / 'backend'
print(f"Adding backend path to sys.path: {backend_path}")
sys.path.insert(0, str(backend_path))

from src.config.settings import get_settings
from sqlalchemy import create_engine, text

def apply_migration():
    """Apply the customer name nullable migration"""
    settings = get_settings()
    engine = create_engine(settings.database_url)
    
    migration_sql = """
    -- Migration: Make customer name field nullable
    -- Date: 2025-08-05
    -- Description: Allow customer name to be null to support Firebase users without names

    BEGIN;
    
    -- Remove NOT NULL constraint from name column if it exists
    ALTER TABLE customers ALTER COLUMN name DROP NOT NULL;
    
    -- Add a comment to document the change
    COMMENT ON COLUMN customers.name IS 'Customer name - nullable to support Firebase users without display names';
    
    COMMIT;
    """
    
    try:
        with engine.connect() as connection:
            # Execute the migration
            connection.execute(text(migration_sql))
            connection.commit()
            print("✅ Migration applied successfully: customer.name is now nullable")
    except Exception as e:
        if "does not exist" in str(e) or "already" in str(e):
            print("✅ Migration not needed: customer.name is already nullable")
        else:
            print(f"❌ Migration failed: {e}")
            raise

if __name__ == "__main__":
    apply_migration()
