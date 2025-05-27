"""Pydantic schemas for Role validation."""

from typing import List
from pydantic import BaseModel


class CreateRoleSchema(BaseModel):
    """CreateSchema."""

    name: str
    permissions: List[int]


class UpdateRoleSchema(BaseModel):
    """Update schema"""

    idx: int
    name: str
    permissions: List[int]
