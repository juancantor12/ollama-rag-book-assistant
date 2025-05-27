"""User routes."""

# from typing import List
from fastapi import APIRouter, HTTPException
# from api.controllers.rbac import require_permission
# from api.controllers.user import UserController
from api.db import Database
# from api.schemas.user import CreateUserSchema, ListUserSchema, UpdateUserSchema

router = APIRouter(tags=["admin"])
db = Database()

@router.get("/admin/create_db_tables")
# _=Depends(require_permission("create_db_tables"))
async def create_db_tables():
    """Endpoint for admins to generate the api DB tables."""
    if db.create_all_tables():
        return {"message": "The database tables have been created"}
    raise HTTPException( status_code = 500)

# @router.post("/admin/users/create")
# async def create_user(users: List[CreateUserSchema]):
#     """Endpoint for admins to create users."""
#     user_controller = UserController()
#     ln = user_controller.create(users)
#     if ln is not None:
#         return { "created_records": ln }
#     raise HTTPException( status_code = 500)

# @router.post("/admin/users/list")
# async def list_users(query: ListUserSchema):
#     """Endpoint for admins to see users."""
#     user_controller = UserController()
#     users = user_controller.list(query.limit, query.offset)
#     if users is not None:
#         return { "users": users }
#     raise HTTPException( status_code = 500)

# @router.post("/admin/users/delete")
# async def delete_users(idxs: List[int]):
#     """Endpoint for admins to delete users."""
#     user_controller = UserController()
#     ln = user_controller.delete(idxs)
#     if ln is not None:
#         return {"deleted_record": ln}
#     raise HTTPException( status_code = 500)

# @router.post("/admin/users/update")
# async def update_users(users: List[UpdateUserSchema]):
#     """Endpoint for admins to update users."""
#     user_controller = UserController()
#     ln = user_controller.update(users)
#     if ln is not None:
#         return {"updated_records": ln }
#     raise HTTPException(status_code = 500)
