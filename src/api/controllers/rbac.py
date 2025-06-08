"""RBAC Dependency."""

from typing import Callable
from fastapi import Depends, HTTPException, status
from api.controllers.auth import verify_token
from api.models.user import User


def require_permission(required_permission: str) -> Callable[[User], None]:
    """RBAC Dependency."""

    def permission_dependency(payload=Depends(verify_token)):
        if required_permission not in payload["permissions"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
            )
        return payload

    return permission_dependency
