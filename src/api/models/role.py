"""DB Model for the api roles."""

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from api.db import Base
from api.models.role import Role  # pylint: disable=unused-import

class User(Base):
    """DB Models for the api users."""
    __tablename__ = 'users'

    idx = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role_id = Column(Integer, ForeignKey('roles.idx'), nullable=True)
    active = Column(Boolean, default=True)
    role = relationship("Role", backref="users", lazy="joined")

    def __init__(
        self, username: str, password: str, role_id: int, active: bool = True
    ):
        """Constructor to initialize user data."""
        self.username = username
        self.password = password
        self.role_id = role_id
        self.active = active

    def check_permission(self, permission: str) -> bool:
        """Checks if the user has a specific permission."""
        if permission in self.role.permissions:
            return True
        return False

    def as_dict(self):
        """Convert the model to a dictionary"""
        return {
            "idx": self.idx,
            "username": self.username,
            "password": self.password,
            "role_id": self.role_id,
            "active": self.active
        }
