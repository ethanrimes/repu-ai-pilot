#!/usr/bin/env python3
"""
Quick script to apply all migrations in the migrations/ folder
in order, sorted by the first three digits of the filename.
"""

import sys
import os
from pathlib import Path
from sqlalchemy import create_engine, text

# Locate backend path and migrations folder
backend_path = Path(__file__).parent.parent.parent / "backend"
migrations_path = backend_path / "migrations"

print(f"Adding backend path to sys.path: {backend_path}")
sys.path.insert(0, str(backend_path))

from src.config.settings import get_settings


def apply_migrations():
    """Apply all migrations from migrations/ in numeric order."""
    settings = get_settings()
    engine = create_engine(settings.database_url)

    if not migrations_path.exists():
        print(f"❌ Migrations folder not found: {migrations_path}")
        sys.exit(1)

    # Get all .sql files, sorted by first 3 digits in filename
    migration_files = sorted(
        [f for f in migrations_path.iterdir() if f.suffix == ".sql"],
        key=lambda f: int(f.name.split("_")[0])
    )

    if not migration_files:
        print("No migration files found.")
        return

    print(f"Found {len(migration_files)} migration(s). Applying in order...")

    for migration_file in migration_files:
        print(f"▶ Applying migration: {migration_file.name}")
        sql = migration_file.read_text()

        try:
            with engine.begin() as connection:
                connection.execute(text(sql))
            print(f"✅ Migration applied successfully: {migration_file.name}")
        except Exception as e:
            # You might want to log and skip certain known harmless errors
            print(f"❌ Migration failed for {migration_file.name}: {e}")
            raise

    print("🎉 All migrations applied successfully.")


if __name__ == "__main__":
    apply_migrations()
