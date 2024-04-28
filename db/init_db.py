import asyncio

from config import logger
from db.base import Base, engine
from db.models import Application, Admin, AccessKey, Interval, User  # import them!


async def create_tables():
    try:
        async with engine.begin() as conn:
            logger.info('(Re)creating tables...')
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
            logger.info('Tables created')
    except Exception as e:
        print(f'An error occurred creating tables: {e}')

asyncio.run(create_tables())
