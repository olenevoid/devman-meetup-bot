from telegram.ext import CommandHandler, ConversationHandler

from tg_bot.handlers import main_menu
from tg_bot.handlers.states import State


def get_root_conversation_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("start", main_menu.start)],
        states={
            State.MAIN_MENU: [],
        },
        fallbacks=[CommandHandler("start", main_menu.start)],
        per_message=False,
        per_chat=True,
        per_user=True,
    )
