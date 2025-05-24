"""DB Models for the api users."""


class User:  # pylint: disable=too-few-public-methods
    """Model for the user."""
    def __init__(self, idx: int, username: str, password: str, role: str):
        self.idx = idx
        self.username = username
        self.password = password
        self.role = role
