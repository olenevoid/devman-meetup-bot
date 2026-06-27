from telegram import Update
from telegram.ext import CallbackContext

from tg_bot.handlers import main_menu
from tg_bot.handlers.states import State


async def enter(update: Update, context: CallbackContext) -> State:
    await main_menu.show_stub(update, context, "Программа")
    return State.MAIN_MENU


async def show_full(update: Update, context: CallbackContext) -> State:
    await main_menu.show_stub(update, context, "Полная программа")
    return State.MAIN_MENU


async def page(update: Update, context: CallbackContext) -> State:
    await main_menu.show_stub(update, context, "Программа · страница")
    return State.MAIN_MENU
