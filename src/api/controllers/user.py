"""Controller for the User model."""

from typing import List
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from api.models.user import User
from api.db import Database
from api.schemas.user import CreateUserSchema, UpdateUserSchema


class UserController:
    """Controller for the User model."""

    def __init__(self):
        self.db = Database()
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def create(self, users: List[CreateUserSchema]) -> int:
        """Adds users to the database."""
        new_users = []
        for data in users:
            new_users.append(
                User(
                    username=data.username,
                    password=self.pwd_context.hash(data.password),
                    role_id=data.role_id,
                    active=data.active,
                )
            )
        ln = len(new_users)
        self.db.session.add_all(new_users)
        self.db.session.commit()
        return ln

    def list(self, limit: int = 1000, offset: int = 0) -> List[User]:
        """List all users."""
        stmt = select(User).limit(limit).offset(offset).options(selectinload(User.role))
        return list(self.db.session.scalars(stmt))

    def update(self, users: List[UpdateUserSchema]) -> int:
        """Updates users on the database."""
        ln = len(users)
        for user_data in users:
            user = self.db.session.query(User).get(user_data.idx)
            if not user:
                return None
            user.username = user_data.username
            if user_data.password:
                user.password = self.pwd_context.hash(user_data.password)
            user.role_id = user_data.role_id
            user.active = user_data.active
        self.db.session.commit()
        return ln

    def delete(self, idxs: List[int]) -> int:
        """Deletes the given users by id."""
        ln = len(idxs)
        users_to_delete = self.db.session.query(User).filter(User.idx.in_(idxs)).all()
        for user in users_to_delete:
            self.db.session.delete(user)
        self.db.session.commit()
        return ln
