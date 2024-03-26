from typing import Optional, List
from datetime import datetime

from pydantic import ConfigDict, BaseModel as PydanticBase
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models import SQLAlchemyBase
from database.models.paths import Path

class Project(SQLAlchemyBase):
    __tablename__ = "projects"

    # Primary Keys
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Columns
    name: Mapped[str] = mapped_column(unique=True)
    description: Mapped[Optional[str]] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=func.current_timestamp())
    last_modified: Mapped[datetime] = mapped_column(default=func.current_timestamp(), onupdate=func.current_timestamp())

    # Relationships
    paths: Mapped[List["Path"]] = relationship("Path", back_populates="project")

    def __repr__(self) -> str:
        return f"Project(id={self.id!r}, name={self.name!r}, description={self.description!r}, created_at={self.created_at!r}, last_modified={self.last_modified!r})"

# Pydantic Models
class ProjectInputModel(PydanticBase):
    name: str
    description: Optional[str]

class ProjectResponseModel(ProjectInputModel):
    created_at: datetime
    last_modified: datetime
    model_config = ConfigDict(from_attributes=True)
    id: int