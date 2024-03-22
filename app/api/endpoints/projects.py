from http import HTTPStatus

from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from database import Session
from database.models.projects import Project, ProjectResponseModel, ProjectInputModel
from database.models.paths import Path, PathInputModel, PathResponseModel
from database.models.stackups import Stackup, StackupInputModel, StackupResponseModel

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("", response_model=list[ProjectResponseModel])
def get_projects(name: str|None = None):
    """Get projects"""
    with Session() as session, session.begin():
        if name:
            stmt = select(Project).where(Project.name == name)
        else:
            stmt = select(Project)
        projects = session.execute(stmt).scalars().all()
        if projects:
            projects = [ProjectResponseModel.model_validate(project) for project in projects]
        elif name:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"No project found with name: {name}")
    return projects


@router.delete("")
def delete_projects():
    """Delete projects"""
    with Session() as session, session.begin():
        num_deleted = session.query(Project).delete()
        if num_deleted == 0:
            raise HTTPException(HTTPStatus.NOT_FOUND, detail=f"No projects found")


@router.post("", status_code=HTTPStatus.CREATED, response_model=ProjectResponseModel)
def post_project(body: ProjectInputModel):
    """Create project"""
    with Session() as session, session.begin():
        project = Project(**body.model_dump())
        try:
            session.add(project)
            session.flush()
        except IntegrityError as e:
            err_msg = str(e)

            # If the project already exists, raise a 409 Conflict
            if "UniqueViolation" in err_msg:
                raise HTTPException(status_code=HTTPStatus.CONFLICT)

            # If it wasn't a unique or foreign key constraint, something else went wrong
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=err_msg)
    return project


@router.get("/{project_id}", response_model=ProjectResponseModel)
def get_project(project_id: int):
    """Get project with `project_id`"""
    with Session() as session, session.begin():
        stmt = select(Project).where(Project.id == project_id)
        project = session.execute(stmt).scalar_one_or_none()
        if project is None:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"No project found with project ID: {project_id}")
        project = ProjectResponseModel.model_validate(project)
    return project


@router.put("/{project_id}", status_code=HTTPStatus.CREATED, response_model=ProjectResponseModel)
def put_project(project_id: int, body: ProjectInputModel):
    """Update project with `project_id`"""
    with Session() as session, session.begin():
        stmt = select(Project).where(Project.id == project_id)
        project = session.execute(stmt).scalar_one_or_none()
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

            # If it wasn't a unique or foreign key constraint, something else went wrong
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=err_msg)
    return project


@router.delete("/{project_id}")
def delete_project(project_id: int):
    """Delete project with `project_id`"""
    with Session() as session, session.begin():
        num_deleted = session.query(Project).filter(Project.id == project_id).delete()
        if num_deleted == 0:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"No project found with project ID: {project_id}")


@router.get("/{project_id}/paths", response_model=list[PathResponseModel])
def get_project_paths(project_id: int):
    """Get paths for project with `project_id`"""
    with Session() as session, session.begin():
        stmt = select(Project).where(Project.id == project_id)
        project = session.execute(stmt).scalar_one_or_none()
        if project is None:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"No project found with project ID: {project_id}")
        paths = project.paths
        paths = [PathResponseModel.model_validate(path) for path in paths]
    return paths


@router.delete("/{project_id}/paths")
def delete_project_paths(project_id: int):
    """Delete paths for project with `project_id`"""
    with Session() as session, session.begin():
        num_deleted = session.query(Path).filter(Path.project_id == project_id).delete()
        if num_deleted == 0:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"No paths found for project ID: {project_id}")
        

@router.post("/{project_id}/paths", status_code=HTTPStatus.CREATED, response_model=PathResponseModel)
def post_path(project_id: int, body: PathInputModel):
    """Create path for project with `project_id`"""
    with Session() as session, session.begin():
        path = Path(**body.model_dump(),project_id=project_id)
        try:
            session.add(path)
            session.flush()
        except IntegrityError as e:
            err_msg = str(e)

            # If it wasn't a unique or foreign key constraint, something else went wrong
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=err_msg)
        path = PathResponseModel.model_validate(path)
    return path


@router.get("/{project_id}/paths/{path_id}", response_model=PathResponseModel)
def get_project_path(project_id: int, path_id: int):
    """Get path with `path_id` from project with `project_id`"""
    with Session() as session, session.begin():
        stmt = select(Path).where(Path.project_id == project_id, Path.id == path_id,)
        path = session.execute(stmt).scalar_one_or_none()
        if path is None:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"Path with ID: {path_id} in project with ID: {project_id} not found")
        path = PathResponseModel.model_validate(path)
    return path


@router.put("/{project_id}/paths/{path_id}", response_model=PathResponseModel)
def put_project_path(project_id: int, path_id: int, body: PathInputModel):
    """Update path with `path_id` from project with `project_id`"""
    with Session() as session, session.begin():
        stmt = select(Path).where(Path.project_id == project_id, Path.id == path_id,)
        path = session.execute(stmt).scalar_one_or_none()
        if path is None:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"Path with ID: {path_id} in project with ID: {project_id} not found")
        for field, value in body.model_dump().items():
                setattr(path, field, value)
        try:
            session.flush()
            path = PathResponseModel.model_validate(path)
            session.commit()
        except IntegrityError as e:
            err_msg = str(e)

            # If it wasn't a unique or foreign key constraint, something else went wrong
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=err_msg)
    return path