"""DB Model for the api RBAC roles."""

from typing import List
from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship
from api.db import Base
from api.models.permission import Permission  # pylint: disable=unused-import

# Many-to-many relation with permission
role_permission = Table(
    "role_permission",
    Base.metadata,
    Column("role_idx", ForeignKey("roles.idx"), primary_key=True),
    Column("permission_idx", ForeignKey("permissions.idx"), primary_key=True),
)


class Role(Base):
    """DB Model for the api RBAC roles."""

    __tablename__ = "roles"

    idx = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    permissions = relationship(
        Permission, secondary=role_permission, back_populates="roles"
    )

    def __init__(self, name: str):
        self.name = name

    def get_role_permissions(self) -> List[str]:
        """Checks if the user has a specific permission."""
        return [permission.name for permission in self.permissions]

    def as_dict(self):
        """Convert the model to a dictionary"""
        return {
            "idx": self.idx,
            "name": self.name,
            "permissions": self.get_role_permissions(),
        }
