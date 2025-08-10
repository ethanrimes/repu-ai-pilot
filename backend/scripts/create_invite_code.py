#!/usr/bin/env python3
"""
Script to manually insert a hardcoded invite code into the invite_codes table.
Run: python backend/scripts/create_invite_code.py
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone

# Add backend src to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from src.config.settings import get_settings
from src.infrastructure.database.models.invite_code import InviteCode


def main():
    settings = get_settings()
    engine = create_engine(settings.database_url)

    # Hardcoded values
    HARDCODED_CODE = "MY-SPECIAL-CODE-327"
    MAX_USES = 5
    EXPIRES_IN_DAYS = 30

    expires_at = datetime.now(timezone.utc) + timedelta(days=EXPIRES_IN_DAYS)

    with Session(engine) as session:
        # Check if code already exists
        existing = session.query(InviteCode).filter_by(code=HARDCODED_CODE).first()
        if existing:
            print(f"⚠️ Invite code '{HARDCODED_CODE}' already exists (id={existing.id})")
            return

        invite = InviteCode(
            code=HARDCODED_CODE,
            max_uses=MAX_USES,
            uses=0,
            expires_at=expires_at,
            created_by=None,  # set to admin user ID if desired
            redeemed_by=[],
        )
        session.add(invite)
        session.commit()

        print(f"✅ Invite code '{HARDCODED_CODE}' created successfully.")
        print(f"    Max uses: {MAX_USES}")
        print(f"    Expires: {expires_at.isoformat()}")


if __name__ == "__main__":
    main()
