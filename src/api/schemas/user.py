"""Pydantic schemas for User validation."""

from pydantic import BaseModel


class UserCreateSchema(BaseModel):
    """User creation schema."""

    username: str
    password: str
    role: str


class UserGetSchema(BaseModel):
    """User retrieval schema."""

    idx: int
    username: str
    role: str
    active: bool
