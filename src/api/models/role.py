"""DB Models for the api users."""

from typing import List


class Role:  # pylint: disable=too-few-public-methods
    """Model for the role."""
    def __init__(self, name: str, permissions: List[str]):
        self.name = name
        self.permissions = permissions
