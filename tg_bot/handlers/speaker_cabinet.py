from telegram import Update
from telegram.ext import CallbackContext

from metup_bot.services import questions, talks
from tg_bot import keyboards, strings
from tg_bot.callbacks import parse_callback_data_string
from tg_bot.handlers.states import State
from tg_bot.messaging import edit_current

CABINET_PAGE_SIZE = 5


async def _get_talk(update: Update):
    tg_id = update.effective_user.id
    return await talks.get_speaker_talk(tg_id)


async def _render_cabinet(update: Update, talk) -> None:
    active_talk = await talks.get_active_talk()
    total = 0
    unanswered = 0
    if talk.state in ("active", "finished"):
        total, unanswered = await questions.questions_stats_for_talk(talk)
    await edit_current(
        update,
        text=strings.speaker_cabinet_text(
            talk, active_talk, total, unanswered
        ),
        keyboard=keyboards.get_speaker_cabinet_menu(
            talk, active_talk, total, unanswered
        ),
    )


async def _render_questions(update: Update, talk, page: int) -> None:
    talk_questions, num_pages = await questions.get_questions_paginated(
        talk, page, page_size=CABINET_PAGE_SIZE
    )
    await edit_current(
        update,
        text=strings.questions_list_text(talk, page, num_pages),
        keyboard=keyboards.get_questions_list_menu(
            talk_questions, page, num_pages
        ),
    )


async def _render_detail(update: Update, question) -> None:
    await edit_current(
        update,
        text=strings.question_detail_text(question),
        keyboard=keyboards.get_question_detail_menu(question),
    )


async def _back_to_cabinet(update: Update) -> None:
    talk = await _get_talk(update)
    if talk is not None:
        await _render_cabinet(update, talk)


async def enter(update: Update, context: CallbackContext) -> State:
    talk = await _get_talk(update)
    if talk is None:
        await edit_current(
            update,
            text=strings.speaker_cabinet_text(None, None, 0, 0),
            keyboard=keyboards.menu_only(),
        )
        return State.MAIN_MENU
    await _render_cabinet(update, talk)
    return State.MAIN_MENU


async def start_talk(update: Update, context: CallbackContext) -> State:
    talk = await _get_talk(update)
    if talk is not None:
        try:
            await talks.start_talk(talk)
        except ValueError:
            pass
        await _render_cabinet(update, talk)
    return State.MAIN_MENU


async def end_talk(update: Update, context: CallbackContext) -> State:
    talk = await _get_talk(update)
    if talk is not None:
        try:
            await talks.end_talk(talk)
        except ValueError:
            pass
        await _render_cabinet(update, talk)
    return State.MAIN_MENU


async def list_questions(update: Update, context: CallbackContext) -> State:
    talk = await _get_talk(update)
    if talk is None:
        return State.MAIN_MENU
    data = parse_callback_data_string(update.callback_query.data)
    page = int(data.params.get("page", 1))
    await _render_questions(update, talk, page)
    return State.MAIN_MENU


async def show_question(update: Update, context: CallbackContext) -> State:
    data = parse_callback_data_string(update.callback_query.data)
    question = await questions.get_question(int(data.params["id"]))
    if question is None:
        await _back_to_cabinet(update)
        return State.MAIN_MENU
    await _render_detail(update, question)
    return State.MAIN_MENU


async def mark_answered(update: Update, context: CallbackContext) -> State:
    data = parse_callback_data_string(update.callback_query.data)
    question = await questions.mark_answered(int(data.params["id"]))
    if question is None:
        await _back_to_cabinet(update)
        return State.MAIN_MENU
    await _render_detail(update, question)
    return State.MAIN_MENU
