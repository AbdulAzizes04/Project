"""
Auth Router — JWT login/logout/register
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
import os

from database.db import get_db, User
from schemas import LoginRequest, Token, UserCreate, UserOut

router = APIRouter()

SECRET_KEY = os.getenv("SECRET_KEY", "thyroid-secret-key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    cred_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise cred_exc
    except JWTError:
        raise cred_exc
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise cred_exc
    return user


def ensure_default_admin(db: Session):
    """Create default admin if no users exist."""
    if db.query(User).count() == 0:
        admin = User(
            username="admin",
            email="admin@thyroidai.com",
            hashed_password=get_password_hash("admin123"),
            role="admin",
            full_name="System Administrator",
        )
        db.add(admin)
        db.commit()


@router.post("/login", response_model=Token)
async def login(req: LoginRequest, db: Session = Depends(get_db)):
    ensure_default_admin(db)
    user = db.query(User).filter(User.username == req.username).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = create_access_token({"sub": user.username, "role": user.role})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {"id": user.id, "username": user.username, "role": user.role, "full_name": user.full_name, "email": user.email}
    }


@router.post("/token")
async def token_login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    ensure_default_admin(db)
    user = db.query(User).filter(User.username == form.username).first()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": user.username, "role": user.role})
    return {"access_token": token, "token_type": "bearer"}


@router.post("/register", response_model=UserOut)
async def register(req: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == req.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")
    user = User(
        username=req.username,
        email=req.email,
        hashed_password=get_password_hash(req.password),
        full_name=req.full_name,
        role=req.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
