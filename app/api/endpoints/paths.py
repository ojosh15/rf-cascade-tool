from http import HTTPStatus

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select, null, func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.database.models.paths import *
from app.database.models.stackups import *
from app.database.models.projects import *
from app.crud.crud_paths import *
from app.crud.crud_projects import _update_project_modified_at
from app.utils.rfcascade import analyze, AnalysisParamsModel

router = APIRouter(prefix='/paths', tags=["Paths"])


@router.get("", response_model=list[PathResponseModel])
def get_paths_edpt(db: Session = Depends(get_db)):
    """Get all paths"""
    paths = get_paths(db=db)
    paths = [PathResponseModel.model_validate(path) for path in paths]
    return paths


@router.post("", status_code=HTTPStatus.CREATED, response_model=PathResponseModel)
def post_path_edpt(path: PathInputModel, db: Session = Depends(get_db)):
    """Create a Path"""
    path = Path(**path.model_dump())
    try:
        path = add_path(db=db,path=path)
        db.commit()
    except IntegrityError as e:
        err_msg = str(e)
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=err_msg)
    path = PathResponseModel.model_validate(path)
    return path


@router.delete("", status_code=HTTPStatus.NO_CONTENT)
def delete_all_paths_edpt(db: Session = Depends(get_db)):
    """Delete all paths"""
    delete_paths(db=db)
    db.commit()
    return


@router.get("/{path_id}", response_model=PathResponseModel)
def get_path_edpt(path_id: int, db: Session = Depends(get_db)):
    """Get path with `path_id` from project with `project_id`"""
    path = get_path_by_id(db,path_id)
    if path is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"No Path found with ID: {path_id}")
    path = PathResponseModel.model_validate(path)
    return path


@router.patch("/{path_id}", response_model=PathResponseModel)
def patch_path_edpt(path_id: int, body: PathPatchModel, db: Session = Depends(get_db)):
    """Update path with `path_id`"""
    
    path = get_path_by_id(db,path_id)
    if path is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"No Path found with ID: {path_id}")
    
    path = update_path(db,path,body)
    if not path:
        # If it wasn't a unique or foreign key constraint, something else went wrong
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR)
    db.commit()
    return PathResponseModel.model_validate(path)

@router.delete("/{path_id}", status_code=HTTPStatus.NO_CONTENT)
def delete_path_edpt(path_id: int, db: Session = Depends(get_db)):
    """Delete path with `path_id`"""
    deleted = delete_path(db, path_id)
    if deleted:
        db.commit()


@router.get("/{path_id}/stackup", response_model=list[StackupResponseModel])
def get_path_stackup_edpt(path_id: int, db: Session = Depends(get_db)):
    """Get stackup from path with `path_id`"""
    path = get_path_by_id(db,path_id)
    if path is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"No Path found with ID: {path_id}")

    stackups = [StackupResponseModel.model_validate(stackup) for stackup in path.stackups]
    return stackups


@router.put("/{path_id}/stackup", status_code=HTTPStatus.CREATED, response_model=list[StackupResponseModel])
def create_stackup_edpt(path_id: int, body: list[StackupInputModel], db: Session = Depends(get_db)):
    """Create a stackup on path with `path_id`"""
    # Query for existing stackups on the given path
    path = get_path_by_id(db,path_id)
    if path:
        path.stackups = []
        db.flush()
    
    for stackup_body in body:
        stackup = Stackup(**stackup_body.model_dump(), path_id=path_id)
        path.stackups.append(stackup)
        db.flush()

        if len(path.stackups) > 1:
            path.stackups[-2].next_stackup_id = stackup.id
            db.flush()
    
    path.modified_at = func.current_timestamp()
    _update_project_modified_at(db,project_ids=path.project_id)
    db.commit()       
    
    stackups = [StackupResponseModel.model_validate(stackup) for stackup in path.stackups]
    return stackups

@router.delete("/{path_id}/stackup",status_code=HTTPStatus.NO_CONTENT)
def delete_path_stackups_edpt(path_id: int, db: Session = Depends(get_db)):
    """Delete stackup for path with `path_id`"""
    path = get_path_by_id(db,path_id)
    if not path:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"No path found with path ID: {path_id}")
    
    path.stackups = []
    db.commit()        
    
@router.post("/{path_id}/analyze")
def analzye_path(path_id: int, params: AnalysisParamsModel, db: Session = Depends(get_db)):
    """Perform cascade analysis for a path with `path_id`"""
    path = get_path_by_id(db,path_id)
    if path is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"No path found with path ID: {path_id}")
    
    results = analyze(path.stackups,params.start_freq,params.stop_freq,params.points_per_mhz)
    return results
    