"""DB Model for the api RBAC users."""

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from api.db import Base
from api.models.role import Role


class User(Base):
    """DB Model for the api RBAC users."""

    __tablename__ = "users"

    idx = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role_id = Column(Integer, ForeignKey("roles.idx"), nullable=True)
    active = Column(Boolean, default=True)
    role = relationship("Role", backref="users", lazy="joined")

    def __init__(self, username: str, password: str, role_id: int, active: bool = True):
        """Constructor to initialize user data."""
        self.username = username
        self.password = password
        self.role_id = role_id
        self.active = active

    def check_permission(self, permission: str) -> bool:
        """Checks if the user has a specific permission."""
        if permission in self.role.get_role_permissions():
            return True
        return False

    def get_role(self) -> Role:
        """
        Returns the user role, also prevents linter for complaining about unused imports
        since SQLAlchemy requires the import but dont use it directly.
        """
        return self.role

    def as_dict(self):
        """Convert the model to a dictionary"""
        return {
            "idx": self.idx,
            "username": self.username,
            "password": self.password,
            "role_id": self.role_id,
            "active": self.active,
            "role": self.role.as_dict(),
        }
