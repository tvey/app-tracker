from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, CommandHandler, ContextTypes

import db.operations as ops


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_chat_id = update.effective_user.id
    key = context.args[0] if context.args else None

    if key and await ops.is_key_valid(key):
        data = {
            'telegram_id': user_chat_id,
            'username': update.effective_user.username,
            'access_key': key
        }
        await ops.create_user(data)
        await update.message.reply_text('Доступ к боту успешно открыт!')
    else:
        msg = 'Запросите ключ доступа у администратора.'
        await update.message.reply_text(msg)


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show app list."""
    apps = await ops.get_app_list()
    text = 'Список приложений:\n\n'

    for app in apps:
        text += f'{app.name}\nCсылка: {app.url}'

    await update.message.reply_text(text, disable_web_page_preview=True) # for now


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


async def handle_launch_call(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    app_id = int(query.data)
    app = await ops.get_app(app_id)
    if app and app.url:
        msg = f'Ссылка для запуска {app.name}: {app.launch_url}'
        await query.message.reply_text(msg)
    else:
        await query.message.reply_text(f'Нет ссылки для запуска {app.name}')


handlers = [
    CommandHandler('start', start),
    CallbackQueryHandler(handle_launch_call),
]
