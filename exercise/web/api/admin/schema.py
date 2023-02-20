from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional


class AdminBase(BaseModel):
    """
    Pydantic base model for admin models.

    It returned when accessing admin models from the API.
    """

    name: Optional[str]
    email: EmailStr

    class Config:
        orm_mode = True


class AdminCreate(AdminBase):
    """Model for creating new admin model."""

    password: str
    
class AdminShow(AdminBase):
    """Model for showing admin model."""

    id: int
    avatar: Optional[bytes]
    date_creation: Optional[datetime]
    
    class Config:
        orm_mode = True
