from datetime import timedelta
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from exercise.db.dao.admin_dao import AdminDAO
from exercise.db.models.admin_model import AdminModel
from exercise.settings import settings
from exercise.web.api.admin.schema import AdminBase, AdminCreate, AdminShow, Token

router = APIRouter()

ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_time

""" GET METHOD """

@router.get("/", response_model=List[AdminShow])
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

@router.get("/me", response_model=AdminShow)
async def read_admin_me(
    current_admin: AdminShow = Depends(AdminDAO.get_current_active_admin),
    ):
    return current_admin


""" POST METHOD """

@router.post("/")
async def create_admin_model(
    new_admin_object: AdminCreate,
    admin_dao: AdminDAO = Depends(),
) -> None:
    """
    Creates admin model in the database.

    :param new_admin_object: new admin model item.
    :param admin_dao: DAO for admin models.
    """
    await admin_dao.create_admin_model(**new_admin_object.dict())
    
@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    admin_dao: AdminDAO = Depends(),
    ):
    user = await admin_dao.authenticate_admin(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await admin_dao.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}
    

""" PUT METHOD """

@router.put("/avatar")
async def add_admin_pic(
    admin_id: int,
    avatar: bytes = File(...),
    admin_dao: AdminDAO = Depends(),
) -> None:
    """
    Add pic to admin model in database.
    
    :param admin_modif: admin model item with avatar.
    :param admin_dao: DAO
    """
    await admin_dao.update_admin_avatar(admin_id, avatar)

""" DELETE METHOD """

@router.delete("/{admin_id}")
async def delete_admin_model(
    admin_id: int,
    admin_dao: AdminDAO = Depends(),
) -> None:
    """
    Delete admin model from database.

    :param admin_id: id of admin model to delete.
    :param admin_dao: DAO for admin models.
    """
    await admin_dao.delete_admin(admin_id)