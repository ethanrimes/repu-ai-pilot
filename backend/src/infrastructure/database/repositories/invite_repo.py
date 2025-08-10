# backend/src/infrastructure/database/repositories/invite_repo.py
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from src.infrastructure.database.models.invite_code import InviteCode

class InviteRepository:
    def __init__(self, db: Session):
        self.db = db

    async def get_valid_code(self, code: str) -> Optional[InviteCode]:
        """Return the invite code if it's valid (not expired, uses < max_uses)."""
        now = datetime.now(timezone.utc)
        query = (
            self.db.query(InviteCode)
            .filter(InviteCode.code == code)
            .filter((InviteCode.expires_at.is_(None)) | (InviteCode.expires_at > now))
            .filter(InviteCode.uses < InviteCode.max_uses)
        )
        return query.first()

    async def redeem(self, code_id: int, user_id: int) -> None:
        """Increment uses and append the redeemer's user_id."""
        invite = self.db.query(InviteCode).filter(InviteCode.id == code_id).first()
        if not invite:
            return
        invite.uses += 1
        if invite.redeemed_by is None:
            invite.redeemed_by = [user_id]
        else:
            invite.redeemed_by.append(user_id)
        self.db.add(invite)
        self.db.commit()
