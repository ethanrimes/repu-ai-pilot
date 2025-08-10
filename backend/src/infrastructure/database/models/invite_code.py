# backend/src/infrastructure/database/models/invite_code.py
from sqlalchemy import Column, Integer, Text, DateTime, BigInteger, ARRAY
from sqlalchemy.sql import func
from .company import Base  # reuse existing declarative Base

class InviteCode(Base):
    __tablename__ = "invite_codes"

    id = Column(BigInteger, primary_key=True)
    code = Column(Text, nullable=False, unique=True, index=True)
    max_uses = Column(Integer, nullable=False, default=1)
    uses = Column(Integer, nullable=False, default=0)
    expires_at = Column(DateTime(timezone=True))
    created_by = Column(BigInteger)
    redeemed_by = Column(ARRAY(BigInteger))
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
