import asyncio

from db.base import create_tables

if __name__ == 'main':
    asyncio.run(create_tables())
