from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
)


def main_keyboard(user_type):
    if user_type == 'admin':
        pass
    else:
        pass


def app_list_keyboard(apps, prefix):
    keyboard = [
        [InlineKeyboardButton(app.name, callback_data=f'{prefix}_{app.id}')]
        for app in apps
    ]
    return InlineKeyboardMarkup(keyboard)
