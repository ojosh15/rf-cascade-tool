from http import HTTPStatus

from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from database import Session
from database.models.components import Component, ComponentInputModel, ComponentResponseModel

router = APIRouter(prefix='/components', tags=["Components"])

@router.get("", response_model=list[ComponentResponseModel])
def get_components():
    """Get all components"""
    with Session() as session, session.begin():
        stmt = select(Component)
        components = session.execute(stmt).scalars().all()
        components = [ComponentResponseModel.model_validate(component) for component in components]
    return components

@router.post("", status_code=HTTPStatus.CREATED, response_model=ComponentResponseModel)
def post_component(body: ComponentInputModel):
    """Create a new component"""
    with Session() as session, session.begin():
        component = Component(**body.model_dump())
        try:
            session.add(component)
            session.flush()  # Needed to get the autoincremented id into the radio object
        except IntegrityError as e:
            err_msg = str(e)

            # If the radio already exists, raise a 409 Conflict
            if "UniqueViolation" in err_msg:
                raise HTTPException(status_code=HTTPStatus.CONFLICT)

            # If it wasn't a unique or foreign key constraint, something else went wrong
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=err_msg)
    return component

@router.delete("")
def delete_components():
    """Delete all components"""
    with Session() as session, session.begin():
        session.query(Component).delete()

@router.put("/{component_id}", response_model=ComponentResponseModel)
def update_component(component_id: int, body: ComponentInputModel):
    """Update component with `component_id`"""
    with Session() as session, session.begin():
        stmt = select(Component).where(Component.id == component_id)
        component = session.execute(stmt).scalar_one_or_none()
        if component is None:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"Component with ID: {component_id} not found")
        for field, value in body.model_dump().items():
            setattr(component, field, value)

        try:
            session.flush()
            component = ComponentResponseModel.model_validate(component)
            session.commit()
        except IntegrityError as e:
            err_msg = str(e)

            # If it wasn't a unique or foreign key constraint, something else went wrong
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=err_msg)
    return component