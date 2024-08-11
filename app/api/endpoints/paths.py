from http import HTTPStatus

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select, null, func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from database import get_db
from database.models.paths import *
from database.models.projects import *

router = APIRouter(prefix='/paths', tags=["Paths"])


@router.get("", response_model=list[PathResponseModel])
def get_paths(db: Session = Depends(get_db)):
    """Get all paths"""
    stmt = select(Path)
    paths = db.execute(stmt).scalars().all()
    paths = [PathResponseModel.model_validate(path) for path in paths]
    return paths


@router.post("", status_code=HTTPStatus.CREATED, response_model=PathResponseModel)
def post_path(project_id: int, body: PathInputModel, db: Session = Depends(get_db)):
    """Create path for project with `project_id`"""
    project = db.query(Project).filter(Project.id == project_id).one_or_none()
    if project is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"No project found with project ID: {project_id}")
    
    path = Path(**body.model_dump(),project_id=project_id)
    try:
        db.add(path)
        db.flush()
    except IntegrityError as e:
        err_msg = str(e)
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=err_msg)
    project.modified_at = func.current_timestamp()
    path = PathResponseModel.model_validate(path)
    return path


@router.get("/{path_id}", response_model=PathResponseModel)
def get_project_path(project_id: int, path_id: int, db: Session = Depends(get_db)):
    """Get path with `path_id` from project with `project_id`"""
    path = db.query(Path).filter(Path.project_id == project_id, Path.id == path_id).one_or_none()
    if path is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"Path with ID: {path_id} in project with ID: {project_id} not found")
    path = PathResponseModel.model_validate(path)
    return path


@router.put("/{path_id}", response_model=PathResponseModel)
def put_project_path(project_id: int, path_id: int, body: PathInputModel, db: Session = Depends(get_db)):
    """Update path with `path_id` from project with `project_id`"""
    project = db.query(Project).filter(Project.id == project_id).one_or_none()
    if project is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"No project found with project ID: {project_id}")
    
    path = db.query(Path).filter(Path.project_id == project_id, Path.id == path_id).one_or_none()
    if path is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"Path with ID: {path_id} in project with ID: {project_id} not found")
    
    for field, value in body.model_dump().items():
        setattr(path, field, value)
    path.modified_at = func.current_timestamp()
    project.modified_at = func.current_timestamp()
    try:
        db.flush()
        path = PathResponseModel.model_validate(path)
        db.commit()
    except IntegrityError as e:
        err_msg = str(e)

        # If it wasn't a unique or foreign key constraint, something else went wrong
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=err_msg)
    return path

@router.delete("/{path_id}")
def delete_project_path(project_id: int, path_id: int, db: Session = Depends(get_db)):
    """Delete path with `path_id` from project with `project_id`"""
    project = db.query(Project).filter(Project.id == project_id).one_or_none()
    if project is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"No project found with project ID: {project_id}")
    
    num_deleted = db.query(Path).filter(Path.project_id == project_id, Path.id == path_id).delete()
    if num_deleted == 0:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"Path with ID: {path_id} in project with ID: {project_id} not found")
    project.modified_at = func.current_timestamp()
    return {"num_deleted": num_deleted}


@router.get("/{path_id}/stackups", response_model=list[StackupResponseModel])
def get_project_path_stackups(path_id: int, db: Session = Depends(get_db)):
    """Get stackups from path with `path_id`"""
    stmt = select(Stackup).where(Stackup.path_id == path_id)
    stackups = db.execute(stmt).scalars().all()
    stackups = [StackupResponseModel.model_validate(stackup) for stackup in stackups]
    return stackups


@router.post("/{path_id}/stackups", status_code=HTTPStatus.CREATED, response_model=list[StackupResponseModel])
def create_stackup(path_id: int, body: list[StackupInputModel], db: Session = Depends(get_db)):
    """Create a stackup on path with `path_id`"""
    # Query for existing stackups on the given path
    path = db.query(Path).filter(Path.id == path_id).one()
    if not path:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"Path with ID: {path_id} not found")
    if path.stackup:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=f"Stackups for path with ID: {path_id} already exist. Use PUT route or DELETE and try again.")
    
    for stackup_body in body:
        stackup = Stackup(**stackup_body.model_dump(), path_id=path_id)
        path.stackup.append(stackup)
        db.flush()

        if len(path.stackup) > 1:
            path.stackup[-1].next_stackup_id = stackup.id
            db.flush()
    
    path.modified_at = func.current_timestamp()
    stackups = [StackupResponseModel.model_validate(stackup) for stackup in path.stackup]
    db.commit()       
        
    return stackups

@router.post("/{path_id}/stackup/insert", status_code=HTTPStatus.CREATED, response_model=StackupResponseModel)
def insert_stackup(path_id: int, body: StackupInputModel, db: Session = Depends(get_db)):
    """Create a stackup on path with `path_id`"""
    # Query for the last stackup on the given path where next_stackup_id is null/None
    last_stackup = db.query(Stackup).filter(Stackup.path_id == path_id, Stackup.next_stackup_id == null()).first()
    stackup = Stackup(**body.model_dump(),path_id=path_id)
    db.add(stackup)
    db.flush()

    # Update the next_stackup_id of the last stackup
    if last_stackup is not None:
        last_stackup.next_stackup_id = stackup.id
        db.flush()

    stackup = StackupResponseModel.model_validate(stackup)
    db.commit()       
        
    return stackup

@router.delete("/{path_id}/stackups")
def delete_path_stackups(path_id: int, db: Session = Depends(get_db)):
    """Delete stackups with `path_id`"""
    num_deleted = db.query(Stackup).filter(Stackup.path_id == path_id).delete()
    if num_deleted == 0:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"No stackups found with path ID: {path_id}")