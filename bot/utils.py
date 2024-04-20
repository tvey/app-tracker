import aiohttp

from .links import APP_LINKS_RU


async def is_app_available(app_url: str) -> bool:
    async with aiohttp.ClientSession() as session:
        async with session.get(app_url) as r:
            return r.status == 200


async def check_apps():
    apps = APP_LINKS_RU
    for url in apps:  # can create tasks, probably
        app_id = url.rsplit('id', maxsplit=1)[-1]
        if await is_app_available(url):
            print(f'{app_id} is fine')
        else:
            print(f'{app_id} is not available')