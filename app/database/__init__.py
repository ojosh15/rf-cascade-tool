from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import config
from database.models import SQLAlchemyBase
from database.models.projects import *
from database.models.paths import *
from database.models.components import *
from database.models.sources import *
from database.models.stackups import *


# Log in to the database and create tables
engine = create_engine(str(config.POSTGRES_URL))
LocalSession = sessionmaker(bind=engine, expire_on_commit=False)

if config.CLEAR_DB:
    SQLAlchemyBase.metadata.drop_all(engine)

SQLAlchemyBase.metadata.create_all(engine)

with LocalSession() as session, session.begin():
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

def create_tables():
    SQLAlchemyBase.metadata.create_all(engine)

def drop_tables():
    SQLAlchemyBase.metadata.drop_all(engine)

def get_db():
    db = LocalSession()
    try:
        yield db
    except Exception as se:
        db.rollback()
        raise se
    finally:
        db.close()