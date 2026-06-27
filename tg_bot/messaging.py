from telegram import Update
from telegram.error import TelegramError
from telegram.ext import CallbackContext

LAST_MESSAGE_KEY = "last_message_id"


async def edit_current(
    update: Update,
    text: str,
    keyboard=None,
    parse_mode: str = "HTML",
) -> None:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        text,
        reply_markup=keyboard,
        parse_mode=parse_mode,
    )


async def replace_current(
    update: Update,
    context: CallbackContext,
    text: str,
    keyboard=None,
    parse_mode: str = "HTML",
) -> int:
    chat_id = update.effective_chat.id
    last_message_id = context.user_data.get(LAST_MESSAGE_KEY)
    if last_message_id is not None:
        try:
            await context.bot.delete_message(chat_id, last_message_id)
        except TelegramError:
            pass
    message = await context.bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=keyboard,
        parse_mode=parse_mode,
    )
    context.user_data[LAST_MESSAGE_KEY] = message.message_id
    return message.message_id
