from typing import Optional, List, TYPE_CHECKING
from datetime import datetime

from pydantic import ConfigDict, BaseModel as PydanticBase
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.models import SQLAlchemyBase

if TYPE_CHECKING:
    from app.database.models.paths import Path

class Project(SQLAlchemyBase):
    __tablename__ = "projects"

    # Primary Keys
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Columns
    name: Mapped[str] = mapped_column(unique=True)
    description: Mapped[Optional[str]] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=func.current_timestamp())
    modified_at: Mapped[datetime] = mapped_column(default=func.current_timestamp(), onupdate=func.current_timestamp())

    # Relationships
    paths: Mapped[List["Path"]] = relationship("Path", back_populates="project")

    def __repr__(self) -> str:
        return f"Project(id={self.id!r}, name={self.name!r}, description={self.description!r}, created_at={self.created_at!r}, modified_at={self.modified_at!r})"

# Pydantic Models
class ProjectInputModel(PydanticBase):
    model_config = ConfigDict(from_attributes=True)
    name: str
    description: str | None = None

class ProjectResponseModel(ProjectInputModel):
    model_config = ConfigDict(from_attributes=True)
    created_at: datetime
    modified_at: datetime
    id: int

class ProjectPatchModel(PydanticBase):
    model_config = ConfigDict(from_attributes=True)
    name: str | None = None
    description: str | None = None