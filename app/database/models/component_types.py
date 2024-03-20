from sqlalchemy.orm import Mapped, mapped_column

from database.models import SQLAlchemyBase

class ComponentType(SQLAlchemyBase):
    __tablename__ = "component_types"

    # Columns
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    type: Mapped[str] = mapped_column(unique=True)