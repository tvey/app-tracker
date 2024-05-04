import re
from functools import wraps
from types import SimpleNamespace

import validators

import db.operations as ops

TEXTS = SimpleNamespace(
    app_list='Список приложений',
    launch_links='Сформировать ссылку запуска',
    faq='FAQ',
    add_app='Добавить приложение',
    add_memo=(
        'Нужно добавить к команде 3 аргумента через пробел:\n'
        '/add [URL приложения] [Название] [Ссылка запуска]'
    ),
    add_url_validation='Со ссылками что-то не так',
    remove_app='Удалить приложение',
    broadcast='Отправить всем сообщение',
    generate_key='Сгенерировать ключ доступа',
    set_interval='Задать интервал',
    interval_example='Присылай интервал в формате: "10 минут", "3 часа" и т.п.',
    app_list_empty='Список приложений пуст',
    bloadcast_memo='Сообщение нужно добавить после команды: /broadcast <текст>',
)


def admin_only(func):
    @wraps(func)
    async def wrapped(update, context, *args, **kwargs):
        user_id = update.effective_user.id
        is_admin = await ops.is_admin(user_id)
        if not is_admin:
            return
        return await func(update, context, *args, **kwargs)

    return wrapped


def protected(func):
    """Decorate handlers to allow access only to existing users and admins."""
    @wraps(func)
    async def wrapped(update, context, *args, **kwargs):
        user_id = update.effective_user.id
        is_admin = await ops.is_admin(user_id)
        is_user = await ops.is_existing_user(user_id)
        if not is_admin and not is_user:
            return
        return await func(update, context, *args, **kwargs)

    return wrapped
 


def parse_interval_input(value: str) -> int:
    units = {
        'секунд': 1,
        'минут': 60,
        'час': 3600,
    }
    match = re.match(r'(\d+)\s+(\w+)', value)

    if not match:
        return -1

    number, unit = int(match.group(1)), match.group(2)

    def find_unit(unit):
        for u in units.keys():
            if unit.startswith(u):
                return u
        return None

    found_unit = find_unit(unit)
    if not found_unit:
        return -1

    return number * units[found_unit]


def is_valid_url(value: str) -> bool:
    if validators.url(value):
        return True
    return False
