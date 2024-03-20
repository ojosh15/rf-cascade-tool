from typing import Optional, List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.orderinglist import ordering_list

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

    # Foreign Keys
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id",ondelete="CASCADE"))

    # Relationships
    components: Mapped[List["Stackup"]] = relationship(order_by="Stackup.position",
                              collection_class=ordering_list('position'))
