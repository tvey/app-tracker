import logging
import os

import dotenv
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


def main() -> None:
    logging.info('Database tables created successfully.')
    application = Application.builder().token(BOT_TOKEN).build()

    for handler in (admin_handlers.handlers + user_handlers.handlers):
        application.add_handler(handler)

    print((admin_handlers.handlers + user_handlers.handlers))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
