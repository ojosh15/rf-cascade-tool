from datetime import datetime

from pydantic import ConfigDict, BaseModel as PydanticBase
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.models import SQLAlchemyBase

class User(SQLAlchemyBase):
    __tablename__ = "users"

    # Primary Keys
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Columns
    email: Mapped[str] = mapped_column(unique=True)
    full_name: Mapped[str] = mapped_column()
    disabled: Mapped[bool] = mapped_column(default=False)

# Pydantic Models
class UserCreateModel(PydanticBase):
    model_config = ConfigDict(from_attributes=True)
    email: str
    full_name: str
    password: str

class UserModel(PydanticBase):
    model_config = ConfigDict(from_attributes=True)
    email: str
    full_name: str
    disabled: bool = False

class UserInputModel(UserModel):
    model_config = ConfigDict(from_attributes=True)
    hashed_password: str

class UserResponseModel(UserModel):
    model_config = ConfigDict(from_attributes=True)
    id: int

class UserPatchModel(PydanticBase):
    model_config = ConfigDict(from_attributes=True)
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None