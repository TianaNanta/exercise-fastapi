from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import DateTime, LargeBinary, String

from exercise.db.base import Base


class AdminModel(Base):
    """Model for admin."""

    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(length=200))  # noqa: WPS432
    email: Mapped[str] = mapped_column(String(length=200))  # noqa: WPS432
    hashed_password: Mapped[str] = mapped_column(String(length=300))  # noqa: WPS432
    avatar: Mapped[bytes] = mapped_column(LargeBinary(length=300), nullable=True)  # noqa: WPS432
    date_creation: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=True)  # noqa: WPS432
