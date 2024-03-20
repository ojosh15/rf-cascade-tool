from typing import Optional
from datetime import datetime, timezone

from sqlalchemy import ForeignKey, event, JSON, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models import SQLAlchemyBase
from database.models.sources import SourceEnum
from database.models.component_types import ComponentType

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
    gain: Mapped[dict] = mapped_column(JSON)
    nf: Mapped[dict] = mapped_column(JSON)
    ip2: Mapped[dict] = mapped_column(JSON)
    ip3: Mapped[dict] = mapped_column(JSON)
    p1db: Mapped[dict] = mapped_column(JSON)
    max_input: Mapped[dict] = mapped_column(JSON)
    is_active: Mapped[bool] = mapped_column(Boolean,default=False)
    is_variable: Mapped[bool] = mapped_column(Boolean,default=False)
    description: Mapped[Optional[str]] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=datetime.now(timezone.utc))
    last_modified: Mapped[datetime] = mapped_column(default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    type: Mapped["ComponentType"] = relationship()

@event.listens_for(Component, 'before_update')
def set_last_modified(mapper, connection, target):
    target.last_modified = datetime.now(timezone.utc)

    