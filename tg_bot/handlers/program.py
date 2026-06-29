from telegram import Update
from telegram.ext import CallbackContext

from metup_bot.services import talks
from tg_bot import keyboards, strings
from tg_bot.callbacks import parse_callback_data_string
from tg_bot.handlers.states import State
from tg_bot.messaging import edit_current

FULL_PROGRAM_PAGE_SIZE = 5


async def enter(update: Update, context: CallbackContext) -> State:
    active_talk = await talks.get_active_talk()
    next_talk = await talks.get_next_talk()
    await edit_current(
        update,
        text=strings.program_text(active_talk, next_talk),
        keyboard=keyboards.get_program_menu(
            has_active_talk=active_talk is not None,
        ),
    )
    return State.MAIN_MENU


async def show_full(update: Update, context: CallbackContext) -> State:
    talks_page, num_pages = await talks.get_talks_paginated(
        page=1,
        page_size=FULL_PROGRAM_PAGE_SIZE,
    )
    await edit_current(
        update,
        text=strings.full_program_text(1, num_pages, talks_page),
        keyboard=keyboards.get_full_program_menu(1, num_pages),
    )
    return State.MAIN_MENU


async def page(update: Update, context: CallbackContext) -> State:
    data = parse_callback_data_string(update.callback_query.data)
    page_num = int(data.params.get("page", 1))
    talks_page, num_pages = await talks.get_talks_paginated(
        page=page_num,
        page_size=FULL_PROGRAM_PAGE_SIZE,
    )
    await edit_current(
        update,
        text=strings.full_program_text(page_num, num_pages, talks_page),
        keyboard=keyboards.get_full_program_menu(page_num, num_pages),
    )
    return State.MAIN_MENU
