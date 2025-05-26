"""Authentication module for the api."""

from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, Header, HTTPException, status
import jwt
from api.models.user import User
from app.utils import Utils


def get_token(authorization: str = Header(...)) -> str:
    """Extracts the token from the Authorization header."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization scheme",
        )
    return authorization[len("Bearer ") :]


def get_current_user_permissions(token: str = Depends(get_token)) -> User:
    """Returns the current user."""
    payload = verify_token(token)
    return payload.get("permissions", "")


def generate_access_token(
    data: dict, expiration_delta: Optional[timedelta] = None
) -> str:
    """
    Generates an access token with a specific or default expiration delta.
    Args:
    data (dict): Data with wich the token will be generated.
    expiration_delta: a python timedelta object with a custom expiration delta.
    Returns:
    str: The JWT token

    """
    # db = Database()
    # user = db.session.query(User).filter(User.idx == payload["idx"]).first()
    if expiration_delta:
        Utils.logger.info(
            "Generating token with custom expiration delta: %s", expiration_delta
        )
        expiration = datetime.utcnow() + expiration_delta
    else:
        expiration = datetime.utcnow() + timedelta(
            minutes=Utils.API_TOKEN_EXPIRE_MINUTES
        )
    token_data = data.copy()
    token_data.update({"exp": expiration})
    encoded_jwt = jwt.encode(
        token_data, Utils.API_SECRET_KEY, algorithm=Utils.API_TOKEN_ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str) -> dict:
    """
    Verifies the provided token.
    Args:
    token (str): The token to verify
    Returns:
    Union[dict, None]: The token payload or None if the token couldnt be verified.
    """
    try:
        payload = jwt.decode(
            token, Utils.API_SECRET_KEY, algorithms=[Utils.API_TOKEN_ALGORITHM]
        )
        return payload
    except jwt.PyJWTError as error:
        Utils.logger.error("Unable to veiry token: %s", error)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        ) from error
