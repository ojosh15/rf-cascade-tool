from typing import Optional
from datetime import datetime, timezone

from pydantic import ConfigDict, BaseModel as PydanticBase
from sqlalchemy import event, func
from sqlalchemy.orm import Mapped, mapped_column

from database.models import SQLAlchemyBase

class Project(SQLAlchemyBase):
    __tablename__ = "projects"

    # Columns
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(unique=True)
    description: Mapped[Optional[str]] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(insert_default=datetime.now(timezone.utc),default=None)
    last_modified: Mapped[datetime] = mapped_column(default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

@event.listens_for(Project, 'before_update')
def set_last_modified(mapper, connection, target):
    target.last_modified = datetime.now(timezone.utc)

# Pydantic Models
class ProjectInputModel(PydanticBase):
    name: str
    description: Optional[str]

class ProjectResponseModel(ProjectInputModel):
    created_at: datetime
    last_modified: datetime
    model_config = ConfigDict(from_attributes=True)
    id: int