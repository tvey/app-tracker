import os

import dotenv
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
)

dotenv.load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
SQLALCHEMY_ECHO = bool(os.getenv('SQLALCHEMY_ECHO'))
engine = create_async_engine(DATABASE_URL, echo=SQLALCHEMY_ECHO)

Base = declarative_base()
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
