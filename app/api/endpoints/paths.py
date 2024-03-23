from http import HTTPStatus

from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from database import Session
from database.models.paths import Path, PathInputModel, PathResponseModel
from database.models.stackups import Stackup, StackupInputModel, StackupResponseModel

router = APIRouter(prefix='/paths', tags=["Paths"])


@router.get("", response_model=list[PathResponseModel])
def get_paths():
    """Get all paths"""
    with Session() as session, session.begin():
        stmt = select(Path)
        paths = session.execute(stmt).scalars().all()
        paths = [PathResponseModel.model_validate(path) for path in paths]
    return paths


@router.get("/{path_id}/stackups", response_model=list[StackupResponseModel])
def get_project_path_stackups(path_id: int):
    """Get stackups from path with `path_id` in project with `project_id`"""
    with Session() as session, session.begin():
        stmt = select(Stackup).where(Stackup.path_id == path_id).order_by(Stackup.position)
        stackups = session.execute(stmt).scalars().all()
        stackups = [StackupResponseModel.model_validate(stackup) for stackup in stackups]
    return stackups


@router.post("/{path_id}/stackups", status_code=HTTPStatus.CREATED, response_model=StackupResponseModel)
def create_stackup(path_id: int, body: StackupInputModel):
    """Create a stackup on path with `path_id`"""
    with Session() as session, session.begin():
        stackup = Stackup(**body.model_dump())
        session.add(stackup)
        session.flush()
        stackup = StackupResponseModel.model_validate(stackup)
    return stackup