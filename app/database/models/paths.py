from typing import Optional, List
from datetime import datetime

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.orderinglist import ordering_list

from pydantic import ConfigDict, BaseModel as PydanticBase
from database.models import SQLAlchemyBase
from database.models.components import Component, ComponentResponseModel

class Path(SQLAlchemyBase):
    __tablename__ = "paths"

    # Primary Key
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Foreign Keys
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))

    # Columns
    input: Mapped[str] = mapped_column()
    output: Mapped[str] = mapped_column()
    description: Mapped[Optional[str]] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=func.current_timestamp())
    modified_at: Mapped[datetime] = mapped_column(default=func.current_timestamp(), onupdate=func.current_timestamp())

    # Relationships
    stackup: Mapped[List["Stackup"]] = relationship("Stackup", back_populates="path")
    project = relationship("Project", back_populates="paths")

    def __repr__(self) -> str:
        return f"Path(id={self.id!r}, input={self.input!r}, output={self.output!r}, description={self.description!r}, created_at={self.created_at!r}, modified_at={self.modified_at!r})"

class Stackup(SQLAlchemyBase):
    __tablename__ = "stackups"

    # Primary Keys
    id: Mapped[int] = mapped_column(primary_key=True)

    # Foreign Keys
    path_id: Mapped[int] = mapped_column(ForeignKey("paths.id"))
    component_id: Mapped[int] = mapped_column(ForeignKey("components.id"))
    next_stackup_id: Mapped[Optional[int]] = mapped_column(ForeignKey("stackups.id"), unique=True)

    # Relationships
    component: Mapped["Component"] = relationship("Component")
    next_stackup: Mapped[Optional["Stackup"]] = relationship("Stackup", remote_side=[id], foreign_keys=[next_stackup_id], uselist=False)
    path: Mapped["Path"] = relationship("Path", back_populates="stackup")

    def __repr__(self) -> str:
        return f"Stackup(id={self.id!r})"

# Pydantic Models
class StackupInputModel(PydanticBase):
    component_id: int

class StackupResponseModel(StackupInputModel):
    model_config = ConfigDict(from_attributes=True)
    path_id: int
    next_stackup_id: Optional[int]
    component: ComponentResponseModel
    id: int

class PathInputModel(PydanticBase):
    input: str
    output: str
    description: Optional[str]

class PathResponseModel(PathInputModel):
    created_at: datetime
    modified_at: datetime
    model_config = ConfigDict(from_attributes=True)
    stackup: List[StackupResponseModel]
    id: int