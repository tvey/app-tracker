import logging

from telegram import Update
from telegram.ext import Application

from bot import admin_handlers, common_handlers
from bot.tracker import track_availability
from config import BOT_TOKEN

logging.getLogger('httpx').setLevel(logging.WARNING)


def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()
    start_handler = common_handlers.handlers[0]
    application.add_handler(start_handler)

    for handler in admin_handlers.handlers + common_handlers.handlers[1:]:
        application.add_handler(handler)

    job_queue = application.job_queue
    job_queue.run_repeating(track_availability, interval=60, first=0)

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
