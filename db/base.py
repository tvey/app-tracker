import logging
import os

import dotenv
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

dotenv.load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_async_engine(DATABASE_URL, echo=True)

Base = declarative_base()
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def create_tables():
    try:
        async with engine.begin() as conn:
            logger.info('Creating tables...')
            await conn.run_sync(Base.metadata.create_all)
            logger.info('Tables created.')
    except Exception as e:
        print(f'An error occurred creating tables: {e}')
