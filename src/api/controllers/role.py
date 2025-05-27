"""Controller for the Role model."""

from typing import List
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from api.models.permission import Permission
from api.models.role import Role
from api.db import Database
from api.schemas.role import CreateRoleSchema, UpdateRoleSchema

class RoleController:
    """Controller for the Role model."""
    def __init__(self):
        self.db = Database()

    def create(self, roles: List[CreateRoleSchema]) -> int:
        """Adds roles to the database."""
        new_roles = []
        for data in roles:
            permissions = self.db.session.query(Permission).filter(
                Permission.idx.in_(data.permissions)
            ).all()
            new_roles.append( Role(name = data.name, permissions = permissions) )
        ln = len(new_roles)
        self.db.session.add_all(new_roles)
        self.db.session.commit()
        return ln

    def list(self, limit: int = 1000, offset: int = 0) -> List[Role]:
        """List all roles."""
        stmt = select(Role).limit(limit).offset(offset).options(selectinload(Role.permissions))
        return list(self.db.session.scalars(stmt))

    def update(self, roles: List[UpdateRoleSchema]) -> int:
        """Updates roles on the database."""
        ln = len(roles)
        for role_data in roles:
            role = self.db.session.query(Role).get(role_data.idx)
            if not role:
                return None
            updated_permissions = self.db.session.query(Permission).filter(
                Permission.idx.in_(role_data.permissions)
            ).all()
            role.permissions = []
            role.permissions.extend(updated_permissions)
            role.name = role_data.name
        self.db.session.commit()
        return ln

    def delete(self, idxs: List[int]) -> int:
        """Deletes the given roles by id."""
        ln = len(idxs)
        roles_to_delete = self.db.session.query(Role).filter(Role.idx.in_(idxs)).all()
        for role in roles_to_delete:
            self.db.session.delete(role)
        self.db.session.commit()
        return ln
