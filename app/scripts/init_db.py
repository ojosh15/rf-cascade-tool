import json
from app.database import LocalSession
from sqlalchemy.orm import Session


def prepopulate_component_types(db: Session):
    # Load comp types
    file_path = '/static/component_types.json'
    with open(file_path) as data:
        comp_types = json.load(data)

    # Get current comp types in db

    # Update/insert comp types into db


if __name__ == "__main__":
    with LocalSession() as session, session.begin():
        prepopulate_component_types(session)