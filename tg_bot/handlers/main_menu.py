from telegram import Update
from telegram.ext import CallbackContext

from tg_bot import keyboards, strings
from tg_bot.handlers.states import State
from tg_bot.messaging import edit_current, replace_current


async def start(update: Update, context: CallbackContext) -> State:
    await replace_current(
        update,
        context,
        text=strings.MAIN_MENU_TEXT,
        keyboard=keyboards.get_main_menu({"guest"}),
    )
    return State.MAIN_MENU


async def show_main_menu(update: Update, context: CallbackContext) -> State:
    await edit_current(
        update,
        text=strings.MAIN_MENU_TEXT,
        keyboard=keyboards.get_main_menu({"guest"}),
    )
    return State.MAIN_MENU


async def show_stub(
    update: Update, context: CallbackContext, name: str
) -> None:
    text = strings.stub_text(name)
    if update.callback_query is not None:
        await edit_current(update, text, keyboards.menu_only())
    else:
        await replace_current(update, context, text, keyboards.menu_only())
