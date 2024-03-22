from typing import Optional
from datetime import datetime

from sqlalchemy import ForeignKey, JSON, String, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models import SQLAlchemyBase
from database.models.sources import SourceEnum
from database.models.component_types import ComponentType
from pydantic import ConfigDict, BaseModel as PydanticBase

class Component(SQLAlchemyBase):
    __tablename__ = "components"

    # Columns
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    model: Mapped[str] = mapped_column(String(50))
    manufacturer: Mapped[str] = mapped_column()
    type_id: Mapped[int] = mapped_column(ForeignKey("component_types.id"))
    source: Mapped[SourceEnum] = mapped_column(default=SourceEnum.SIMULATED)
    start_freq: Mapped[int] = mapped_column(default=0)
    stop_freq: Mapped[int] = mapped_column(default=18e9)
    gain: Mapped[Optional[dict]] = mapped_column(JSON)
    nf: Mapped[Optional[dict]] = mapped_column(JSON)
    ip2: Mapped[Optional[dict]] = mapped_column(JSON)
    ip3: Mapped[Optional[dict]] = mapped_column(JSON)
    p1db: Mapped[Optional[dict]] = mapped_column(JSON)
    max_input: Mapped[Optional[dict]] = mapped_column(JSON)
    is_active: Mapped[bool] = mapped_column(Boolean,default=False)
    is_variable: Mapped[bool] = mapped_column(Boolean,default=False)
    description: Mapped[Optional[str]] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=func.current_timestamp())
    last_modified: Mapped[datetime] = mapped_column(default=func.current_timestamp(), onupdate=func.current_timestamp())

    # Relationships
    type: Mapped[ComponentType] = relationship()

# Pydantic models
class ComponentInputModel(PydanticBase):
    model: str
    manufacturer: str
    type_id: int
    source: SourceEnum
    start_freq: int
    stop_freq: int
    gain: Optional[dict]
    nf: Optional[dict]
    p1db: Optional[dict]
    ip2: Optional[dict]
    ip3: Optional[dict]
    max_input: Optional[dict]
    is_active: bool
    is_variable: bool
    description: Optional[str]

class ComponentResponseModel(ComponentInputModel):
    created_at: datetime
    last_modified: datetime
    model_config = ConfigDict(from_attributes=True)
    id: int










