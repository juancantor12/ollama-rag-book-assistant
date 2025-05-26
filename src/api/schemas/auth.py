"""Pydantic schemas for authentication."""

from pydantic import BaseModel


class LoginRequestSchema(BaseModel):
    """Token retrieval schema."""

    username: str
    password: str
