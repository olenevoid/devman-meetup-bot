from telegram import Update
from telegram.ext import CallbackContext

from metup_bot.services import users
from tg_bot import keyboards, strings
from tg_bot.handlers.states import State
from tg_bot.messaging import edit_current, replace_current


async def start(update: Update, context: CallbackContext) -> State:
    tg_id = update.effective_user.id
    roles = users.get_roles_for_telegram_id(tg_id)
    await replace_current(
        update,
        context,
        text=strings.main_menu_text(roles),
        keyboard=keyboards.get_main_menu(roles),
    )
    return State.MAIN_MENU


async def show_main_menu(update: Update, context: CallbackContext) -> State:
    tg_id = update.effective_user.id
    roles = users.get_roles_for_telegram_id(tg_id)
    await edit_current(
        update,
        text=strings.main_menu_text(roles),
        keyboard=keyboards.get_main_menu(roles),
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
