from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    Update,
)
from telegram.ext import CallbackQueryHandler, CommandHandler, ContextTypes

import db.operations as ops

app_list_text = 'Список приложений'
launch_links_text = 'Сформировать ссылку запуска'
add_app_text = 'Добавить приложение'
remove_app_text = 'Удалить приложение'


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_chat_id = update.effective_user.id
    is_admin = await ops.is_admin(user_chat_id)

    if is_admin:
        keyboard = [[add_app_text, remove_app_text]]  # more
        reply_markup = ReplyKeyboardMarkup(
            keyboard, resize_keyboard=True, one_time_keyboard=False
        )
    key = context.args[0] if context.args else None

    if not key:
        msg = 'Добавьте ключ доступа: /start <ключ>'
        await update.message.reply_text(msg)

    is_valid = await ops.is_key_valid(key)

    if is_valid:
        data = {
            'telegram_id': user_chat_id,
            'username': update.effective_user.username,
            'access_key': key,
        }
        await ops.create_user(data)
        keyboard = [[app_list_text, launch_links_text], ['FAQ']]
        reply_markup = ReplyKeyboardMarkup(
            keyboard, resize_keyboard=True, one_time_keyboard=False
        )
        await update.message.reply_text(
            'Доступ к боту успешно открыт!',
            reply_markup=reply_markup,
        )
    else:
        await update.message.reply_text('Неверный ключ доступа.')


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show app list."""
    apps = await ops.get_app_list()
    if apps:
        for app in apps:
            text = 'Список приложений:\n\n'
            text += f'{app.name}\nCсылка: {app.url}\n\n'
    else:
        text = 'Список приложений пуст.'

    await update.message.reply_text(
        text, disable_web_page_preview=True
    )  # for now


async def get_launch_urls(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List apps and return assigned launch_url on button press."""
    if update.message:
        apps = await ops.get_app_list()
        keyboard = [
            [
                InlineKeyboardButton(app.name, callback_data=str(app.id))
                for app in apps
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        msg = 'Выберите приложение для генерации ссылки:'
        await update.message.reply_text(msg, reply_markup=reply_markup)


async def handle_launch_call(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()
    app_id = int(query.data)
    app = await ops.get_app(app_id)
    if app and app.url:
        msg = f'Ссылка для запуска {app.name}: {app.launch_url}'
        await query.message.reply_text(msg)
    else:
        await query.message.reply_text(f'Нет ссылки для запуска {app.name}')


async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == app_list_text:
        return await status(update, context)
    elif text == launch_links_text:
        return await get_launch_urls(update, context)


handlers = [
    CommandHandler('start', start),
    CommandHandler('status', status),
    CallbackQueryHandler(handle_launch_call),
]
