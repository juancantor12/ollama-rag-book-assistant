"""DB Model for recovery codes."""

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from api.db import Base


class RecoveryCode(Base):
    """DB Model for recovery codes."""

    __tablename__ = "recovery_codes"

    idx = Column(Integer, primary_key=True, autoincrement=True)
    code_hash = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False, nullable=False)
