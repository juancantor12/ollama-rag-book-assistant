"""DB Models for the api RBAC permissions."""

from typing import List
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from api.db import Base
from api.models.role_permission import role_permission


class Permission(Base):
    """DB Models for the api RBAC permissions."""

    __tablename__ = "permissions"

    idx = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    roles = relationship(
        "Role",
        secondary=role_permission,
        back_populates="permissions",
        passive_deletes=True,
    )

    def __init__(self, name: str):
        self.name = name

    def get_roles(self) -> List[str]:
        """Gets all roles that has this permission."""
        return [role.name for role in self.roles]

    def as_dict(self):
        """Convert the model to a dictionary"""
        return {
            "idx": self.idx,
            "name": self.name,
            "roles": [r.name for r in self.get_roles()],
        }
