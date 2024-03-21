from typing import Optional
from datetime import datetime

from pydantic import ConfigDict, BaseModel as PydanticBase
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models import SQLAlchemyBase

class Project(SQLAlchemyBase):
    __tablename__ = "projects"

    # Columns
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(unique=True)
    description: Mapped[Optional[str]] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=func.current_timestamp())
    last_modified: Mapped[datetime] = mapped_column(default=func.current_timestamp(), onupdate=func.current_timestamp())
    paths = relationship("Path", order_by="Path.id", back_populates="project")

# Pydantic Models
class ProjectInputModel(PydanticBase):
    name: str
    description: Optional[str]

class ProjectResponseModel(ProjectInputModel):
    created_at: datetime
    last_modified: datetime
    model_config = ConfigDict(from_attributes=True)
    id: int