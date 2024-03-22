from http import HTTPStatus

from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from database import Session
from database.models.projects import Project, ProjectResponseModel, ProjectInputModel
from database.models.paths import Path, PathInputModel, PathResponseModel

router = APIRouter(prefix="/projects", tags=["Projects"])

def create_project(body: dict):
    with Session() as session, session.begin():
        project = Project(**body)
        try:
            session.add(project)
            session.commit()  # Needed to get the autoincremented id into the radio object
        except IntegrityError as e:
            err_msg = str(e)

            # If the radio already exists, raise a 409 Conflict
            if "UniqueViolation" in err_msg:
                raise HTTPException(status_code=HTTPStatus.CONFLICT)

            # If it wasn't a unique or foreign key constraint, something else went wrong
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=err_msg)

        return project
    
def update_project(id: int, body: dict):
    with Session() as session, session.begin():
        stmt = select(Project).where(Project.id == id)
        project = session.execute(stmt).scalar_one_or_none()
        if project is not None:
            for field, value in body.items():
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
    return create_project(body)


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
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"Project with name: {name}, not found")
    return projects

@router.delete("")
def delete_projects():
    """Delete projects"""
    with Session() as session, session.begin():
        session.query(Project).delete()


@router.post("", status_code=HTTPStatus.CREATED, response_model=ProjectResponseModel)
def post_project(body: ProjectInputModel):
    """Create project"""
    return create_project(body.model_dump())

@router.get("/{project_id}", response_model=ProjectResponseModel)
def get_project(project_id: int):
    """Get project with `project_id`"""
    with Session() as session, session.begin():
        stmt = select(Project).where(Project.id == project_id)
        project = session.execute(stmt).scalar_one_or_none()
        if project is None:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND)
        project = ProjectResponseModel.model_validate(project)
    return project

@router.put("/{project_id}", status_code=HTTPStatus.CREATED, response_model=ProjectResponseModel)
def put_project(project_id: int, body: ProjectInputModel):
    """Update project with `project_id`"""
    return update_project(project_id, body.model_dump())

@router.delete("/{project_id}")
def delete_project(project_id: int):
    """Delete project with `project_id`"""
    with Session() as session, session.begin():
        stmt = select(Project).where(Project.id == project_id)
        project = session.execute(stmt).scalar_one_or_none()
        if project is None:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND)
        session.delete(project)


@router.get("/{project_id}/paths", response_model=list[PathResponseModel])
def get_project_paths(project_id: int):
    """Get paths for project with `project_id`"""
    with Session() as session, session.begin():
        stmt = select(Project).where(Project.id == project_id)
        project = session.execute(stmt).scalar_one_or_none()
        if project is None:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND)
        paths = project.paths
        paths = [PathResponseModel.model_validate(path) for path in paths]
    return paths

@router.delete("/{project_id}/paths")
def delete_project_paths(project_id: int):
    """Delete paths for project with `project_id`"""
    with Session() as session, session.begin():
        stmt = select(Path).where(Path.project_id == project_id)
        paths = session.execute(stmt).scalars().all()
        if paths is None:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND)
        session.delete(paths)

def create_path(project_id: int, body: dict):
    with Session() as session, session.begin():
        path = Path(**body,project_id=project_id)
        try:
            session.add(path)
            session.flush()  # Needed to get the autoincremented id into the path object
        except IntegrityError as e:
            err_msg = str(e)

            # If the radio already exists, raise a 409 Conflict
            if "UniqueViolation" in err_msg:
                raise HTTPException(status_code=HTTPStatus.CONFLICT)

            # If it wasn't a unique or foreign key constraint, something else went wrong
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=err_msg)

        return path


@router.post("/{project_id}/paths", status_code=HTTPStatus.CREATED, response_model=PathResponseModel)
def post_path(project_id: int, body: PathInputModel):
    """Create path for project with `project_id`"""
    return create_path(project_id,body.model_dump())

@router.get("/projects/{project_id}/paths/{path_id}")
def get_project_path(project_id: int, path_id: int):
    """Get path with `path_id` from project with `project_id`"""
    with Session() as session, session.begin():
        stmt = select(Project).join(Path,Project.id == Path.project_id).where(Path.id == path_id)
        path = session.execute(stmt).scalar_one_or_none()
        if path is None:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND)
        path = PathResponseModel.model_validate(path)
    return path