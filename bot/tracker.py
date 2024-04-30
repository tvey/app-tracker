import aiohttp
from telegram import Update
from telegram.ext import Application, CallbackContext

import db.operations as ops
from config import logger


async def track_availability(context: CallbackContext):
    """Repeatedly track apps from db for availability."""
    db_interval = await ops.get_interval_seconds()
    applications = await ops.get_app_list()

    async with aiohttp.ClientSession() as http_session:
        if applications:
            for app in applications:
                app_info = {'name': app.name, 'url': app.url}
                failure_msg = f'App fails: {app.name}, notifying users'

                try:
                    async with http_session.get(app.url) as response:
                        if response.status == 200:
                            if app.failure_count > 0:
                                await ops.update_failure_count(app.id)
                        else:
                            await ops.update_failure_count(app.id, reset=False)
                            if app.failure_count >= 3:
                                await notify_users(context.bot, app_info)
                                logger.info(failure_msg)
                                await ops.update_failure_count(app.id)
                except aiohttp.ClientError:
                    await ops.update_failure_count(app.id, reset=False)
                    if app.failure_count >= 3:
                        logger.info(failure_msg)
                        await notify_users(context.bot, app_info)
                        await ops.update_failure_count(app.id)

    current_interval = context.bot_data.get('tracking_interval', 60)
    if db_interval != current_interval:
        context.job.schedule_removal()
        context.job_queue.run_repeating(
            track_availability,
            interval=db_interval,
            first=db_interval,
        )


async def notify_users(bot, app_info: dict):
    msg = f'Приложение {app_info["name"]} недоступно!\n\n{app_info["url"]}' 
    admin_ids = await ops.get_admin_ids()
    users = await ops.get_user_list()
    recipients = list(admin_ids)

    if users:
        recipients += [user.telegram_id for user in users]

    for rec_id in recipients:
        await bot.send_message(chat_id=rec_id, text=msg)
