from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import config
from app.database.models import SQLAlchemyBase
from app.database.models.projects import *
from app.database.models.paths import *
from app.database.models.components import *
from app.database.models.sources import *
from app.database.models.stackups import *
from app.database.models.users import *


# Log in to the database and create tables
engine = create_engine(str(config.POSTGRES_URL))
LocalSession = sessionmaker(bind=engine, expire_on_commit=False)


def get_db():
    db = LocalSession()
    try:
        yield db
    except Exception as se:
        db.rollback()
        raise se
    finally:
        db.close()