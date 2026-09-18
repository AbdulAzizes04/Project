"""Authentication API routes — register, login, profile."""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
import uuid

from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token
from app.core.dependencies import CurrentUser, DbSession
from app.core.config import settings
from app.models.user import User
from app.models.audit import AuditLog
from app.schemas.auth import (
    RegisterRequest, LoginRequest, TokenResponse, UserResponse,
    AuthResponse, RefreshRequest
)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest, db: DbSession):
    """Register a new citizen account."""
    # Check email uniqueness
    existing = db.query(User).filter(User.email == request.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    user = User(
        id=str(uuid.uuid4()),
        email=request.email,
        full_name=request.full_name,
        phone=request.phone,
        password_hash=hash_password(request.password),
        role="citizen",
        is_active=True,
    )
    db.add(user)

    # Audit log
    db.add(AuditLog(
        id=str(uuid.uuid4()),
        user_id=user.id,
        user_email=user.email,
        action="USER_REGISTER",
        resource_type="user",
        resource_id=user.id,
        details={"email": user.email, "role": "citizen"},
    ))
    db.commit()

    access_token = create_access_token(user.id, user.role)
    refresh_token = create_refresh_token(user.id)

    return AuthResponse(
        success=True,
        message="Account created successfully.",
        user=UserResponse.model_validate(user),
        access_token=access_token,
        token_type="bearer",
        tokens=TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        ),
    )


@router.post("/login", response_model=AuthResponse)
def login(request: LoginRequest, db: DbSession):
    """Login with email and password. Returns JWT tokens."""
    user = db.query(User).filter(User.email == request.email).first()

    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been deactivated. Please contact support.",
        )

    access_token = create_access_token(user.id, user.role)
    refresh_token = create_refresh_token(user.id)

    # Audit log
    db.add(AuditLog(
        id=str(uuid.uuid4()),
        user_id=user.id,
        user_email=user.email,
        action="USER_LOGIN",
        resource_type="user",
        resource_id=user.id,
    ))
    db.commit()

    return AuthResponse(
        success=True,
        message="Login successful.",
        user=UserResponse.model_validate(user),
        access_token=access_token,
        token_type="bearer",
        tokens=TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        ),
    )


@router.get("/me", response_model=UserResponse)
def get_me(current_user: CurrentUser):
    """Get the currently authenticated user's profile."""
    return UserResponse.model_validate(current_user)


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(request: RefreshRequest, db: DbSession):
    """Get a new access token using a refresh token."""
    from app.core.security import decode_token
    from jose import JWTError

    try:
        payload = decode_token(request.refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        user_id = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return TokenResponse(
        access_token=create_access_token(user.id, user.role),
        refresh_token=create_refresh_token(user.id),
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
