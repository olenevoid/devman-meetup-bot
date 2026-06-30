from telegram import Update
from telegram.ext import CallbackContext

from metup_bot.services import questions, talks
from tg_bot import keyboards, strings
from tg_bot.handlers.states import State
from tg_bot.messaging import edit_current, replace_current


async def enter(update: Update, context: CallbackContext) -> State:
    active_talk = await talks.get_active_talk()
    if active_talk is None:
        await edit_current(
            update,
            text=strings.no_active_speaker(),
            keyboard=keyboards.menu_only(),
        )
        return State.MAIN_MENU
    await edit_current(
        update,
        text=strings.ask_prompt(active_talk),
        keyboard=keyboards.get_ask_prompt_menu(),
    )
    return State.IN_ASK_SPEAKER


async def receive_question(update: Update, context: CallbackContext) -> State:
    active_talk = await talks.get_active_talk()
    if active_talk is None:
        await replace_current(
            update,
            context,
            text=strings.no_active_speaker(),
            keyboard=keyboards.menu_only(),
        )
        return State.MAIN_MENU
    tg_id = update.effective_user.id
    await questions.create_question(tg_id, active_talk, update.message.text)
    await replace_current(
        update,
        context,
        text=strings.question_sent(active_talk),
        keyboard=keyboards.get_question_sent_menu(),
    )
    return State.MAIN_MENU
