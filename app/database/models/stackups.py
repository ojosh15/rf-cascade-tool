from typing import Optional, List, TYPE_CHECKING
from datetime import datetime

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.orderinglist import ordering_list

from pydantic import ConfigDict, BaseModel as PydanticBase
from database.models import SQLAlchemyBase
from database.models.components import ComponentVersion, ComponentResponseModel

if TYPE_CHECKING:
    from database.models.paths import Path

class Stackup(SQLAlchemyBase):
    __tablename__ = "stackups"

    # Primary Keys
    id: Mapped[int] = mapped_column(primary_key=True)

    # Foreign Keys
    path_id: Mapped[int] = mapped_column(ForeignKey("paths.id"))
    component_version_id: Mapped[int] = mapped_column(ForeignKey("component_versions.id"))
    next_stackup_id: Mapped[Optional[int]] = mapped_column(ForeignKey("stackups.id"), unique=True)

    # Relationships
    component_version: Mapped["ComponentVersion"] = relationship("ComponentVersion")
    next_stackup: Mapped[Optional["Stackup"]] = relationship("Stackup", remote_side=[id], foreign_keys=[next_stackup_id], uselist=False)
    path: Mapped["Path"] = relationship("Path", back_populates="stackups")

    def __repr__(self) -> str:
        return f"Stackup(id={self.id!r})"

# Pydantic Models
class StackupInputModel(PydanticBase):
    model_config = ConfigDict(from_attributes=True)
    component_id: int

class StackupResponseModel(StackupInputModel):
    model_config = ConfigDict(from_attributes=True)
    path_id: int
    next_stackup_id: int | None = None
    component: ComponentResponseModel
    id: int

class StackupPatchModel(PydanticBase):
    model_config = ConfigDict(from_attributes=True)
    component_id: int | None = None