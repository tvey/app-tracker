from collections.abc import Sequence

from sqlalchemy import select, delete
from sqlalchemy.exc import IntegrityError

from .base import AsyncSessionLocal
from .models import AccessKey, Admin, Application, Interval, User


async def get_admin_ids() -> Sequence[int]:
    """"Return a list of Telegram IDs of admin users."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Admin.telegram_id))
        return result.scalars().all()


async def is_admin(telegram_id: int) -> bool:
    async with AsyncSessionLocal() as session:
        stmt = select(Admin).where(Admin.telegram_id == telegram_id)
        result = await session.execute(stmt)
        admin = result.one_or_none()
        return bool(admin)


async def set_interval(seconds: int) -> None:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Interval).limit(1))
        existing_interval = result.scalars().one_or_none()

        if existing_interval:
            existing_interval.interval_seconds = seconds
        else:
            new_interval = Interval(interval_seconds=seconds)
            session.add(new_interval)
        await session.commit()


async def get_interval_seconds() -> int:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Interval))
        existing_interval = result.scalars().one_or_none()
        if existing_interval:
            return existing_interval.interval_seconds
        else:
            return 3600


async def generate_key() -> str:
    """Return a key generated by an admin for future use in /start by a user."""
    async with AsyncSessionLocal() as session:
        new_key = AccessKey()
        session.add(new_key)
        await session.commit()
        return new_key.key


async def is_key_valid(key: str) -> bool:
    async with AsyncSessionLocal() as session:
        stmt = select(AccessKey).where(AccessKey.key == key)
        db_key = await session.execute(stmt)
        return bool(db_key.one_or_none())


async def create_user(data: dict):
    """Create a new user, assign key and remove the used key from db."""
    async with AsyncSessionLocal() as session:
        key = data['access_key']
        telegram_id = data['telegram_id']
        user_stmt = select(User).where(User.telegram_id == telegram_id)
        user_query = await session.execute(user_stmt)
        is_user_exist = bool(user_query.one_or_none())

        if not is_user_exist:
            new_user = User(
                telegram_id=telegram_id,
                username=data.get('username'),
                access_key=key,
            )
            session.add(new_user)
            await session.execute(delete(AccessKey).where(AccessKey.key == key))
            await session.commit()


async def get_user_list() -> Sequence[Application]:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User))
        return result.scalars().all()


async def add_app(data: dict) -> bool:
    async with AsyncSessionLocal() as session:
        try:
            new_app = Application(
                url=data['app_url'],
                name=data['app_name'],
                launch_url=data['app_launch_url'],
            )
            session.add(new_app)
            await session.commit()
            return True
        except IntegrityError:
            await session.rollback()
            return False


async def remove_app(app_id: int) -> None:
    async with AsyncSessionLocal() as session:
        stmt = delete(Application).where(Application.id == app_id)
        await session.execute(stmt)
        await session.commit()


async def get_app(app_id: int) -> Application:
    async with AsyncSessionLocal() as session:
        stmt = select(Application).where(Application.id == app_id)
        result = await session.execute(stmt)
        return result.scalars().first()


async def get_app_list() -> Sequence[Application]:
    async with AsyncSessionLocal() as session:
        stmt = select(Application).order_by(Application.name)
        result = await session.execute(stmt)
        return result.scalars().all()


async def update_failure_count(app_id: int, reset: bool = True):
    async with AsyncSessionLocal() as session:
        stmt = select(Application).where(Application.id == app_id)
        result = await session.execute(stmt)
        app = result.scalars().first()

        if app:
            if reset:
                app.failure_count = 0
            else:
                app.failure_count += 1
            
            session.add(app)
            await session.commit()
