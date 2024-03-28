from http import HTTPStatus

from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from database import Session
from database.models.components import Component, ComponentInputModel, ComponentResponseModel
from database.models.component_types import ComponentType, ComponentTypeInputModel, ComponentTypeResponseModel

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
            ComponentResponseModel.model_validate(component)
        except IntegrityError as e:
            err_msg = str(e)

            # If it wasn't a unique or foreign key constraint, something else went wrong
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=err_msg)
    return component

@router.delete("")
def delete_components():
    """Delete all components"""
    with Session() as session, session.begin():
        num_deleted = session.query(Component).delete()
    return {"num_deleted": num_deleted}

@router.put("/{component_id}", response_model=ComponentResponseModel)
def update_component(component_id: int, body: ComponentInputModel):
    """Update component with `component_id`"""
    with Session() as session, session.begin():
        component = session.query(Component).filter(Component.id == component_id).one_or_none()
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

@router.get("/types", response_model=list[ComponentTypeResponseModel])
def get_component_types():
    """Get component types"""
    with Session() as session, session.begin():
        component_types = session.query(ComponentType).all()
        component_types = [ComponentTypeResponseModel.model_validate(component_type) for component_type in component_types]
    return component_types

@router.post("/types", response_model=ComponentTypeResponseModel)
def post_component_type(body: ComponentTypeInputModel):
    """Create a component type"""
    with Session() as session, session.begin():
        component_type = ComponentType(**body.model_dump())
        try:
            session.add(component_type)
            session.flush()  # Needed to get the autoincremented id into the component_type object
            component_type = ComponentTypeResponseModel.model_validate(component_type)
        except IntegrityError as e:
            err_msg = str(e)

            # If the type already exists, raise a 409 Conflict
            if "UniqueViolation" in err_msg:
                raise HTTPException(status_code=HTTPStatus.CONFLICT, detail=f"Component of type: {component_type.type} already exists")

            # If it wasn't a unique or foreign key constraint, something else went wrong
            raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=err_msg)
    return component_type

@router.delete("/types")
def delete_component_types():
    with Session() as session, session.begin():
        num_deleted = session.query(ComponentType).delete()
    return {"num_deleted": num_deleted}

@router.delete("/types/{type_id}")
def delete_component_type(type_id: int):
    with Session() as session, session.begin():
        num_deleted = session.query(ComponentType).filter(ComponentType.id == type_id).delete()
        if num_deleted == 0:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"Component type with ID: {type_id} not found")
    return {"num_deleted": num_deleted}