import json
from app.database import LocalSession
from sqlalchemy.orm import Session
from app.crud.crud_component_types import *


def prepopulate_component_types(db: Session):
    # Load comp types
    file_path = '/static/component_types.json'
    with open(file_path) as data:
        comp_types = json.load(data)
    comp_types = [ComponentTypeInputModel.model_validate(comp_type) for comp_type in comp_types]

    # Get current comp types in db
    current_comps = get_component_types(db=db)
    current_comps_dict = {current_comp.type: current_comp for current_comp in current_comps}

    # Update/insert comp types into db
    for comp_type in comp_types:
        if comp_type.type in current_comps_dict:
            current_comp = current_comps_dict[comp_type.type]
            update_component_type(db=db, comp_type_id=current_comp.id, comp_type=comp_type)
        else:
            add_component_type(db, ComponentType(**comp_type.model_dump()))
    
    db.close()


if __name__ == "__main__":
    prepopulate_component_types(LocalSession())