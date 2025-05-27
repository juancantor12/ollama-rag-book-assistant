"""Pydantic schemas for permission validation."""

from pydantic import BaseModel


class CreatePermissionSchema(BaseModel):
    """CreateSchema."""

    name: str


class UpdatePermissionSchema(BaseModel):
    """Update schema"""

    idx: int
    name: str
