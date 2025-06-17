"""Pydantic schemas for shared validation."""

from pydantic import BaseModel


class ListSchema(BaseModel):
    """List query schema."""

    limit: int = 1000
    offset: int = 0


class GetSchemaSchema(BaseModel):
    """Get schema."""
    model_name: str
