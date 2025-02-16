from sqlalchemy import select, delete, update, func
from sqlalchemy.orm import Session
from app.database.models.projects import *

def add_project(db: Session, project: Project) -> Project:
    try:
        db.add(project)
        db.flush()
        db.refresh(project)
    except Exception as e:
        raise e
    return project

def get_projects(db: Session) -> list[Project]:
    stmt = select(Project)
    projects = db.execute(stmt).scalars().all()
    return projects

def delete_projects(db: Session) -> None:
    stmt = delete(Project)
    db.execute(stmt)
    return

def get_project_by_id(db: Session, project_id: int) -> Project | None:
    stmt = select(Project).where(Project.id == project_id)
    project = db.execute(stmt).scalar_one_or_none()
    return project

def update_project(db: Session, project: Project, project_patch: ProjectPatchModel) -> Project | None:
    try:
        [setattr(project, key, value) for key, value in project.model_dump().items()]
        project.modified_at = func.current_timestamp()
        db.flush()
        db.refresh(project)
    except Exception as e:
        raise e
    return project

def delete_project(db: Session, project_id: int) -> bool:
    stmt = select(Project).where(Project.id == project_id)
    project = db.execute(stmt).scalar_one_or_none()
    if project is None:
        return False
    db.delete(project)
    return True

def _update_project_modified_at(db: Session, project_ids: list[int] | int) -> None:
    """Update the `modified_at` column for the specified projects. (Does not commit changes)"""
    if isinstance(project_ids,int):
        project_ids = [project_ids]

    if project_ids:
        update_stmt = (
            update(Project)
            .where(Project.id.in_(project_ids))
            .values(modified_at=func.now())
        )
        db.execute(update_stmt)