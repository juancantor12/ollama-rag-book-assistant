"""DB Model for the api RBAC roles."""

from typing import List
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from api.db import Base
from api.models.permission import Permission
from api.models.role_permission import role_permission


class Role(Base):
    """DB Model for the api RBAC roles."""

    __tablename__ = "roles"

    idx = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    permissions = relationship(
        Permission,
        secondary=role_permission,
        back_populates="roles",
        passive_deletes=True,
    )

    def __init__(self, name: str, permissions: List[Permission]):
        self.name = name
        self.permissions = permissions

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
