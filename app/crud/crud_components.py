from sqlalchemy import select, delete
from sqlalchemy.orm import Session
from app.database.models.components import *

def add_component(db: Session, comp: Component) -> Component:
    try:
        db.add(comp)
        db.commit()
        db.refresh(comp)
    except Exception as e:
        db.rollback()
        raise e
    return comp

def get_components(db: Session) -> list[Component]:
    stmt = select(Component)
    components = db.execute(stmt).scalars().all()
    return components

def delete_components(db: Session) -> None:
    stmt = delete(ComponentType)
    db.execute(stmt)
    return

def get_component_by_id(db: Session, comp_id: int) -> Component | None:
    stmt = select(Component).where(Component.id == comp_id)
    component = db.execute(stmt).scalar_one_or_none()
    return component

def update_component(db: Session, comp_id: int, comp: ComponentPatchModel) -> Component | None:
    stmt = select(Component).where(Component.id == comp_id)
    comp = db.execute(stmt).scalar_one_or_none()
    if comp is None:
        return None
    
    [setattr(comp, key, value) for key, value in comp.model_dump().items()]

    try:
        db.flush()
        db.commit()
        db.refresh(comp)
    except Exception as e:
        db.rollback()
        raise e
    return comp

def delete_component(db: Session, comp_id: int) -> bool:
    stmt = select(ComponentType).where(ComponentType.id == comp_id)
    comp = db.execute(stmt).scalar_one_or_none()
    if comp is None:
        return False
    db.delete(comp)
    return True