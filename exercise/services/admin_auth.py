from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from exercise.db.dao.admin_dao import AdminDAO
from exercise.settings import settings
from exercise.web.api.admin.schema import AdminShow, TokenData

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_time

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/admin/login")

async def authenticate_admin(
    email: str,
    password: str,
    admin_dao: AdminDAO = Depends(),
    ):
    """
    Authenticate admin.
    :param email: email of admin.
    :param password: password of admin.
    :return: admin model.
    """
    admin = await admin_dao.get_admin(email)
    if not admin:
        return False
    if not admin_dao.verify_password(password, admin.hashed_password):
        return False
    return admin

async def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create access token.
    :param data: data for token.
    :param expires_delta: timedelta for token expiration.
    :return: access token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_admin(token: str = Depends(oauth2_scheme), admin_dao: AdminDAO = Depends()):
    """
    Get current admin.
    :param token: token of admin.
    :return: admin model.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    admin = await admin_dao.get_admin(email=token_data.username)
    if admin is None:
        raise credentials_exception
    return await admin


async def get_current_active_admin(current_admin: AdminShow = Depends(get_current_admin)):
    """
    Get current active admin.
    :param current_admin: admin model.
    :return: admin model.
    """
    if current_admin.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return await current_admin