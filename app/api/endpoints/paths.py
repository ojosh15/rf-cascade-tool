from http import HTTPStatus

from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from database import Session
from database.models.paths import Path, PathInputModel, PathResponseModel

router = APIRouter(prefix='/paths', tags=["Paths"])

@router.get("", response_model=list[PathResponseModel])
def get_paths(project_id: int|None = None):
    """Get all paths"""
    with Session() as session, session.begin():
        if project_id:
            stmt = select(Path).where(Path.project_id == project_id)
        else:
            stmt = select(Path)
        paths = session.execute(stmt).scalars().all()
        paths = [PathResponseModel.model_validate(path) for path in paths]
    return paths