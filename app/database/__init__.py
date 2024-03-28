from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import config
from database.models import SQLAlchemyBase
from database.models.projects import Project
from database.models.paths import Path, Stackup
from database.models.components import Component, ComponentData, ComponentVersion, ComponentType, DataSheet
from database.models.sources import SourceEnum


# Log in to the database and create tables
engine = create_engine(str(config.POSTGRES_URL))
Session = sessionmaker(bind=engine, expire_on_commit=False)

if config.CLEAR_DB:
    SQLAlchemyBase.metadata.drop_all(engine)

SQLAlchemyBase.metadata.create_all(engine)

with Session() as session, session.begin():
    types = [
        'Attenuator',
        'Amplifier',
        'Coupler'
    ]
    for type in types:
        type_instance = ComponentType(type=type)
        session.add(type_instance)

    component_data = ComponentData(
      data_source = SourceEnum.SIMULATED,
      gain = {},
      nf = {},
      p1db = {},
      ip2 = {},
      ip3 = {},
      max_input = {}
    )
    session.add(component_data)