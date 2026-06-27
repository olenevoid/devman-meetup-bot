from telegram import InlineKeyboardMarkup

from tg_bot.callbacks import Callback, CallbackButton


def menu_only() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[CallbackButton("Меню", Callback.MENU)]])
