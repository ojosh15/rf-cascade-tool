from sqlalchemy import select, delete
from sqlalchemy.orm import Session
from app.database.models.paths import *
from app.crud.crud_projects import _update_project_modified_at

def add_path(db: Session, path: Path) -> Path:
    try:
        db.add(path)
        db.flush()
        db.refresh(path)
        _update_project_modified_at(db=db,project_ids=path.project_id)
    except Exception as e:
        raise e
    return path

def get_paths(db: Session) -> list[Path]:
    stmt = select(Path)
    paths = db.execute(stmt).scalars().all()
    return paths

def delete_paths(db: Session) -> None:
    project_ids = list(set(db.scalars(select(Path.project_id)).all()))
    stmt = delete(Path)
    db.execute(stmt)
    _update_project_modified_at(db=db,project_ids=project_ids)
    return

def get_path_by_id(db: Session, path_id: int) -> Path | None:
    stmt = select(Path).where(Path.id == path_id)
    path = db.execute(stmt).scalar_one_or_none()
    return path

def update_path(db: Session, path: Path, path_patch: PathPatchModel) -> Path | None:
    try:
        [setattr(path, key, value) for key, value in path.model_dump().items()]
        path.modified_at = func.current_timestamp()
        _update_project_modified_at(db,project_ids=path.project_id)
        db.flush()
    except Exception as e:
        raise e
    return path

def delete_path(db: Session, path_id: int) -> bool:
    stmt = select(Path).where(Path.id == path_id)
    path = db.execute(stmt).scalar_one_or_none()
    if path is None:
        return False
    db.delete(path)
    _update_project_modified_at(db,project_ids=path.project_id)
    return True