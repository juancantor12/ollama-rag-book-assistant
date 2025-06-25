"""Authentication module for the api."""

from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, Request, HTTPException, status
from passlib.context import CryptContext
import jwt
from api.db import Database
from api.models.user import User
from app.utils import Utils


def get_token(request: Request) -> str:
    """Extracts the token from the Authorization header."""
    token = request.cookies.get("token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing access token",
        )
    return token


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
    Utils.logger.info(token_data)
    Utils.logger.info(
        Utils.API_SECRET_KEY,
    )
    Utils.logger.info(Utils.API_TOKEN_ALGORITHM)
    encoded_jwt = jwt.encode(
        token_data, Utils.API_SECRET_KEY, algorithm=Utils.API_TOKEN_ALGORITHM
    )
    return encoded_jwt, expiration


def verify_token(token: str = Depends(get_token)) -> dict:
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


def login_request(login_data):
    """Attemps to log in auser and return an access token."""
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    db = Database()
    user = db.session.query(User).filter(User.username == login_data.username).first()
    if (
        not user
        or not pwd_context.verify(login_data.password, user.password)
        or not user.active
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )
    token_data = {
        "idx": user.idx,
        "username": user.username,
        "permissions": user.role.get_role_permissions(),
    }
    token, expiration = generate_access_token(token_data)
    token_data.update({"exp": expiration})
    return (token, token_data)
