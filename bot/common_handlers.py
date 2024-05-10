from telegram import (
    ReplyKeyboardMarkup,
    Update,
)
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    filters,
    ContextTypes,
    MessageHandler,
)

import db.operations as ops
from config import logger
from .admin_handlers import add_app, remove_app, set_interval, generate_key
from .keyboards import app_list_keyboard, admin_keyboard, user_keyboard
from .utils import protected, TEXTS as txt


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    is_admin = await ops.is_admin(user_id)

    if is_admin:
        logger.info(f'Admin user {user_id} called start command')
        markup = ReplyKeyboardMarkup(
            admin_keyboard,
            resize_keyboard=True,
            one_time_keyboard=False,
        )
        await update.message.reply_text('Привет, админ!', reply_markup=markup)
    else:
        key = context.args[0] if context.args else None

        if not key:
            logger.info(f'User {user_id} called start without key')
            msg = 'Добавьте ключ доступа: /start <ключ>'
            await update.message.reply_text(msg)
        else:
            is_valid = await ops.is_key_valid(key)

            if is_valid:
                data = {
                    'telegram_id': user_id,
                    'username': update.effective_user.username,
                    'access_key': key,
                }
                await ops.create_user(data)

                markup = ReplyKeyboardMarkup(
                    user_keyboard,
                    resize_keyboard=True,
                    one_time_keyboard=False,
                )
                await update.message.reply_text(
                    'Доступ к боту успешно открыт!',
                    reply_markup=markup,
                )
                logger.info(f'User {user_id} successfully got access to bot')
            else:
                logger.info(f'User {user_id} called start with bad key {key}')
                await update.message.reply_text('Неверный ключ доступа')


@protected
async def list_apps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show app list."""
    apps = await ops.get_app_list()

    if apps:
        msg = 'Список приложений:\n\n'
        for app in apps:
            msg += f'{app.name}\nCсылка: {app.url}\n\n'
    else:
        msg = txt.app_list_empty
    await update.message.reply_text(msg, disable_web_page_preview=True)  # dis


@protected
async def get_launch_urls(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List apps and return assigned launch_url on button press."""
    apps = await ops.get_app_list()

    if apps:
        await update.message.reply_text(
            'Выберите приложение для генерации ссылки:\n',
            reply_markup=app_list_keyboard(apps, 'launch'),
        )
    else:
        await update.message.reply_text(txt.app_list_empty)


@protected
async def handle_launch_call(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()
    app_id = int(query.data.split('_')[-1])
    app = await ops.get_app(app_id)
    if app and app.launch_url:
        msg = f'Ссылка для запуска {app.name}: {app.launch_url}'
        await query.message.reply_text(msg)
    else:
        await query.message.reply_text(f'Нет ссылки для запуска {app.name}')


@protected
async def faq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Вопросы и ответы')


@protected
async def handle_button_text(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    text = update.message.text
    if text == txt.app_list:
        return await list_apps(update, context)
    elif text == txt.launch_links:
        return await get_launch_urls(update, context)
    elif text == txt.faq:
        return await faq(update, context)
    elif text == txt.add_app:
        return await add_app(update, context)
    elif text == txt.remove_app:
        return await remove_app(update, context)
    elif text == txt.set_interval:
        return await set_interval(update, context)
    elif text == txt.generate_key:
        return await generate_key(update, context)


handlers = [
    CommandHandler('start', start),
    CommandHandler('list', list_apps),
    CommandHandler('launch', get_launch_urls),
    MessageHandler(
        filters.Text(
            [
                txt.app_list,
                txt.launch_links,
                txt.faq,
                txt.add_app,
                txt.remove_app,
                txt.set_interval,
                txt.generate_key,
            ]
        ),
        handle_button_text,
    ),
    CallbackQueryHandler(handle_launch_call, pattern=r'^launch_'),
]
