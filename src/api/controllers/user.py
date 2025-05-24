"""Controller for the User."""

from typing import Optional, Union
from pydantic import ValidationError
from api.models.user import User
from api.schemas.user import UserCreate, UserGet
from api.db import Database


class UserController:
    """Controller for the User."""

    def __init__(self):
        db = Database()
        self.collection = db.get_collection("users")

    def get(self, idx: str, filters: Optional[dict] = {}) -> Union[None, User]:
        """
        Returns a user based on the provided Id and if is look for active
        returns None if not found.
        """
        result = 
        user_data = UserCreate.parse_obj(data)
        return self.collection.get(
            ids = [idx],
            where = filters
        )

    def create(self, data: dict) -> Union[None, User]:
        """
        Registers a new user to the database.
        """
        try:
            # Validate the input data with the Pydantic schema
            user_data = UserCreate(**data)  # validate and parse incoming data

            # Now that data is validated, we can create the user object
            user = User(
                username=user_data.username,
                password=user_data.password,  # you would typically hash this in a real-world scenario
                role=user_data.role
            )

            # Get the user collection from the database
            collection = db.get_collection('users')  # assuming the collection name is 'users'

            # Insert the user into the collection (you could also use other ORM methods if you use something like MongoDB or SQLAlchemy)
            inserted_user = collection.insert_one(user.dict())  # You would call .dict() to convert the user model to a dictionary

            # Return the inserted user with necessary details
            # Assuming the inserted user has an '_id' field if it's MongoDB, you may want to exclude this from the output
            user.id = inserted_user.inserted_id  # assume the DB returns an ID upon insertion

            return {"id": str(user.id), "username": user.username, "role": user.role}

        except ValidationError as e:
            # Handle invalid data (e.g., missing required fields)
            return {"error": str(e)}, 400  # return an error message with a 400 status code

        except Exception as e:
            # Handle other unexpected errors
            return {"error": "An error occurred while creating the user", "details": str(e)}, 500
