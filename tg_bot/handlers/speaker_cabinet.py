from telegram import Update
from telegram.ext import CallbackContext

from tg_bot.handlers import main_menu
from tg_bot.handlers.states import State


async def enter(update: Update, context: CallbackContext) -> State:
    await main_menu.show_stub(update, context, "Кабинет спикера")
    return State.MAIN_MENU


async def start_talk(update: Update, context: CallbackContext) -> State:
    await main_menu.show_stub(update, context, "Начать доклад")
    return State.MAIN_MENU


async def end_talk(update: Update, context: CallbackContext) -> State:
    await main_menu.show_stub(update, context, "Завершить доклад")
    return State.MAIN_MENU


async def list_questions(update: Update, context: CallbackContext) -> State:
    await main_menu.show_stub(update, context, "Вопросы к докладу")
    return State.MAIN_MENU


async def show_question(update: Update, context: CallbackContext) -> State:
    await main_menu.show_stub(update, context, "Вопрос")
    return State.MAIN_MENU


async def mark_answered(update: Update, context: CallbackContext) -> State:
    await main_menu.show_stub(update, context, "Отметить отвеченным")
    return State.MAIN_MENU
