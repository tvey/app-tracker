
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    filters,
    ContextTypes,
    MessageHandler,
)

import db.operations as ops
from .keyboards import app_list_keyboard
from .utils import admin_only, is_valid_url, parse_interval_input, TEXTS as txt


@admin_only
async def add_app(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args or len(context.args) < 3:
        await update.message.reply_text(txt.add_memo)
        return

    app_url = context.args[0]
    app_name = ' '.join(context.args[1:-1])
    app_launch_url = context.args[-1]

    if (not is_valid_url(app_url)) or (not is_valid_url(app_launch_url)):
        await update.message.reply_text(txt.add_url_validation)
        return
    else:
        new_app_data = {
            'app_url': app_url,
            'app_name': app_name,
            'app_launch_url': app_launch_url,
        }
        result = await ops.add_app(new_app_data)
        if result:
            msg = f'Приложение \"{new_app_data["app_name"]}\" добавлено'
        else:
            msg = f'Приложение с таким URL уже существует'
        await update.message.reply_text(msg)


@admin_only
async def remove_app(update: Update, context: ContextTypes.DEFAULT_TYPE):
    apps = await ops.get_app_list()
    if apps:
        await update.message.reply_text(
            'Выберите приложение для удаления:',
            reply_markup=app_list_keyboard(apps, 'remove'),
        )
    else:
        await update.message.reply_text(txt.app_list_empty)


@admin_only
async def handle_remove_call(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()
    app_id = int(query.data.split('_')[-1])
    await ops.remove_app(app_id)
    await query.message.reply_text('Приложение удалено')


@admin_only
async def set_interval(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(txt.interval_example)


@admin_only
async def handle_interval(update: Update, context: CallbackContext):
    value = update.message.text
    seconds = parse_interval_input(value)
    if seconds > 0:
        await ops.set_interval(seconds)
        await update.message.reply_text(f'Интервал ({value}) сохранён')
    else:
        await update.message.reply_text(f'Непонятный интервал: {value}')


@admin_only
async def generate_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    key = await ops.generate_key()
    await update.message.reply_text(
        f'Новый ключ доступа:\n`{key}`',
        parse_mode='MarkdownV2',
    )


@admin_only
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = ' '.join(context.args)

    if not msg:
        await update.message.reply_text(txt.bloadcast_memo)
        return

    users = await ops.get_user_list()

    if users:
        for user in users:
            try:
                await context.bot.send_message(
                    chat_id=user.telegram_id,
                    text=msg,
                    parse_mode='HTML',
                )
            except Exception:
                pass


handlers = [
    CommandHandler('add', add_app),
    CommandHandler('remove', remove_app),
    CallbackQueryHandler(handle_remove_call, pattern=r'^remove_'),
    CommandHandler('interval', set_interval),
    CommandHandler('genkey', generate_key),
    CommandHandler('broadcast', broadcast),
    MessageHandler(
        filters.Regex(r'\d+\s+(час(а|ов)?|минут(а|ы)?|секунд(а|ы)?)'),
        handle_interval,
    ),
]
