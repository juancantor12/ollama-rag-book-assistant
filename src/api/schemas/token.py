"""Pydantic schemas for token validation."""

from pydantic import BaseModel


class Token(BaseModel):
    """Token retrieval schema."""
    access_token: str
    token_type: str
