"""Many-to-many relation with permission."""

from sqlalchemy import Column, ForeignKey, Table
from api.db import Base

role_permission = Table(
    "role_permission",
    Base.metadata,
    Column("role_idx", ForeignKey("roles.idx"), primary_key=True),
    Column("permission_idx", ForeignKey("permissions.idx"), primary_key=True),
)
