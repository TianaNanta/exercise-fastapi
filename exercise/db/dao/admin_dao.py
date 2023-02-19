from typing import List, Optional

from fastapi import Depends
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from exercise.db.dependencies import get_db_session
from exercise.db.models.admin_model import AdminModel


class AdminDAO:
    """Class for accessing admin table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def create_admin_model(self, name: str) -> None:
        """
        Add single admin to session.

        :param name: name of a admin.
        """
        self.session.add(AdminModel(name=name))

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
