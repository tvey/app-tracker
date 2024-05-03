from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from .utils import TEXTS as txt


user_keyboard = [
    [txt.app_list, txt.launch_links],
    [txt.faq],
]

admin_keyboard = [
    [txt.add_app, txt.remove_app],
    [txt.set_interval, txt.generate_key],
    [txt.app_list, txt.launch_links],
]


def app_list_keyboard(apps, prefix):
    keyboard = [
        [InlineKeyboardButton(app.name, callback_data=f'{prefix}_{app.id}')]
        for app in apps
    ]
    return InlineKeyboardMarkup(keyboard)
