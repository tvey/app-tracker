import logging
import os

import dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes as CT,
)

from bot.utils import check_apps

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)
logger = logging.getLogger(__name__)
logging.getLogger('httpx').setLevel(logging.WARNING)

dotenv.load_dotenv()

BOT_TOKEN = os.getenv('BOT_API_TOKEN')
INTERVAL_MINUTES = int(os.getenv('INTERVAL_MINUTES', '1'))


async def try_command(update: Update, context: CT.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text('Nice try')


def main() -> None:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(check_apps, 'interval', minutes=INTERVAL_MINUTES)
    scheduler.start()

    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler('try', try_command))
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
