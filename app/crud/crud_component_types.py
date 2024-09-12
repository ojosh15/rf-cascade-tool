from sqlalchemy import select, delete
from sqlalchemy.orm import Session
from app.database.models.components import *

def add_component_type(db: Session, comp_type: ComponentType) -> ComponentType:
    try:
        db.add(comp_type)
        db.commit()
        db.refresh(comp_type)
    except Exception as e:
        db.rollback()
        raise e
    return comp_type

def get_component_types(db: Session) -> List[ComponentType]:
    stmt = select(ComponentType)
    comp_types = db.execute(stmt).scalars().all()
    return comp_types

def delete_component_types(db: Session) -> None:
    stmt = delete(ComponentType)
    db.execute(stmt)
    return

def update_component_type(db: Session, comp_type_id: int, comp_type: ComponentTypePatchModel) -> ComponentType | None:
    stmt = select(ComponentType).where(ComponentType.id == comp_type_id)
    comp_type = db.execute(stmt).scalar_one_or_none()
    if comp_type is None:
        return None
    
    [setattr(comp_type, key, value) for key, value in comp_type.model_dump().items()]

    try:
        db.flush()
        db.commit()
        db.refresh(comp_type)
    except Exception as e:
        db.rollback()
        raise e
    return comp_type


def delete_component_type(db: Session, comp_type_id: int) -> bool:
    stmt = select(ComponentType).where(ComponentType.id == comp_type_id)
    comp_type = db.execute(stmt).scalar_one_or_none()
    if comp_type is None:
        return False
    db.delete(comp_type)
    return True