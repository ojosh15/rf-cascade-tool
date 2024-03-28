from http import HTTPStatus

from fastapi import APIRouter, HTTPException
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError

from database import Session
from database.models.projects import Project, ProjectResponseModel, ProjectInputModel
from database.models.paths import Path, PathInputModel, PathResponseModel, Stackup, StackupInputModel, StackupResponseModel

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("", response_model=list[ProjectResponseModel])
def get_projects():
    """Get all projects"""
    with Session() as session, session.begin():
        projects = session.query(Project).all()
        projects = [ProjectResponseModel.model_validate(project) for project in projects]
    return projects


@router.delete("")
def delete_projects():
    """Delete all projects"""
    with Session() as session, session.begin():
        num_deleted = session.query(Project).delete()       
    return {"num_deleted": num_deleted}


@router.post("", status_code=HTTPStatus.CREATED, response_model=ProjectResponseModel)
def post_project(body: ProjectInputModel):
    """Create a project"""
    with Session() as session, session.begin():
        project = Project(**body.model_dump())
        try:
            session.add(project)
            session.flush() # Update database if changes from session (needed for autoincremented ID)
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
def get_project(project_id: int):
    """Get project with `project_id`"""
    with Session() as session, session.begin():
        project = session.query(Project).filter(Project.id == project_id).one_or_none()
        if project is None:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"No project found with project ID: {project_id}")
        project = ProjectResponseModel.model_validate(project)
    return project


@router.put("/{project_id}", status_code=HTTPStatus.CREATED, response_model=ProjectResponseModel)
def put_project(project_id: int, body: ProjectInputModel):
    """Update project with `project_id`"""
    with Session() as session, session.begin():
        project = session.query(Project).filter(Project.id == project_id).one_or_none()
        if project is None:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"No project found with project ID: {project_id}")
        for field, value in body.model_dump().items():
            setattr(project, field, value)

        try:
            session.flush()
            project = ProjectResponseModel.model_validate(project)
            session.commit()
        except IntegrityError as e:
            err_msg = str(e)

            # If the project already exists, raise a 409 Conflict
            if "UniqueViolation" in err_msg:
                raise HTTPException(status_code=HTTPStatus.CONFLICT, detail=f"Project with name: {project.name} already exists")
            
            # If it wasn't a unique constraint, something else went wrong
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=err_msg)
    return project


@router.delete("/{project_id}")
def delete_project(project_id: int):
    """Delete project with `project_id`"""
    with Session() as session, session.begin():
        num_deleted = session.query(Project).filter(Project.id == project_id).delete()
        if num_deleted == 0:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"No project found with project ID: {project_id}")
    return {"num_deleted": num_deleted}


@router.get("/{project_id}/paths", response_model=list[PathResponseModel])
def get_project_paths(project_id: int):
    """Get paths for project with `project_id`"""
    with Session() as session, session.begin():
        project = session.query(Project).filter(Project.id == project_id).one_or_none()
        if project is None:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"No project found with project ID: {project_id}")
        paths = [PathResponseModel.model_validate(path) for path in project.paths]
    return paths


@router.delete("/{project_id}/paths")
def delete_project_paths(project_id: int):
    """Delete paths for project with `project_id`"""
    with Session() as session, session.begin():
        project = session.query(Project).filter(Project.id == project_id).one_or_none()
        if project is None:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"No project found with project ID: {project_id}")
        initial_path_count = len(project.paths)
        
        # Delete associated paths for project
        for path in project.paths:
            session.delete(path)

        num_deleted = initial_path_count - len(project.paths) # Get the number of paths deleted
        project.modified_at = func.current_timestamp()
    return {"num_deleted": num_deleted}
        
        

@router.post("/{project_id}/paths", status_code=HTTPStatus.CREATED, response_model=PathResponseModel)
def post_path(project_id: int, body: PathInputModel):
    """Create path for project with `project_id`"""
    with Session() as session, session.begin():
        project = session.query(Project).filter(Project.id == project_id).one_or_none()
        if project is None:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"No project found with project ID: {project_id}")
        
        path = Path(**body.model_dump(),project_id=project_id)
        try:
            session.add(path)
            session.flush()
        except IntegrityError as e:
            err_msg = str(e)
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=err_msg)
        project.modified_at = func.current_timestamp()
        path = PathResponseModel.model_validate(path)
    return path


@router.get("/{project_id}/paths/{path_id}", response_model=PathResponseModel)
def get_project_path(project_id: int, path_id: int):
    """Get path with `path_id` from project with `project_id`"""
    with Session() as session, session.begin():
        path = session.query(Path).filter(Path.project_id == project_id, Path.id == path_id).one_or_none()
        if path is None:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"Path with ID: {path_id} in project with ID: {project_id} not found")
        path = PathResponseModel.model_validate(path)
    return path


@router.put("/{project_id}/paths/{path_id}", response_model=PathResponseModel)
def put_project_path(project_id: int, path_id: int, body: PathInputModel):
    """Update path with `path_id` from project with `project_id`"""
    with Session() as session, session.begin():
        project = session.query(Project).filter(Project.id == project_id).one_or_none()
        if project is None:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"No project found with project ID: {project_id}")
        
        path = session.query(Path).filter(Path.project_id == project_id, Path.id == path_id).one_or_none()
        if path is None:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"Path with ID: {path_id} in project with ID: {project_id} not found")
        
        for field, value in body.model_dump().items():
            setattr(path, field, value)
        path.modified_at = func.current_timestamp()
        project.modified_at = func.current_timestamp()
        try:
            session.flush()
            path = PathResponseModel.model_validate(path)
            session.commit()
        except IntegrityError as e:
            err_msg = str(e)

            # If it wasn't a unique or foreign key constraint, something else went wrong
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=err_msg)
    return path

@router.delete("/{project_id}/paths/{path_id}")
def delete_project_path(project_id: int, path_id: int):
    """Delete path with `path_id` from project with `project_id`"""
    with Session() as session, session.begin():
        project = session.query(Project).filter(Project.id == project_id).one_or_none()
        if project is None:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"No project found with project ID: {project_id}")
        
        num_deleted = session.query(Path).filter(Path.project_id == project_id, Path.id == path_id).delete()
        if num_deleted == 0:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"Path with ID: {path_id} in project with ID: {project_id} not found")
        project.modified_at = func.current_timestamp()
    return {"num_deleted": num_deleted}