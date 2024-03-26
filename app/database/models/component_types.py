from sqlalchemy.orm import Mapped, mapped_column

from database.models import SQLAlchemyBase

class ComponentType(SQLAlchemyBase):
    __tablename__ = "component_types"

    # Primary Keys
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Columns
    type: Mapped[str] = mapped_column(unique=True)

    def __repr__(self) -> str:
        return f"ComponentType(id={self.id!r}, type={self.type!r})"