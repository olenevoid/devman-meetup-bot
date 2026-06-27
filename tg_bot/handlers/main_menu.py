from telegram import Update
from telegram.ext import CallbackContext

from tg_bot.handlers.states import State
from tg_bot.messaging import replace_current


async def start(update: Update, context: CallbackContext) -> State:
    await replace_current(
        update,
        context,
        text="PythonMeetup bot: структура заложена.",
        keyboard=None,
    )
    return State.MAIN_MENU
