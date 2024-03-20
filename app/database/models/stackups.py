from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models import SQLAlchemyBase
from database.models.components import Component

class Stackup(SQLAlchemyBase):
    __tablename__ = "stackups"

    # Columns
    id: Mapped[int] = mapped_column(primary_key=True)
    path_id: Mapped[int] = mapped_column(ForeignKey("paths.id"))
    component_id: Mapped[int] = mapped_column(ForeignKey("components.id"))
    position: Mapped[int] = mapped_column(default=0)

    # Relationships
    component: Mapped["Component"] = relationship()