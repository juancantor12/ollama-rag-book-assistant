"""Pydantic schemas for Role validation."""

from typing import List
from pydantic import BaseModel


class ListSchema(BaseModel):
    """List query schema."""

    limit: int = 1000
    offset: int = 0
