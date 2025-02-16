from http import HTTPStatus

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.database.models.projects import *
from app.database.models.paths import *
from app.crud.crud_projects import *

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("", response_model=list[ProjectResponseModel], summary="Get all projects")
def get_projects_edpt(db: Session = Depends(get_db)):
    """Get all projects"""
    projects = get_projects(db=db)
    projects = [ProjectResponseModel.model_validate(project) for project in projects]
    return projects


@router.delete("", status_code=HTTPStatus.NO_CONTENT, summary="Delete all projects")
def delete_projects_edpt(db: Session = Depends(get_db)):
    """Delete all projects"""
    delete_projects(db=db)
    db.commit()
    return


@router.post("", status_code=HTTPStatus.CREATED, response_model=ProjectResponseModel, summary="Create a new project")
def post_project_edpt(body: ProjectInputModel, db: Session = Depends(get_db)):
    """Create a project"""
    project = Project(**body.model_dump())
    try:
        project = add_project(db=db,project=project)
        db.commit()
    except IntegrityError as e:
        err_msg = str(e)

        # If the project already exists, raise a 409 Conflict
        if "UniqueViolation" in err_msg:
            raise HTTPException(status_code=HTTPStatus.CONFLICT, detail=f"Project with name: {project.name} already exists")

        # If it wasn't a unique constraint, something else went wrong
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=err_msg)
    
    project = ProjectResponseModel.model_validate(project)
    return project


@router.get("/{project_id}", response_model=ProjectResponseModel, summary="Get a project by ID")
def get_project_edpt(project_id: int, db: Session = Depends(get_db)):
    """Get project with `project_id`"""
    project = get_project_by_id(db=db,project_id=project_id)
    if project is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"No project found with project ID: {project_id}")
    return ProjectResponseModel.model_validate(project)


@router.patch("/{project_id}", status_code=HTTPStatus.CREATED, response_model=ProjectResponseModel, summary="Update a project by ID")
def patch_project_edpt(project_id: int, updated_project: ProjectPatchModel, db: Session = Depends(get_db)):
    """Update project with `project_id`"""
    project = get_project_by_id(db,project_id)
    if project is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"No project found with project ID: {project_id}")
    try:
        project = update_project(db=db,project=project,project_patch=updated_project)
        db.commit()
    except IntegrityError as e:
        err_msg = str(e)

        # If the project already exists, raise a 409 Conflict
        if "UniqueViolation" in err_msg:
            raise HTTPException(status_code=HTTPStatus.CONFLICT, detail=f"Project with name: {updated_project.name} already exists")
        
        # If it wasn't a unique constraint, something else went wrong
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=err_msg)
    return ProjectResponseModel.model_validate(project)


@router.delete("/{project_id}", status_code=HTTPStatus.NO_CONTENT, summary="Delete a project by ID")
def delete_project_edpt(project_id: int, db: Session = Depends(get_db)):
    """Delete project with `project_id`"""
    deleted = delete_project(db=db,project_id=project_id)
    if deleted:
        db.commit()
    return


@router.get("/{project_id}/paths", response_model=list[PathResponseModel], summary="Get all paths for a project")
def get_project_paths_edpt(project_id: int, db: Session = Depends(get_db)):
    """Get paths for project with `project_id`"""
    project = get_project_by_id(db=db,project_id=project_id)
    if project is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"No project found with project ID: {project_id}")
    paths = [PathResponseModel.model_validate(path) for path in project.paths]
    return paths


@router.delete("/{project_id}/paths", status_code=HTTPStatus.NO_CONTENT, summary="Delete all the paths for a project")
def delete_project_paths_edpt(project_id: int, db: Session = Depends(get_db)):
    """Delete paths for project with `project_id`"""
    project = get_project_by_id(db=db,project_id=project_id)
    if project is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"No project found with project ID: {project_id}")
    
    # Delete associated paths for project
    project.paths = []
    project.modified_at = func.current_timestamp()
    db.commit()
    return