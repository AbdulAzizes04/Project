"""
FastAPI dependency injection functions.
Provides authenticated user, role guards, and database sessions.
"""
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import User

# OAuth2 Bearer token scheme
bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    db: Session = Depends(get_db),
) -> User:
    """
    FastAPI dependency: validates JWT token and returns the current user.
    Raises 401 if token is missing, expired, or invalid.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(credentials.credentials)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if user is None:
        raise credentials_exception

    return user


def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """Ensure the current user is active."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )
    return current_user


def require_role(*roles: str):
    """
    FastAPI dependency factory for role-based access control.
    
    Usage:
        @router.get("/admin", dependencies=[Depends(require_role("admin"))])
    """
    def _check_role(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role(s): {', '.join(roles)}",
            )
        return current_user
    return _check_role


# Convenience role dependencies
require_admin = Depends(require_role("admin"))
require_staff = Depends(require_role("admin", "staff"))
require_citizen = Depends(require_role("citizen", "admin", "staff"))

# Type aliases for cleaner route signatures
CurrentUser = Annotated[User, Depends(get_current_active_user)]
AdminUser = Annotated[User, Depends(require_role("admin"))]
StaffUser = Annotated[User, Depends(require_role("admin", "staff"))]
DbSession = Annotated[Session, Depends(get_db)]
