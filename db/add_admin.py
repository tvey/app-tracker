import argparse
import asyncio

from sqlalchemy import select

from db.base import AsyncSessionLocal
from db.models import Admin
from logger_config import logger


async def add_admin(telegram_id: str):
    async with AsyncSessionLocal() as session:
        stmt = select(Admin).filter_by(telegram_id=telegram_id)
        result = await session.execute(stmt)
        existing_admin = result.scalars().first()

        if existing_admin:
            logger.warning(f'Админ с ID {telegram_id} уже в базе.')
            return

        new_admin = Admin(telegram_id=telegram_id)
        session.add(new_admin)
        await session.commit()
        logger.info(f'Добавлен админ с Телеграм ID {telegram_id}')


def main():
    parser = argparse.ArgumentParser(description='Добавить админа в БД')
    parser.add_argument(
        'telegram_id',
        type=int,
        help='Телеграм ID будущего админа',
    )
    args = parser.parse_args()
    asyncio.run(add_admin(args.telegram_id))


if __name__ == "__main__":
    main()
