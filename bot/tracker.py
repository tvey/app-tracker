import aiohttp
from telegram import Update
from telegram.ext import Application, CallbackContext

import db.operations as ops


async def track_availability(context: CallbackContext):
    """Repeatedly track apps from db for availability."""
    db_interval = await ops.get_interval_seconds()
    applications = await ops.get_app_list()

    async with aiohttp.ClientSession() as http_session:
        for app in applications:
            app_info = {'name': app.name, 'url': app.url}
            try:
                async with http_session.get(app.url) as response:
                    if response.status == 200:
                        if app.failure_count > 0:
                            await ops.update_failure_count(app.id)
                    else:
                        await ops.update_failure_count(app.id, reset=False)
                        if app.failure_count >= 3:
                            await notify_users(context.bot, app_info)
                            await ops.update_failure_count(app.id)
            except aiohttp.ClientError:
                await ops.update_failure_count(app.id, reset=False)
                if app.failure_count >= 3:
                    await notify_users(context.bot, app_info)
                    await ops.update_failure_count(app.id)

    current_interval = context.bot_data.get('tracking_interval', 60)
    if db_interval != current_interval:
        context.job.schedule_removal()
        context.job_queue.run_repeating(
            track_availability,
            interval=db_interval,
            first=0,  # run immediately
        )


async def notify_users(bot, app_info: dict):
    msg = f'Приложение {app_info["name"]} недоступно!\n\n{app_info["url"]}'
    users = await ops.get_user_list()

    if users:
        for user in users:
            await bot.send_message(chat_id=user, text=msg)
