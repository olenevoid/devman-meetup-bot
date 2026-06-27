from telegram import Update
from telegram.ext import CallbackContext

from tg_bot.handlers import main_menu
from tg_bot.handlers.states import State


async def enter(update: Update, context: CallbackContext) -> State:
    await main_menu.show_stub(update, context, "Спросить спикера")
    return State.IN_ASK_SPEAKER


async def receive_question(update: Update, context: CallbackContext) -> State:
    await main_menu.show_stub(update, context, "Приём вопроса")
    return State.MAIN_MENU
