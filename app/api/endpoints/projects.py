from http import HTTPStatus

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from database import get_db
from database.models.projects import *
from database.models.paths import *

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("", response_model=list[ProjectResponseModel])
def get_projects(db: Session = Depends(get_db)):
    """Get all projects"""
    projects = db.query(Project).all()
    projects = [ProjectResponseModel.model_validate(project) for project in projects]
    return projects


@router.delete("")
def delete_projects(db: Session = Depends(get_db)):
    """Delete all projects"""
    num_deleted = db.query(Project).delete()       
    return {"num_deleted": num_deleted}


@router.post("", status_code=HTTPStatus.CREATED, response_model=ProjectResponseModel)
def post_project(body: ProjectInputModel, db: Session = Depends(get_db)):
    """Create a project"""
    project = Project(**body.model_dump())
    try:
        db.add(project)
        db.commit() # Update database if changes from session (needed for autoincremented ID)
        db.refresh(project)
        project = ProjectResponseModel.model_validate(project)
    except IntegrityError as e:
        err_msg = str(e)

        # If the project already exists, raise a 409 Conflict
        if "UniqueViolation" in err_msg:
            raise HTTPException(status_code=HTTPStatus.CONFLICT, detail=f"Project with name: {project.name} already exists")

        # If it wasn't a unique constraint, something else went wrong
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=err_msg)
    return project


@router.get("/{project_id}", response_model=ProjectResponseModel)
def get_project(project_id: int, db: Session = Depends(get_db)):
    """Get project with `project_id`"""
    project = db.query(Project).filter(Project.id == project_id).one_or_none()
    if project is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"No project found with project ID: {project_id}")
    project = ProjectResponseModel.model_validate(project)
    return project


@router.patch("/{project_id}", status_code=HTTPStatus.CREATED, response_model=ProjectResponseModel)
def patch_project(project_id: int, body: ProjectPatchModel, db: Session = Depends(get_db)):
    """Update project with `project_id`"""
    project = db.query(Project).filter(Project.id == project_id).one_or_none()
    if project is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"No project found with project ID: {project_id}")
    for field, value in body.model_dump().items():
        if value is not None:
            setattr(project, field, value)

    try:
        db.flush()
        project = ProjectResponseModel.model_validate(project)
        db.commit()
    except IntegrityError as e:
        err_msg = str(e)

        # If the project already exists, raise a 409 Conflict
        if "UniqueViolation" in err_msg:
            raise HTTPException(status_code=HTTPStatus.CONFLICT, detail=f"Project with name: {project.name} already exists")
        
        # If it wasn't a unique constraint, something else went wrong
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=err_msg)
    return project


@router.delete("/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    """Delete project with `project_id`"""
    num_deleted = db.query(Project).filter(Project.id == project_id).delete()
    if num_deleted == 0:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"No project found with project ID: {project_id}")
    return {"num_deleted": num_deleted}


@router.get("/{project_id}/paths", response_model=list[PathResponseModel])
def get_project_paths(project_id: int, db: Session = Depends(get_db)):
    """Get paths for project with `project_id`"""
    project = db.query(Project).filter(Project.id == project_id).one_or_none()
    if project is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"No project found with project ID: {project_id}")
    paths = [PathResponseModel.model_validate(path) for path in project.paths]
    return paths


@router.delete("/{project_id}/paths")
def delete_project_paths(project_id: int, db: Session = Depends(get_db)):
    """Delete paths for project with `project_id`"""
    project = db.query(Project).filter(Project.id == project_id).one_or_none()
    if project is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"No project found with project ID: {project_id}")
    initial_path_count = len(project.paths)
    
    # Delete associated paths for project
    for path in project.paths:
        db.delete(path)

    num_deleted = initial_path_count - len(project.paths) # Get the number of paths deleted
    project.modified_at = func.current_timestamp()
    return {"num_deleted": num_deleted}