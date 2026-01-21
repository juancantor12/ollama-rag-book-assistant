"""User routes."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from api.controllers.rbac import require_permission
from api.controllers.permission import PermissionController
from api.controllers.role import RoleController
from api.db import Database
from api.schemas.permission import CreatePermissionSchema, UpdatePermissionSchema
from api.schemas.role import CreateRoleSchema, UpdateRoleSchema
from api.schemas.shared import ListSchema

router = APIRouter(tags=["rbac"])
db = Database()


@router.post("/admin/permissions/create")
async def create_permission(
    permissions: List[CreatePermissionSchema],
    _=Depends(require_permission("manage_access")),
):
    """Endpoint for admins to create permissions on the RBAC."""
    permission_controller = PermissionController()
    ln = permission_controller.create(permissions)
    if ln is not None:
        return {"created_records": ln}
    raise HTTPException(status_code=500)


@router.post("/admin/permissions/list")
async def list_permissions(
    query: ListSchema, _=Depends(require_permission("manage_access"))
):
    """Endpoint for admins to see permissions on the RBAC."""
    permission_controller = PermissionController()
    permissions = permission_controller.list(query.limit, query.offset)
    if permissions is not None:
        return permissions
    raise HTTPException(status_code=500)


@router.post("/admin/permissions/delete")
async def delete_permissions(
    idxs: List[int], _=Depends(require_permission("manage_access"))
):
    """Endpoint for admins to delete permissions from the RBAC."""
    permission_controller = PermissionController()
    ln = permission_controller.delete(idxs)
    if ln is not None:
        return {"deleted_record": ln}
    raise HTTPException(status_code=500)


@router.post("/admin/permissions/update")
async def update_permissions(
    permissions: List[UpdatePermissionSchema],
    _=Depends(require_permission("manage_access")),
):
    """Endpoint for admins to update permissions on the RBAC."""
    permission_controller = PermissionController()
    ln = permission_controller.update(permissions)
    if ln is not None:
        return {"updated_records": ln}
    raise HTTPException(status_code=500)


@router.post("/admin/roles/create")
async def create_role(
    roles: List[CreateRoleSchema], _=Depends(require_permission("manage_access"))
):
    """Endpoint for admins to create roles on the RBAC."""
    role_controller = RoleController()
    ln = role_controller.create(roles)
    if ln is not None:
        return {"created_records": ln}
    raise HTTPException(status_code=500)


@router.post("/admin/roles/list")
async def list_roles(query: ListSchema, _=Depends(require_permission("manage_access"))):
    """Endpoint for admins to see roles on the RBAC."""
    role_controller = RoleController()
    roles = role_controller.list(query.limit, query.offset)
    if roles is not None:
        return roles
    raise HTTPException(status_code=500)


@router.post("/admin/roles/delete")
async def delete_roles(idxs: List[int], _=Depends(require_permission("manage_access"))):
    """Endpoint for admins to delete roles from the RBAC."""
    role_controller = RoleController()
    ln = role_controller.delete(idxs)
    if ln is not None:
        return {"deleted_record": ln}
    raise HTTPException(status_code=500)


@router.post("/admin/roles/update")
async def update_roles(
    roles: List[UpdateRoleSchema], _=Depends(require_permission("manage_access"))
):
    """Endpoint for admins to update roles from the RBAC."""
    role_controller = RoleController()
    ln = role_controller.update(roles)
    if ln is not None:
        return {"updated_records": ln}
    raise HTTPException(status_code=500)
