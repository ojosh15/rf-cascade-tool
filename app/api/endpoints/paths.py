from http import HTTPStatus

from fastapi import APIRouter, HTTPException
from sqlalchemy import select, null, func
from sqlalchemy.exc import IntegrityError

from database import Session
from database.models.paths import Path, PathInputModel, PathResponseModel, Stackup, StackupInputModel, StackupResponseModel

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
    """Get stackups from path with `path_id`"""
    with Session() as session, session.begin():
        stmt = select(Stackup).where(Stackup.path_id == path_id)
        stackups = session.execute(stmt).scalars().all()
        stackups = [StackupResponseModel.model_validate(stackup) for stackup in stackups]
    return stackups


@router.post("/{path_id}/stackups", status_code=HTTPStatus.CREATED, response_model=list[StackupResponseModel])
def create_stackup(path_id: int, body: list[StackupInputModel]):
    """Create a stackup on path with `path_id`"""
    with Session() as session, session.begin():
        # Query for existing stackups on the given path
        path = session.query(Path).filter(Path.id == path_id).one()
        if not path:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"Path with ID: {path_id} not found")
        if path.stackup:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=f"Stackups for path with ID: {path_id} already exist. Use PUT route or DELETE and try again.")
        
        for stackup_body in body:
            stackup = Stackup(**stackup_body.model_dump(), path_id=path_id)
            path.stackup.append(stackup)
            session.flush()

            if len(path.stackup) > 1:
                path.stackup[-1].next_stackup_id = stackup.id
                session.flush()
        
        path.modified_at = func.current_timestamp()
        stackups = [StackupResponseModel.model_validate(stackup) for stackup in path.stackup]
        session.commit()       
        
    return stackups

@router.post("/{path_id}/stackup/insert", status_code=HTTPStatus.CREATED, response_model=StackupResponseModel)
def insert_stackup(path_id: int, body: StackupInputModel):
    """Create a stackup on path with `path_id`"""
    with Session() as session, session.begin():
        # Query for the last stackup on the given path where next_stackup_id is null/None
        last_stackup = session.query(Stackup).filter(Stackup.path_id == path_id, Stackup.next_stackup_id == null()).first()
        stackup = Stackup(**body.model_dump(),path_id=path_id)
        session.add(stackup)
        session.flush()

        # Update the next_stackup_id of the last stackup
        if last_stackup is not None:
            last_stackup.next_stackup_id = stackup.id
            session.flush()

        stackup = StackupResponseModel.model_validate(stackup)
        session.commit()       
        
    return stackup

@router.delete("/{path_id}/stackups")
def delete_path_stackups(path_id: int):
    """Delete stackups with `path_id`"""
    with Session() as session, session.begin():
        num_deleted = session.query(Stackup).filter(Stackup.path_id == path_id).delete()
        if num_deleted == 0:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"No stackups found with path ID: {path_id}")