from datetime import datetime

from sqlalchemy import ForeignKey, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models import SQLAlchemyBase
from database.models.components import Component
from pydantic import ConfigDict, BaseModel as PydanticBase

class Stackup(SQLAlchemyBase):
    __tablename__ = "stackups"

    # Columns
    id: Mapped[int] = mapped_column(primary_key=True)
    path_id: Mapped[int] = mapped_column(ForeignKey("paths.id"))
    component_id: Mapped[int] = mapped_column(ForeignKey("components.id"))
    position: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(default=func.current_timestamp())
    last_modified: Mapped[datetime] = mapped_column(default=func.current_timestamp(), onupdate=func.current_timestamp())

    # # Relationships
    # component: Mapped["Component"] = relationship()

    # Constraints
    __table_args__ = (
        UniqueConstraint('path_id', 'position', name='uq_stackup_path_position'),
    )

# Pydantic models
class StackupInputModel(PydanticBase):
    path_id: int
    component_id: int
    position: int

class StackupResponseModel(StackupInputModel):
    created_at: datetime
    last_modified: datetime
    model_config = ConfigDict(from_attributes=True)
    id: int