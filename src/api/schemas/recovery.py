"""Pydantic schemas for recovery."""

from pydantic import BaseModel


class RecoveryRequestSchema(BaseModel):
    """Recovery request."""

    username: str
    new_password: str
    recovery_code: str
