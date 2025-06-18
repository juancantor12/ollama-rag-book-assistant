"""User routes."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from api.controllers.rbac import require_permission
from api.controllers.user import UserController
from api.db import Database
from api.models.permission import Permission
from api.models.role import Role
from api.models.user import User
from api.schemas.shared import ListSchema, GetSchemaSchema
from api.schemas.user import CreateUserSchema, UpdateUserSchema

router = APIRouter(tags=["admin"])
db = Database()


@router.get("/admin/create_db_tables")
# _=Depends(require_permission("create_db_tables"))
async def create_db_tables(_=Depends(require_permission("manage_db"))):
    """Endpoint for admins to generate the api DB tables."""
    if db.create_all_tables():
        return {"message": "The database tables have been created"}
    raise HTTPException(status_code=500)


@router.post("/admin/users/create")
async def create_user(
    users: List[CreateUserSchema], _=Depends(require_permission("manage_users"))
):
    """Endpoint for admins to create users."""
    user_controller = UserController()
    ln = user_controller.create(users)
    if ln is not None:
        return {"created_records": ln}
    raise HTTPException(status_code=500)


@router.post("/admin/users/list")
async def list_users(query: ListSchema, _=Depends(require_permission("manage_users"))):
    """Endpoint for admins to see users."""
    user_controller = UserController()
    users = user_controller.list(query.limit, query.offset)
    if users is not None:
        return users
    raise HTTPException(status_code=500)


@router.post("/admin/users/delete")
async def delete_users(idxs: List[int], _=Depends(require_permission("manage_users"))):
    """Endpoint for admins to delete users."""
    user_controller = UserController()
    ln = user_controller.delete(idxs)
    if ln is not None:
        return {"deleted_record": ln}
    raise HTTPException(status_code=500)


@router.post("/admin/users/update")
async def update_users(
    users: List[UpdateUserSchema], _=Depends(require_permission("manage_users"))
):
    """Endpoint for admins to update users."""
    user_controller = UserController()
    ln = user_controller.update(users)
    if ln is not None:
        return {"updated_records": ln}
    raise HTTPException(status_code=500)


@router.post("/admin/get_schema")
async def get_schema(
    query: GetSchemaSchema, _=Depends(require_permission("get_schema"))
):
    """Endpoint for admins to query model schemas."""
    schema_dict = {
        "permission": Permission.__table__,
        "role": Role.__table__,
        "user": User.__table__,
    }
    if query.model_name not in schema_dict:
        raise HTTPException(status_code=404)

    model = schema_dict.get(query.model_name)
    columns = [
        {
            "name": column.name,
            "type": str(column.type),
            "autoincrement": column.autoincrement,
            "index": column.index,
            "unique": column.unique,
            "nullable": column.nullable,
            "primary_key": column.primary_key,
            "comment": column.comment,
        }
        for column in model.columns
    ]
    return columns
