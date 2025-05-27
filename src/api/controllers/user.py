# """Controller for the User model."""

# from typing import Optional, Union
# from pydantic import ValidationError
# from api.models.user import User
# from api.schemas.user import UserCreateSchema, GetUserRequestSchema
# from api.db import Database


# class UserController:
#     """Controller for the User."""

#     def __init__(self):
#         self.db = Database()

#     def get_by_idx(self, idx: int, filters: Optional[dict]) -> Union[None, User]:
#         """Returns a user by id."""
#         # user_data = UserCreateSchema.parse_obj(data)
#         # return self.collection.get(
#         #     ids = [idx],
#         #     where = filters
#         # )

#     def create(self, data: dict) -> Union[None, User]:
#         """
#         Registers a new user to the database.
#         """
#         try:
#             user_data = UserCreateSchema(**data)
#             user = User(
#                 username=user_data.username,
#                 password=user_data.password,
#                 role=user_data.role
#             )
#             collection = db.get_collection('users')
#             inserted_user = collection.insert_one(user.dict())
#             user.id = inserted_user.inserted_id
#             return {"id": str(user.id), "username": user.username, "role": user.role}
#         except ValidationError as e:
#             return {"error": str(e)}, 400
#         except Exception as e:
#             return {"error": "An error occurred while creating the user", "details": str(e)}, 500
