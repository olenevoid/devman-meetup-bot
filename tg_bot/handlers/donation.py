from telegram import Update
from telegram.ext import CallbackContext

from tg_bot.handlers import main_menu
from tg_bot.handlers.states import State


async def enter(update: Update, context: CallbackContext) -> State:
    await main_menu.show_stub(update, context, "Донат")
    return State.IN_DONATION


async def preset_amount(update: Update, context: CallbackContext) -> State:
    await main_menu.show_stub(update, context, "Донат · сумма")
    return State.MAIN_MENU


async def input_custom_amount(
    update: Update, context: CallbackContext
) -> State:
    await main_menu.show_stub(update, context, "Донат · своя сумма")
    return State.DON_AWAIT_AMOUNT


async def receive_custom_amount(
    update: Update, context: CallbackContext
) -> State:
    await main_menu.show_stub(update, context, "Донат · создание счёта")
    return State.MAIN_MENU


async def on_successful_payment(
    update: Update, context: CallbackContext
) -> State:
    await main_menu.show_stub(update, context, "Донат · спасибо")
    return State.MAIN_MENU
