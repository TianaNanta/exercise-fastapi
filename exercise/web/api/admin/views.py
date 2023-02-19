from typing import List

from fastapi import APIRouter, Depends

from exercise.db.dao.admin_dao import AdminDAO
from exercise.db.models.admin_model import AdminModel
from exercise.web.api.admin.schema import DummyModelDTO, DummyModelInputDTO

router = APIRouter()


@router.get("/", response_model=List[DummyModelDTO])
async def get_admin_models(
    limit: int = 10,
    offset: int = 0,
    admin_dao: AdminDAO = Depends(),
) -> List[AdminModel]:
    """
    Retrieve all admin objects from the database.

    :param limit: limit of admin objects, defaults to 10.
    :param offset: offset of admin objects, defaults to 0.
    :param admin_dao: DAO for admin models.
    :return: list of admin obbjects from database.
    """
    return await admin_dao.get_all_admin(limit=limit, offset=offset)


@router.post("/")
async def create_admin_model(
    new_admin_object: DummyModelInputDTO,
    admin_dao: AdminDAO = Depends(),
) -> None:
    """
    Creates admin model in the database.

    :param new_admin_object: new admin model item.
    :param admin_dao: DAO for admin models.
    """
    await admin_dao.create_admin_model(**new_admin_object.dict())
