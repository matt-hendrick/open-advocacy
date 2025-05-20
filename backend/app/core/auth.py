from datetime import datetime, timedelta
from uuid import UUID

from jose import JWTError, jwt
import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings

from app.models.pydantic.models import UserRole, User

# Auth configuration
SECRET_KEY = settings.AUTH_SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password utilities
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def verify_password(plain_password, hashed_password):
    password_bytes = plain_password.encode("utf-8")
    hashed_bytes = (
        hashed_password.encode("utf-8")
        if isinstance(hashed_password, str)
        else hashed_password
    )
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def get_password_hash(password):
    password_bytes = password.encode("utf-8")
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed.decode("utf-8")


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# Authentication dependencies
async def get_current_user(token: str = Depends(oauth2_scheme)):
    from app.services.service_factory import get_cached_user_service

    user_service = get_cached_user_service()
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await user_service.get_user(UUID(user_id))
    if user is None or not user.is_active:
        raise credentials_exception
    return user


# Permission dependencies
async def get_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Dependency to get the current active user."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user"
        )
    return current_user


async def get_group_admin_user(current_user: User = Depends(get_active_user)):
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.GROUP_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return current_user


async def get_super_admin_user(current_user: User = Depends(get_active_user)):
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return current_user


async def get_editor_user(current_user: User = Depends(get_active_user)):
    if current_user.role not in [
        UserRole.SUPER_ADMIN,
        UserRole.GROUP_ADMIN,
        UserRole.EDITOR,
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return current_user
