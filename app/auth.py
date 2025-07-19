from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.config import settings
from app.models.user_models import User
from app.schemas.user_schemas import TokenData

# 密碼上下文，用於密碼加密和驗證
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# OAuth2 密碼 Bearer 方案
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    驗證明文密碼與哈希密碼是否匹配。

    :param plain_password: str, 明文密碼。
    :param hashed_password: str, 哈希密碼。
    :return: bool, 驗證成功返回 True，否則返回 False。
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    對密碼進行哈希加密。

    :param password: str, 要加密的密碼。
    :return: str, 哈希後的密碼。
    """
    return pwd_context.hash(password)

def get_user(db: Session, username: str) -> Optional[User]:
    """
    根據使用者名稱從資料庫中獲取使用者。

    :param db: Session, 資料庫會話。
    :param username: str, 使用者名稱。
    :return: Optional[User], 找到的使用者或 None。
    """
    return db.query(User).filter(User.username == username).first()

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """
    驗證使用者身份。

    :param db: Session, 資料庫會話。
    :param username: str, 使用者名稱。
    :param password: str, 密碼。
    :return: Optional[User], 驗證成功返回使用者，否則返回 None。
    """
    user = get_user(db, username)
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    創建 JWT 訪問令牌。

    :param data: dict, 要編碼到令牌中的數據。
    :param expires_delta: Optional[timedelta], 令牌過期時間。
    :return: str, 編碼後的 JWT 令牌。
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    從 JWT 令牌中解碼並獲取當前使用者。

    :param token: str, JWT 令牌。
    :param db: Session, 資料庫會話。
    :return: User, 當前使用者。
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    獲取當前活躍的使用者。

    :param current_user: User, 當前使用者。
    :return: User, 當前活躍的使用者。
    """
    if current_user.status != "active":
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_admin_user(current_user: User = Depends(get_current_active_user)) -> User:
    """
    獲取管理員使用者。
    :param current_user: User, 當前活躍的使用者。
    :return: User, 管理員使用者。
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user