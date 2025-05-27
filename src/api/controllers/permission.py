"""Controller for the Permission model."""

from typing import List
from sqlalchemy import select, delete, update, case
from api.models.permission import Permission
from api.db import Database
from api.schemas.permission import CreatePermissionSchema, UpdatePermissionSchema


class PermissionController:
    """Controller for the Permission model."""

    def __init__(self):
        self.db = Database()

    def create(self, permissions: List[CreatePermissionSchema]) -> int:
        """Adds permissions to the database."""
        new_permissions = []
        for data in permissions:
            new_permissions.append(Permission(name=data.name))
        ln = len(new_permissions)
        self.db.session.add_all(new_permissions)
        self.db.session.commit()
        return ln

    def list(self, limit: int = 1000, offset: int = 0) -> List[Permission]:
        """List all permissions."""
        stmt = select(Permission).limit(limit).offset(offset)
        return list(self.db.session.scalars(stmt))

    def update(self, permissions: List[UpdatePermissionSchema]) -> int:
        """Adds permissions to the database."""
        ln = len(permissions)
        stmt = (
            update(Permission)
            .where(Permission.idx.in_([p.idx for p in permissions]))
            .values(
                {
                    "name": case(
                        {p.idx: p.name for p in permissions}, value=Permission.idx
                    )
                }
            )
        )
        self.db.session.execute(stmt)
        self.db.session.commit()
        return ln

    def delete(self, idxs: List[int]) -> int:
        """Deletes the given permissions by id."""
        ln = len(idxs)
        stmt = delete(Permission).where(Permission.idx.in_(idxs))
        self.db.session.execute(stmt)
        self.db.session.commit()
        return ln
