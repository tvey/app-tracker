import asyncio
import logging
import os

import dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)
from bot import admin_handlers, user_handlers
from db.base import create_tables

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)
logger = logging.getLogger(__name__)
logging.getLogger('httpx').setLevel(logging.WARNING)

dotenv.load_dotenv()

BOT_TOKEN = os.getenv('BOT_API_TOKEN')
INTERVAL_MINUTES = int(os.getenv('INTERVAL_MINUTES', '1'))


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    user = update.message.from_user
    await update.message.reply_text(f'Hello, {user.username}')


async def main() -> None:
    # scheduler = AsyncIOScheduler()
    # scheduler.add_job(check_apps, 'interval', minutes=INTERVAL_MINUTES)
    # scheduler.start()

    try:
        await create_tables()
        print("Starting bot after successful table creation.")
        application = Application.builder().token(BOT_TOKEN).build()
        application.add_handler(CommandHandler('start', start_command))

        for handler in (admin_handlers.handlers + user_handlers.handlers):
            application.add_handler(handler)

        async with application:
            await application.initialize()
            await application.start()
            await application.updater.start_polling()
            # await application.updater.stop()
            # await application.stop()
            # await application.shutdown()
    except Exception as e:
        print(f'Failed to start the bot: {e}')


if __name__ == '__main__':
    asyncio.run(main())
