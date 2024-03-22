from typing import Optional, List
from datetime import datetime

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.orderinglist import ordering_list

from pydantic import ConfigDict, BaseModel as PydanticBase
from database.models import SQLAlchemyBase
from database.models.stackups import Stackup

class Path(SQLAlchemyBase):
    __tablename__ = "paths"

    # Primary Key
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Columns
    input: Mapped[str] = mapped_column()
    output: Mapped[str] = mapped_column()
    description: Mapped[Optional[str]] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=func.current_timestamp())
    last_modified: Mapped[datetime] = mapped_column(default=func.current_timestamp(), onupdate=func.current_timestamp())

    # Foreign Keys
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id",ondelete="CASCADE"))

    # Relationships
    components: Mapped[List["Stackup"]] = relationship(order_by="Stackup.position",
                              collection_class=ordering_list('position'))
    project = relationship("Project", back_populates="paths")

# Pydantic Models
class PathInputModel(PydanticBase):
    input: str
    output: str
    description: Optional[str]

class PathResponseModel(PathInputModel):
    created_at: datetime
    last_modified: datetime
    model_config = ConfigDict(from_attributes=True)
    id: int