from functools import wraps

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
)

import db.operations as ops


def admin_only(func):
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        user_id = update.effective_user.id
        if not ops.is_admin(user_id):
            return  # what here
        return func(update, context, *args, **kwargs)

    return wrapped


# /add [URL приложения] [Название] [Ссылка запуска]
@admin_only
async def add_app(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Add app')


@admin_only
async def remove_app(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Remove app')


@admin_only
async def set_interval(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass


def interval_callback(update: Update, context: CallbackContext):
    # Extract the number from the message
    number = update.message.text
    # Here you would typically save this number or process it
    update.message.reply_text(f"Number saved: {number}")


@admin_only
async def generate_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    key = await ops.generate_key()
    await update.message.reply_text(
        f'Новый ключ доступа: `{key}`',
        parse_mode='MarkdownV2',
    )


@admin_only
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass


handlers = [
    CommandHandler('add', add_app),
    CommandHandler('remove', remove_app),
    CommandHandler('set_interval', set_interval),
    MessageHandler(filters.TEXT & ~filters.COMMAND, number)

]
