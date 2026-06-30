from telegram import Update
from telegram.ext import CallbackContext

from metup_bot.services import events, users
from tg_bot import keyboards, strings
from tg_bot.callbacks import parse_callback_data_string
from tg_bot.handlers.states import State
from tg_bot.messaging import edit_current

ROLE_LABEL = {"guest": "гость", "speaker": "спикер"}


async def enter(update: Update, context: CallbackContext) -> State:
    future_events = await events.get_future_events()
    if not future_events:
        await edit_current(
            update,
            text=strings.future_no_events_text(),
            keyboard=keyboards.menu_only(),
        )
        return State.MAIN_MENU
    await edit_current(
        update,
        text=strings.future_events_list_text(),
        keyboard=keyboards.get_future_events_menu(future_events),
    )
    return State.MAIN_MENU


async def show_event(update: Update, context: CallbackContext) -> State:
    data = parse_callback_data_string(update.callback_query.data)
    event_id = int(data.params["event_id"])
    future_events = await events.get_future_events()
    event = next((e for e in future_events if e.id == event_id), None)
    if event is None:
        await edit_current(
            update,
            text=strings.future_no_events_text(),
            keyboard=keyboards.menu_only(),
        )
        return State.MAIN_MENU
    await edit_current(
        update,
        text=strings.future_event_sign_text(event.title),
        keyboard=keyboards.get_future_event_sign_menu(event.id),
    )
    return State.MAIN_MENU


async def sign_guest(update: Update, context: CallbackContext) -> State:
    data = parse_callback_data_string(update.callback_query.data)
    event_id = int(data.params["event_id"])
    tg_id = update.effective_user.id
    created = await users.assign_role(tg_id, "guest")
    future_events = await events.get_future_events()
    event = next((e for e in future_events if e.id == event_id), None)
    event_title = event.title if event else "?"
    if created:
        text = strings.signed_as_text("guest", event_title)
    else:
        text = strings.already_signed_text("guest", event_title)
    await edit_current(
        update,
        text=text,
        keyboard=keyboards.get_future_event_sign_menu(event_id),
    )
    return State.MAIN_MENU


async def sign_speaker(update: Update, context: CallbackContext) -> State:
    data = parse_callback_data_string(update.callback_query.data)
    event_id = int(data.params["event_id"])
    tg_id = update.effective_user.id
    created = await users.assign_role(tg_id, "speaker")
    future_events = await events.get_future_events()
    event = next((e for e in future_events if e.id == event_id), None)
    event_title = event.title if event else "?"
    if created:
        text = strings.signed_as_text("speaker", event_title)
    else:
        text = strings.already_signed_text("speaker", event_title)
    await edit_current(
        update,
        text=text,
        keyboard=keyboards.get_future_event_sign_menu(event_id),
    )
    return State.MAIN_MENU
