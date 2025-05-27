"""User routes."""

from typing import List
from fastapi import APIRouter, HTTPException

# from api.controllers.rbac import require_permission
from api.controllers.permission import PermissionController
from api.controllers.role import RoleController
from api.db import Database
from api.schemas.permission import CreatePermissionSchema, UpdatePermissionSchema
from api.schemas.role import CreateRoleSchema, UpdateRoleSchema
from api.schemas.shared import ListSchema


router = APIRouter(tags=["rbac"])
db = Database()
# _=Depends(require_permission("create_db_tables"))


@router.post("/admin/permissions/create")
async def create_permission(permissions: List[CreatePermissionSchema]):
    """Endpoint for admins to create permissions on the RBAC."""
    permission_controller = PermissionController()
    ln = permission_controller.create(permissions)
    if ln is not None:
        return {"created_records": ln}
    raise HTTPException(status_code=500)


@router.post("/admin/permissions/list")
async def list_permissions(query: ListSchema):
    """Endpoint for admins to see permissions on the RBAC."""
    permission_controller = PermissionController()
    permissions = permission_controller.list(query.limit, query.offset)
    if permissions is not None:
        return {"permissions": permissions}
    raise HTTPException(status_code=500)


@router.post("/admin/permissions/delete")
async def delete_permissions(idxs: List[int]):
    """Endpoint for admins to delete permissions from the RBAC."""
    permission_controller = PermissionController()
    ln = permission_controller.delete(idxs)
    if ln is not None:
        return {"deleted_record": ln}
    raise HTTPException(status_code=500)


@router.post("/admin/permissions/update")
async def update_permissions(permissions: List[UpdatePermissionSchema]):
    """Endpoint for admins to update permissions on the RBAC."""
    permission_controller = PermissionController()
    ln = permission_controller.update(permissions)
    if ln is not None:
        return {"updated_records": ln}
    raise HTTPException(status_code=500)


@router.post("/admin/roles/create")
async def create_role(roles: List[CreateRoleSchema]):
    """Endpoint for admins to create roles on the RBAC."""
    role_controller = RoleController()
    ln = role_controller.create(roles)
    if ln is not None:
        return {"created_records": ln}
    raise HTTPException(status_code=500)


@router.post("/admin/roles/list")
async def list_roles(query: ListSchema):
    """Endpoint for admins to see roles on the RBAC."""
    role_controller = RoleController()
    roles = role_controller.list(query.limit, query.offset)
    if roles is not None:
        return {"roles": roles}
    raise HTTPException(status_code=500)


@router.post("/admin/roles/delete")
async def delete_roles(idxs: List[int]):
    """Endpoint for admins to delete roles from the RBAC."""
    role_controller = RoleController()
    ln = role_controller.delete(idxs)
    if ln is not None:
        return {"deleted_record": ln}
    raise HTTPException(status_code=500)


@router.post("/admin/roles/update")
async def update_roles(roles: List[UpdateRoleSchema]):
    """Endpoint for admins to update roles from the RBAC."""
    role_controller = RoleController()
    ln = role_controller.update(roles)
    if ln is not None:
        return {"updated_records": ln}
    raise HTTPException(status_code=500)
