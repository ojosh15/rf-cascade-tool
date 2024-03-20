from http import HTTPStatus

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from database import Session
from database.models.projects import Project, ProjectResponseModel, ProjectInputModel

router = APIRouter(prefix='/projects')

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
        if project is None:
            return create_project(body.model_dump())
        
        return ProjectResponseModel.model_validate(project)

@router.post("", status_code=HTTPStatus.CREATED, response_model=ProjectResponseModel)
def post_project(body: ProjectInputModel):
    """Add a project"""
    return create_project(body.model_dump())

@router.put("/{id}", response_model=ProjectResponseModel)
def put_project(id: int, body: ProjectInputModel):
    with Session() as session, session.begin():
        stmt = select(Project).where(Project.id == id)
        project = session.execute(stmt).scalar_one_or_none()
        if project is not None:
            for field, value in body.model_dump().items():
                setattr(project, field, value)
            session.commit()
            return ProjectResponseModel.model_validate(project)
    
    return create_project(body.model_dump())

@router.get("", response_model=list[ProjectResponseModel])
def get_projects():
    """Get all projects"""
    with Session() as session, session.begin():
        stmt = select(Project)
        projects = session.execute(stmt).scalars().all()
        projects = [ProjectResponseModel.model_validate(project) for project in projects]

    return projects

@router.get("/{id}", response_model=list[ProjectResponseModel])
def get_project(id: int):
    """Get all projects"""
    with Session() as session, session.begin():
        stmt = select(Project)
        projects = session.execute(stmt).scalars().all()
        projects = [ProjectResponseModel.model_validate(project) for project in projects]

    return projects