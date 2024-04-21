import uuid

from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    String,
    Boolean,
    ForeignKey,
)

from .base import Base


class Application(Base):
    __tablename__ = 'apps'

    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=True)  # is nullable?
    launch_url = Column(String, nullable=True)  # is nullable?


class Admin(Base):
    __tablename__ = 'admins'

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String)
    access_key = Column(String, unique=True)


class AccessKey(Base):
    __tablename__ = 'access_keys'

    id = Column(Integer, primary_key=True)
    key = Column(
        String,
        default=lambda: str(uuid.uuid4()).replace('-', ''),
        unique=True,
    )
