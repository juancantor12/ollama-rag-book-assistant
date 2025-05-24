"""Pydantic schemas for User validation."""

from pydantic import BaseModel

class UserCreate(BaseModel):
    """User creation schema."""
    username: str
    password: str
    role: str

class UserGet(BaseModel):
    """User retrieval schema."""
    idx: int
    username: str
    role: str
    active: bool
