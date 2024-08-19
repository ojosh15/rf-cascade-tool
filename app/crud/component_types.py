from sqlalchemy.orm import Session
from app.database.models.components import *

def add_component_type(db: Session, comp_type: ComponentTypeInputModel) -> ComponentType:
    new_comp_type = ComponentType(**comp_type.model_dump())
    try:
        db.add(new_comp_type)
        db.commit()
        db.refresh(new_comp_type)
    except Exception as e:
        db.rollback()
        raise e
    return new_comp_type

def get_component_types(db: Session) -> List[ComponentType]:
    comp_types = db.query(ComponentType).all()
    return comp_types

def update_component_type(db: Session, comp_type_id: int, comp_type: ComponentTypeInputModel) -> ComponentType | None:
    current_comp_type = db.query(ComponentType).filter(ComponentType.id == comp_type_id).first()
    if current_comp_type is None:
        return None
    for attr, value in comp_type.model_dump().items():
        setattr(current_comp_type, attr, value) if value else None

    try:
        db.flush()
        db.commit()
        db.refresh(current_comp_type)
    except Exception as e:
        db.rollback()
        raise e
    return current_comp_type


def delete_component_type(db: Session, comp_type_id: int) -> int:
    num_deleted = db.query(ComponentType).filter(ComponentType.id == comp_type_id).delete()
    return num_deleted