from http import HTTPStatus

from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from database import Session
from database.models.projects import Project, ProjectResponseModel, ProjectInputModel
from database.models.paths import Path, PathInputModel, PathResponseModel

router = APIRouter()

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


@router.get("/projects", response_model=list[ProjectResponseModel], tags=["Projects"])
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

@router.delete("/projects", tags=["Projects"])
def delete_projects():
    """Delete projects"""
    with Session() as session, session.begin():
        session.query(Project).delete()


@router.post("/project", status_code=HTTPStatus.CREATED, response_model=ProjectResponseModel, tags=["Project"])
def post_project(body: ProjectInputModel):
    """Create project"""
    return create_project(body.model_dump())

@router.get("/project/{project_id}", response_model=ProjectResponseModel, tags=["Project"])
def get_project(project_id: int):
    """Get project with `project_id`"""
    with Session() as session, session.begin():
        stmt = select(Project).where(Project.id == project_id)
        project = session.execute(stmt).scalar_one_or_none()
        if project is None:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND)
        projects = ProjectResponseModel.model_validate(project)
    return projects

@router.put("/project/{project_id}", status_code=HTTPStatus.CREATED, response_model=ProjectResponseModel, tags=["Project"])
def put_project(project_id: int, body: ProjectInputModel):
    """Update project with `project_id`"""
    return update_project(project_id, body.model_dump())

@router.delete("/project/{project_id}", tags=["Project"])
def delete_project(project_id: int):
    """Delete project with `project_id`"""
    with Session() as session, session.begin():
        stmt = select(Project).where(Project.id == project_id)
        project = session.execute(stmt).scalar_one_or_none()
        if project is None:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND)
        session.delete(project)


@router.get("/project/{project_id}/paths", response_model=list[PathResponseModel], tags=["Project"])
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

@router.delete("/project/{project_id}/paths", tags=["Project"])
def delete_project_paths(project_id: int):
    """Delete paths for project with `project_id`"""


# @router.get("/project/{project_id}/path/")