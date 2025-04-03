from http import HTTPStatus

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.database.models.components import *
from app.crud.crud_component_types import *
from app.crud.crud_components import *

router = APIRouter(prefix='/components', tags=["Components"])

@router.get("", response_model=list[ComponentResponseModel])
def get_components_edpt(db: Session = Depends(get_db)):
    """Get all components"""
    components = get_components(db=db)
    components = [ComponentResponseModel.model_validate(component) for component in components]
    return components


@router.post("", status_code=HTTPStatus.CREATED, response_model=ComponentResponseModel)
def post_component_edpt(body: ComponentInputModel, db: Session = Depends(get_db)):
    """Create a new component"""
    component = Component(**body.model_dump())
    try:
        component = add_component(db=db,comp=component)
        ComponentResponseModel.model_validate(component)
    except IntegrityError as e:
        err_msg = str(e)

        # If it wasn't a unique or foreign key constraint, something else went wrong
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=err_msg)
    return component


@router.delete("", status_code=HTTPStatus.NO_CONTENT)
def delete_components_edpt(db: Session = Depends(get_db)):
    """Delete all components"""
    delete_components(db=db)
    return


@router.get("/{component_id}", response_model=ComponentResponseModel)
def get_component_edpt(component_id: int, db: Session = Depends(get_db)):
    """Get a component with `component_id`"""
    component = get_component_by_id(db=db,comp_id=component_id)
    if component is None:
        raise HTTPException(HTTPStatus.NOT_FOUND, detail=f"Component with ID: {component_id} not found")
    return ComponentResponseModel.model_validate(component)


@router.put("/{component_id}", response_model=ComponentResponseModel)
def update_component_edpt(component_id: int, component: ComponentPatchModel, db: Session = Depends(get_db)):
    """Update component with `component_id`"""
    try:
        component = update_component(db=db,comp_id=component_id,comp=component)
        if component is None:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"Component with ID: {component_id} not found")
        component = ComponentResponseModel.model_validate(component)
    except IntegrityError as e:
        err_msg = str(e)

        # If it wasn't a unique or foreign key constraint, something else went wrong
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=err_msg)
    return component


@router.delete("/{component_id}", status_code=HTTPStatus.NO_CONTENT)
def delete_component_edpt(component_id: int, db: Session = Depends(get_db)):
    success = delete_component(db=db, comp_id=component_id)
    if not success:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"Component type with ID: {component_id} not found")
    return


@router.post("/{component_id}/data", response_model=ComponentVersionResponseModel)
def post_component_data_edpt(component_id: int, body: ComponentVersionInputModel, db: Session = Depends(get_db)):
    """Create data entry for component with `component_id`"""
    component = get_component_by_id(db, component_id)
    if component is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"Component type with ID: {component_id} not found")
    
    # Calc next version
    latest_version = max(component.component_versions, key=lambda cv: cv.version, default=None)
    if latest_version:
        next_version = latest_version.version + 1
    else:
        next_version = 0

    component_data = ComponentData(**body.component_data.model_dump())
    component_version = ComponentVersion(**body.model_dump(exclude="component_data"),component_data=component_data,version=next_version)
    component.component_versions.append(component_version)
    db.commit()
    return ComponentVersionResponseModel.model_validate(component_version, from_attributes=True)


@router.get("/{component_id}/data", response_model=ComponentDataResponseModel)
def get_component_data_edpt(component_id: int, version: int | None = None, db: Session = Depends(get_db)):
    component = get_component_by_id(db, component_id)

    if component is None:
        raise HTTPException(HTTPStatus.NOT_FOUND, detail="Component with id = {component_id} does not exist")
    
    if not component.component_versions:
        raise HTTPException(HTTPStatus.NOT_FOUND, detail="RF data for component with id = {component_id} does not exist")
    
    if version is not None:
        component_version = next((cv for cv in component.component_versions if cv.version == version), None)
    else:
        component_version = max(component.component_versions, key=lambda cv: cv.version, default=None)
    
    if component_version is None:
        raise HTTPException(HTTPStatus.NOT_FOUND, detail="Version = {version} does not exist for component with id = {component_id}")
    
    return ComponentDataResponseModel.model_validate(component_version.component_data)



@router.get("/{component_id}/versions", response_model=list[ComponentVersionResponseModel])
def get_component_versions_edpt(component_id: int, db: Session = Depends(get_db)):
    """Get versions of component with `component_id`"""
    component = db.query(Component).filter(Component.id == component_id).one_or_none()
    if component is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"Component with ID: {component_id} not found")
    component_versions = [ComponentVersionResponseModel.model_validate(component_version) for component_version in component.component_versions]
    return component_versions


@router.post("/{component_id}/versions", response_model=ComponentVersionResponseModel)
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
    db.commit()
    return component_version


@router.get("/types", response_model=list[ComponentTypeResponseModel])
def get_component_types_edpt(db: Session = Depends(get_db)):
    """Get component types"""
    component_types = get_component_types(db=db)
    component_types = [ComponentTypeResponseModel.model_validate(component_type) for component_type in component_types]
    return component_types


@router.post("/types", status_code=HTTPStatus.CREATED, response_model=ComponentTypeResponseModel)
def post_component_type_edpt(body: ComponentTypeInputModel, db: Session = Depends(get_db)):
    """Create a component type"""
    component_type = ComponentType(**body.model_dump())
    
    try:
        component_type = add_component_type(db=db,comp_type=component_type)
        component_type = ComponentTypeResponseModel.model_validate(component_type)
    except IntegrityError as e:
        err_msg = str(e)

        # If the type already exists, raise a 409 Conflict
        if "UniqueViolation" in err_msg:
            raise HTTPException(status_code=HTTPStatus.CONFLICT, detail=f"Component of type: {component_type.type} already exists")

        # If it wasn't a unique or foreign key constraint, something else went wrong
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=err_msg)
    return component_type


@router.delete("/types", status_code=HTTPStatus.NO_CONTENT)
def delete_component_types_edpt(db: Session = Depends(get_db)):
    delete_component_types(db=db)
    return


@router.delete("/types/{type_id}", status_code=HTTPStatus.NO_CONTENT)
def delete_component_type_edpt(type_id: int, db: Session = Depends(get_db)):
    success = delete_component_type(db=db, type_id=type_id)
    if not success:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"Component type with ID: {type_id} not found")
    return