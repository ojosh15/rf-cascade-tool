from typing import Optional, List
from datetime import datetime

from sqlalchemy import ForeignKey, JSON, String, Boolean, BigInteger, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.models import SQLAlchemyBase
from app.database.models.sources import SourceEnum
from pydantic import ConfigDict, BaseModel as PydanticBase, field_validator, model_validator


class Component(SQLAlchemyBase):
    __tablename__ = "components"

    # Primary Keys
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Foreign Keys
    component_type_id: Mapped[int] = mapped_column(ForeignKey("component_types.id"))

    # Columns
    model: Mapped[str] = mapped_column(String(50))
    manufacturer: Mapped[str] = mapped_column(String(50))
    serial_no: Mapped[str] = mapped_column(String(50))
    num_ports: Mapped[int] = mapped_column(default=2)
    start_freq: Mapped[BigInteger] = mapped_column(BigInteger, default=0)
    stop_freq: Mapped[BigInteger] = mapped_column(BigInteger, default=18e9)
    is_active: Mapped[bool] = mapped_column(Boolean,default=False)
    is_variable: Mapped[bool] = mapped_column(Boolean,default=False)
    description: Mapped[Optional[str]] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=func.current_timestamp())
    modified_at: Mapped[datetime] = mapped_column(default=func.current_timestamp(), onupdate=func.current_timestamp())

    # Relationships
    type: Mapped["ComponentType"] = relationship("ComponentType")
    component_versions: Mapped[List["ComponentVersion"]] = relationship("ComponentVersion", back_populates="component")
    data_sheets: Mapped[List["DataSheet"]] = relationship("DataSheet", back_populates="component")


class ComponentVersion(SQLAlchemyBase):
    __tablename__ = "component_versions"

    # Primary Keys
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Foreign Keys
    component_id: Mapped[int] = mapped_column(ForeignKey("components.id"))
    component_data_id: Mapped[int] = mapped_column(ForeignKey("component_data.id"))

    # Columns
    version: Mapped[int] = mapped_column()
    change_note: Mapped[str] = mapped_column()
    is_verified: Mapped[bool] = mapped_column()

    # Relationships
    component: Mapped["Component"] = relationship("Component", back_populates="component_versions")
    component_data: Mapped["ComponentData"] = relationship("ComponentData", back_populates="component_version")



class ComponentData(SQLAlchemyBase):
    __tablename__ = "component_data"

    # Primary Keys
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Columns
    data_source: Mapped[SourceEnum] = mapped_column(default=SourceEnum.SIMULATED)
    gain: Mapped[Optional[dict]] = mapped_column(JSON)
    nf: Mapped[Optional[dict]] = mapped_column(JSON)
    ip2: Mapped[Optional[dict]] = mapped_column(JSON)
    ip3: Mapped[Optional[dict]] = mapped_column(JSON)
    p1db: Mapped[Optional[dict]] = mapped_column(JSON)
    max_input: Mapped[Optional[dict]] = mapped_column(JSON)

    # Relationships
    component_version: Mapped["ComponentVersion"] = relationship("ComponentVersion", back_populates="component_data")


class DataSheet(SQLAlchemyBase):
    __tablename__ = "data_sheets"
    
    # Primary Keys
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Foreign Keys
    component_id: Mapped[int] = mapped_column(ForeignKey("components.id"))

    # Columns
    name: Mapped[str] = mapped_column(unique=True)
    extension: Mapped[str] = mapped_column()
    mime_type: Mapped[str] = mapped_column()
    file_path: Mapped[str] = mapped_column(unique=True)

    # Relationships
    component: Mapped["Component"] = relationship("Component", back_populates="data_sheets")


class ComponentType(SQLAlchemyBase):
    __tablename__ = "component_types"

    # Primary Keys
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Columns
    type: Mapped[str] = mapped_column(String(50), unique=True)

    def __repr__(self) -> str:
        return f"ComponentType(id={self.id!r}, type={self.type!r})"


# Pydantic Models
class ComponentTypeInputModel(PydanticBase):
    type: str


class ComponentTypePatchModel(PydanticBase):
    type: str | None = None


class ComponentTypeResponseModel(ComponentTypeInputModel):
    model_config = ConfigDict(from_attributes=True)
    id: int


class ComponentInputModel(PydanticBase):
    model: str
    manufacturer: str
    serial_no: str
    component_type_id: int
    num_ports: int = 2
    start_freq: int = 0
    stop_freq: int = 18e9
    is_active: bool = False
    is_variable: bool = False
    description: Optional[str]


class ComponentPatchModel(PydanticBase):
    model: str | None = None
    manufacturer: str | None = None
    serial_no: str | None = None
    component_type_id: int | None = None
    num_ports: int | None = None
    start_freq: int | None = None
    stop_freq: int | None = None
    is_active: bool | None = None
    is_variable: bool | None = None
    description: str | None = None


class ComponentResponseModel(ComponentInputModel):
    created_at: datetime
    modified_at: datetime
    model_config = ConfigDict(from_attributes=True)
    type: ComponentTypeResponseModel
    id: int


class DataModel(PydanticBase):
    freq: list[int]
    mag: list[float]

    # Validator to ensure freq and mag have at least two elements
    @field_validator("freq", "mag")
    def validate_min_length(cls, v, field):
        if len(v) < 2:
            raise ValueError(f"{field.name} must have at least two elements.")
        return v

    # Validator to ensure freq is in ascending order
    @field_validator("freq")
    def validate_ascending_order(cls, v):
        if v != sorted(v):
            raise ValueError("freq must be in ascending order.")
        return v

    # Model-level validator to check that freq and mag have the same length
    @model_validator(mode="after")
    def validate_equal_length(cls, values):
        freq = values.freq
        mag = values.mag
        if len(freq) != len(mag):
            raise ValueError("freq and mag must have the same length.")
        return values


class ComponentDataInputModel(PydanticBase):
    data_source: SourceEnum
    gain: DataModel | None = None
    nf: DataModel | None = None
    p1db: DataModel | None = None
    ip2: DataModel | None = None
    ip3: DataModel | None = None
    max_input: DataModel | None = None


class ComponentDataPatchModel(PydanticBase):
    data_source: SourceEnum | None = None
    gain: DataModel | None = None
    nf: DataModel | None = None
    p1db: DataModel | None = None
    ip2: DataModel | None = None
    ip3: DataModel | None = None
    max_input: DataModel | None = None


class ComponentDataResponseModel(ComponentDataInputModel):
    model_config = ConfigDict(from_attributes=True)
    id: int


class ComponentVersionInputModel(PydanticBase):
    change_note: str = "Initial component version"
    component_data_id: int = 1
    # version - incremented through endpoint logic
    # is_verified - set to false by endpoint
    # component_id - derived from endpoint URL path parameters
    

class ComponentVersionPatchModel(PydanticBase):
    change_note: str | None = None
    component_data_id: int | None = None
    version: int | None = None
    is_verified: bool | None = None
    component_id: int | None = None


class ComponentVersionResponseModel(ComponentVersionInputModel):
    model_config = ConfigDict(from_attributes=True)
    version: int
    is_verified: bool
    component_id: int
    component_data: ComponentDataResponseModel
    id: int







