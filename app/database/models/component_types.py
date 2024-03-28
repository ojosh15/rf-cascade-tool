from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from pydantic import ConfigDict, BaseModel as PydanticBase
from database.models import SQLAlchemyBase

class ComponentType(SQLAlchemyBase):
    __tablename__ = "component_types"

    # Primary Keys
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Columns
    type: Mapped[str] = mapped_column(String(50), unique=True)

    def __repr__(self) -> str:
        return f"ComponentType(id={self.id!r}, type={self.type!r})"

# Pydantic Models
class ComponentTypeInputModel(PydanticBase):
    type: str

class ComponentTypeResponseModel(ComponentTypeInputModel):
    model_config = ConfigDict(from_attributes=True)
    id: int