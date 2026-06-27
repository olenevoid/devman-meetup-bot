from telegram import Update
from telegram.ext import CallbackContext

from tg_bot.handlers import main_menu
from tg_bot.handlers.states import State


async def enter(update: Update, context: CallbackContext) -> State:
    await main_menu.show_stub(update, context, "Нетворкинг")
    return State.IN_NETWORKING


async def show_bio_form(update: Update, context: CallbackContext) -> State:
    await main_menu.show_stub(update, context, "Анкета · шаг 1/3")
    return State.NET_FORM_BIO


async def receive_bio(update: Update, context: CallbackContext) -> State:
    await main_menu.show_stub(update, context, "Анкета · шаг 2/3")
    return State.NET_FORM_STACK


async def receive_stack(update: Update, context: CallbackContext) -> State:
    await main_menu.show_stub(update, context, "Анкета · шаг 3/3")
    return State.NET_FORM_CONTACT


async def receive_contact(update: Update, context: CallbackContext) -> State:
    await main_menu.show_stub(update, context, "Нетворкинг · матч")
    return State.NET_MATCHING


async def next_match(update: Update, context: CallbackContext) -> State:
    await main_menu.show_stub(update, context, "Нетворкинг · следующий")
    return State.NET_MATCHING


async def reveal_contact(update: Update, context: CallbackContext) -> State:
    await main_menu.show_stub(update, context, "Нетворкинг · контакт")
    return State.NET_MATCHING
