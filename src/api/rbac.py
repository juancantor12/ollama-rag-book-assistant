"""RBAC Dependency."""

from typing import Callable
from fastapi import Depends, HTTPException, status
from api.auth import get_current_user_permissions
from api.models.user import User


def require_permission(required_permission: str) -> Callable[[User], None]:
    """RBAC Dependency."""

    def permission_dependency(permissions=Depends(get_current_user_permissions)):
        if required_permission not in permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
            )

    return permission_dependency
