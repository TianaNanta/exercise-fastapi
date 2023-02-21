from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from exercise.db.dependencies import get_db_session
from exercise.db.models.admin_model import AdminModel
from exercise.settings import settings
from exercise.web.api.admin.schema import AdminShow, TokenData


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/admin/login")

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_time


class AdminDAO:
    """Class for accessing admin table."""
        
    
    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session
        
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify password.

        :param plain_password: plain password.
        :param hashed_password: hashed password.
        :return: True if password is correct, False otherwise.
        """
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_hashed_password(self, password: str) -> str:
        """
        Get hashed password.

        :param password: password.
        :return: hashed password.
        """
        return pwd_context.hash(password)
    
    async def get_admin(self, email: str):
        """
        Get admin model by email.

        :param email: email of admin.
        :return: admin model.
        """
        raw_admin = await self.session.execute(
            select(AdminModel).where(AdminModel.email == email),
        )
        
        return raw_admin.scalars().first()
    
    async def authenticate_admin(self, email: str, password: str):
        """
        Authenticate admin.

        :param email: email of admin.
        :param password: password of admin.
        :return: admin model.
        """
        admin = await self.get_admin(email)
        if not admin:
            return False
        if not self.verify_password(password, admin.hashed_password):
            return False
        return admin
    
    async def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
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

    async def create_admin_model(self, name: str, email: str, password: str) -> None:
        """
        Add single admin to session.

        :param name: name of a admin.
        """
        self.session.add(
            AdminModel(
                name=name,
                email=email,
                hashed_password=self.get_hashed_password(password))
            )

    async def get_all_admin(self, limit: int, offset: int) -> List[AdminModel]:
        """
        Get all admin models with limit/offset pagination.

        :param limit: limit of admin.
        :param offset: offset of admin.
        :return: stream of admin.
        """
        raw_admin = await self.session.execute(
            select(AdminModel).limit(limit).offset(offset),
        )

        return list(raw_admin.scalars().fetchall())

    async def filter(
        self,
        name: Optional[str] = None,
    ) -> List[AdminModel]:
        """
        Get specific admin model.

        :param name: name of admin instance.
        :return: admin models.
        """
        query = select(AdminModel)
        if name:
            query = query.where(AdminModel.name == name)
        rows = await self.session.execute(query)
        return list(rows.scalars().fetchall())

    # function to update admin picture/avatar
    async def update_admin_avatar(self, admin_id: int, avatar: bytes) -> None:
        """
        Update admin avatar.

        :param admin_id: id of admin.
        :param avatar: avatar of admin.
        """
        await self.session.execute(update(AdminModel).where(AdminModel.id == admin_id).values(avatar=avatar))

    # function to update admin name
    async def update_admin_name(self, admin_id: int, name: str) -> None:
        """
        Update admin name.

        :param admin_id: id of admin.
        :param name: name of admin.
        """
        await self.session.execute(update(AdminModel).where(AdminModel.id == admin_id).values(name=name))

    # function to update admin email
    async def update_admin_email(self, admin_id: int, email: str) -> None:
        """
        Update admin email.

        :param admin_id: id of admin.
        :param email: email of admin.
        """
        await self.session.execute(update(AdminModel).where(AdminModel.id == admin_id).values(email=email))

    # function to update admin password
    async def update_admin_password(self, admin_id: int, hashed_password: str) -> None:
        """
        Update admin password.

        :param admin_id: id of admin.
        :param hashed_password: hashed password of admin.
        """
        await self.session.execute(update(AdminModel).where(AdminModel.id == admin_id).values(hashed_password=hashed_password))
        
    # function to delete admin
    async def delete_admin(self, admin_id: int) -> None:
        """
        Delete admin.

        :param admin_id: id of admin.
        """
        await self.session.execute(delete(AdminModel).where(AdminModel.id == admin_id))
        
    # function to get admin by id
    async def get_admin_by_id(self, admin_id: int) -> AdminModel:
        """
        Get admin by id.

        :param admin_id: id of admin.
        :return: admin model.
        """
        raw_admin = await self.session.execute(
            select(AdminModel).where(AdminModel.id == admin_id),
        )

        return raw_admin.scalars().first()
    
    # function to get admin by email
    async def get_admin_by_email(self, email: str) -> AdminModel:
        """
        Get admin by email.

        :param email: email of admin.
        :return: admin model.
        """
        raw_admin = await self.session.execute(
            select(AdminModel).where(AdminModel.email == email),
        )

        return raw_admin.scalars().first()
    

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