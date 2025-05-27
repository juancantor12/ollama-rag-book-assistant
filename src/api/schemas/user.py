"""Pydantic schemas for User validation."""

from typing import Optional
from pydantic import BaseModel


class CreateUserSchema(BaseModel):
    """CreateSchema."""

    username: str
    password: str
    role_id: int
    active: bool


class UpdateUserSchema(BaseModel):
    """Update schema"""

    idx: int
    username: str
    password: Optional[str] = None
    role_id: int
    active: bool
