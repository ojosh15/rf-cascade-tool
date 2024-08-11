from typing import Optional, List, TYPE_CHECKING
from datetime import datetime

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.orderinglist import ordering_list

from pydantic import ConfigDict, BaseModel as PydanticBase
from database.models import SQLAlchemyBase

if TYPE_CHECKING:
    from database.models.stackups import Stackup

class Path(SQLAlchemyBase):
    __tablename__ = "paths"

    # Primary Key
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Foreign Keys
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))

    # Columns
    input: Mapped[str] = mapped_column()
    output: Mapped[str] = mapped_column()
    description: Mapped[Optional[str]] = mapped_column(default=None)
    created_at: Mapped[datetime] = mapped_column(default=func.current_timestamp())
    modified_at: Mapped[datetime] = mapped_column(default=func.current_timestamp(), onupdate=func.current_timestamp())

    # Relationships
    stackups: Mapped[List["Stackup"]] = relationship("Stackup", back_populates="path")
    project = relationship("Project", back_populates="paths")

    def __repr__(self) -> str:
        return f"Path(id={self.id!r}, input={self.input!r}, output={self.output!r}, description={self.description!r}, created_at={self.created_at!r}, modified_at={self.modified_at!r})"

# Pydantic Models
class PathInputModel(PydanticBase):
    model_config = ConfigDict(from_attributes=True)
    project_id: int
    input: str
    output: str
    description: str | None = None

class PathResponseModel(PathInputModel):
    model_config = ConfigDict(from_attributes=True)
    created_at: datetime
    modified_at: datetime
    id: int

class PathPatchModel(PydanticBase):
    model_config = ConfigDict(from_attributes=True)
    project_id: int | None = None
    input: str | None = None
    output: str | None = None
    description: str | None = None