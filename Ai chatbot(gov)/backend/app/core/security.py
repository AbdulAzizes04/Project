"""
Security utilities: password hashing and JWT token management.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional, Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings


# Password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    subject: str,
    role: str,
    extra_data: Optional[dict] = None,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create a JWT access token.

    Args:
        subject: User ID (UUID string)
        role: User role (citizen / admin / staff)
        extra_data: Optional additional claims
        expires_delta: Token lifetime (defaults to settings value)
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    expire = datetime.now(timezone.utc) + expires_delta

    payload: dict[str, Any] = {
        "sub": str(subject),
        "role": role,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access",
    }

    if extra_data:
        payload.update(extra_data)

    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(subject: str) -> str:
    """Create a longer-lived JWT refresh token."""
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    payload = {
        "sub": str(subject),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "refresh",
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> dict:
    """
    Decode and validate a JWT token.

    Raises:
        JWTError: If the token is invalid or expired
    """
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])


def get_token_subject(token: str) -> Optional[str]:
    """Extract the user ID from a JWT token. Returns None if invalid."""
    try:
        payload = decode_token(token)
        return payload.get("sub")
    except JWTError:
        return None
