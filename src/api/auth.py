"""Authentication module for the api."""

from datetime import datetime, timedelta
from typing import Optional, Union
import jwt
from app.utils import Utils


class Auth:
    """Authentication module for the api."""
    def __init__(self):
        self.secret_key = Utils.API_SECRET_KEY
        self.token_algorithm = Utils.API_TOKEN_ALGORITHM
        self.token_expire_minutes = Utils.API_TOKEN_EXPIRE_MINUTES

    def generate_access_token(
            self, data: dict, expiration_delta: Optional[timedelta] = None
        ) -> str:
        """
        Generates an access token with a specific or default expiration delta.
        Args:
        data (dict): Data with wich the token will be generated.
        expiration_delta: a python timedelta object with a custom expiration delta.
        Returns:
        str: The JWT token

        """
        if expiration_delta:
            Utils.logger.info(
                "Generating token with custom expiration delta: %s", expiration_delta
            )
            expiration = datetime.utcnow() + expiration_delta
        else:
            expiration = datetime.utcnow() + timedelta(minutes=self.token_expire_minutes)
        token_data = data.copy()
        token_data.update({"exp": expiration})
        encoded_jwt = jwt.encode(token_data, self.secret_key, algorithm=self.token_algorithm)
        return encoded_jwt

    def verify_token(self, token: str) -> Union[dict, None]:
        """
        Verifies the provided token.
        Args:
        token (str): The token to verify
        Returns:
        Union[dict, None]: The token payload or None if the token couldnt be verified.
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.token_algorithm])
            return payload
        except jwt.PyJWTError as error:
            Utils.logger.error("Unable to generate token: %s", error)
            return None
