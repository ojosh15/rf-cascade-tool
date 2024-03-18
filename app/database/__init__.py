from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import config
from database.models import SQLAlchemyBase
# from database.models.radio import Radio
# from database.models.users import User

# Log in to the database and create tables
engine = create_engine(str(config.POSTGRES_URL))
Session = sessionmaker(bind=engine, expire_on_commit=False)

if config.CLEAR_DB:
    SQLAlchemyBase.metadata.drop_all(engine)

SQLAlchemyBase.metadata.create_all(engine)