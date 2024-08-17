from http import HTTPStatus

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.database.models.components import *

router = APIRouter(prefix='/components', tags=["Components"])

@router.get("", response_model=list[ComponentResponseModel])
def get_components(db: Session = Depends(get_db)):
    """Get all components"""
    stmt = select(Component)
    components = db.execute(stmt).scalars().all()
    components = [ComponentResponseModel.model_validate(component) for component in components]
    return components


@router.post("", status_code=HTTPStatus.CREATED, response_model=ComponentResponseModel)
def post_component(body: ComponentInputModel, db: Session = Depends(get_db)):
    """Create a new component"""
    component = Component(**body.model_dump())
    try:
        db.add(component)
        db.flush()  # Needed to get the autoincremented id into the radio object
        ComponentResponseModel.model_validate(component)
    except IntegrityError as e:
        err_msg = str(e)

        # If it wasn't a unique or foreign key constraint, something else went wrong
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=err_msg)
    return component


@router.delete("")
def delete_components(db: Session = Depends(get_db)):
    """Delete all components"""
    num_deleted = db.query(Component).delete()
    return {"num_deleted": num_deleted}


@router.put("/{component_id}", response_model=ComponentResponseModel)
def update_component(component_id: int, body: ComponentInputModel, db: Session = Depends(get_db)):
    """Update component with `component_id`"""
    component = db.query(Component).filter(Component.id == component_id).one_or_none()
    if component is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"Component with ID: {component_id} not found")
    for field, value in body.model_dump().items():
        setattr(component, field, value)

    try:
        db.flush()
        component = ComponentResponseModel.model_validate(component)
        db.commit()
    except IntegrityError as e:
        err_msg = str(e)

        # If it wasn't a unique or foreign key constraint, something else went wrong
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=err_msg)
    return component


@router.post("/{component_id}/data", response_model=ComponentDataResponseModel)
def post_component_data(component_id: int, body: ComponentDataInputModel, db: Session = Depends(get_db)):
    """Create data entry for component with `component_id`"""
    component_data = ComponentData(**body.model_dump())

    try:
        db.add(component_data)
        db.flush()
        component_data = ComponentDataResponseModel.model_validate(component_data)
    except IntegrityError as e:
        err_msg = str(e)

        # If it wasn't a unique or foreign key constraint, something else went wrong
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=err_msg)
    return component_data


@router.get("/{component_id}/versions}", response_model=list[ComponentVersionResponseModel])
def get_component_versions(component_id: int, db: Session = Depends(get_db)):
    """Get versions of component with `component_id`"""
    component = db.query(Component).filter(Component.id == component_id).one_or_none()
    if component is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"Component with ID: {component_id} not found")
    component_versions = [ComponentVersionResponseModel.model_validate(component_version) for component_version in component.component_versions]
    return component_versions


@router.post("/{component_id}/versions}", response_model=ComponentVersionResponseModel)
def post_component_version(component_id: int, body: ComponentVersionInputModel, db: Session = Depends(get_db)):
    """Create version for component with `component_id`"""
    version = db.query(func.max(ComponentVersion.version)).filter(ComponentVersion.component_id == component_id).scalar()
    if version is None:
        version = 0
    version = version + 1
    component_version = ComponentVersion(**body.model_dump(), component_id = component_id, is_verified = False, version = version)
    try:
        db.add(component_version)
        db.flush()  # Needed to get the autoincremented id into the radio object
        component_version = ComponentVersionResponseModel.model_validate(component_version)
    except IntegrityError as e:
        err_msg = str(e)

        # If it wasn't a unique or foreign key constraint, something else went wrong
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=err_msg)
    return component_version


@router.get("/types", response_model=list[ComponentTypeResponseModel])
def get_component_types(db: Session = Depends(get_db)):
    """Get component types"""
    component_types = db.query(ComponentType).all()
    component_types = [ComponentTypeResponseModel.model_validate(component_type) for component_type in component_types]
    return component_types


@router.post("/types", response_model=ComponentTypeResponseModel)
def post_component_type(body: ComponentTypeInputModel, db: Session = Depends(get_db)):
    """Create a component type"""
    component_type = ComponentType(**body.model_dump())
    try:
        db.add(component_type)
        db.flush()  # Needed to get the autoincremented id into the component_type object
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
def delete_component_types(db: Session = Depends(get_db)):
    num_deleted = db.query(ComponentType).delete()
    return {"num_deleted": num_deleted}


@router.delete("/types/{type_id}")
def delete_component_type(type_id: int, db: Session = Depends(get_db)):
    num_deleted = db.query(ComponentType).filter(ComponentType.id == type_id).delete()
    if num_deleted == 0:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"Component type with ID: {type_id} not found")
    return {"num_deleted": num_deleted}