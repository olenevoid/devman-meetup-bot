from telegram import Update
from telegram.ext import CallbackContext

from metup_bot.services import networking as net
from tg_bot import keyboards, strings
from tg_bot.handlers.states import State
from tg_bot.messaging import edit_current, replace_current

SKIPPED_KEY = "net_skipped"
FAVORITES_KEY = "net_favorites"
CURRENT_KEY = "net_current_id"


def _skipped(context: CallbackContext) -> list[int]:
    return context.user_data.setdefault(SKIPPED_KEY, [])


def _favorites(context: CallbackContext) -> list[int]:
    return context.user_data.setdefault(FAVORITES_KEY, [])


async def _render(
    update: Update,
    context: CallbackContext,
    text: str,
    keyboard,
) -> None:
    if update.callback_query is not None:
        await edit_current(update, text, keyboard)
    else:
        await replace_current(update, context, text, keyboard)


async def _show_card(
    update: Update, context: CallbackContext, profile
) -> None:
    context.user_data[CURRENT_KEY] = profile.id
    await _render(
        update,
        context,
        text=strings.networking_card_text(profile),
        keyboard=keyboards.get_networking_card_menu(),
    )


async def _browse_or_finish(update: Update, context: CallbackContext) -> State:
    viewer_id = update.effective_user.id
    exclude = _skipped(context) + _favorites(context)
    profile = await net.get_random_unviewed_profile(
        viewer_id, exclude_ids=exclude
    )
    if profile is None:
        await _render(
            update,
            context,
            text=strings.networking_all_viewed_text(),
            keyboard=keyboards.menu_only(),
        )
        return State.NET_MATCHING
    await _show_card(update, context, profile)
    return State.NET_MATCHING


async def enter(update: Update, context: CallbackContext) -> State:
    viewer_id = update.effective_user.id
    profile = await net.get_profile(viewer_id)
    fav_count = len(_favorites(context))
    if profile is None:
        await edit_current(
            update,
            text=strings.networking_intro_text(),
            keyboard=keyboards.get_networking_intro_menu(
                "✍️ Заполнить", fav_count
            ),
        )
        return State.IN_NETWORKING
    if await net.has_other_published_profiles(viewer_id):
        await edit_current(
            update,
            text=strings.networking_intro_text(),
            keyboard=keyboards.get_networking_intro_menu(
                "👀 Смотреть", fav_count
            ),
        )
    else:
        await edit_current(
            update,
            text=strings.networking_no_profiles_text(),
            keyboard=keyboards.get_networking_intro_menu(fav_count=fav_count),
        )
    return State.IN_NETWORKING


async def show_bio_form(update: Update, context: CallbackContext) -> State:
    viewer_id = update.effective_user.id
    profile = await net.get_profile(viewer_id)
    if profile is not None:
        return await _browse_or_finish(update, context)
    await edit_current(
        update,
        text=strings.networking_form_text(1),
        keyboard=keyboards.menu_only(),
    )
    return State.NET_FORM_BIO


async def receive_bio(update: Update, context: CallbackContext) -> State:
    await net.save_bio(update.effective_user.id, update.message.text)
    await replace_current(
        update,
        context,
        text=strings.networking_form_text(2),
        keyboard=keyboards.menu_only(),
    )
    return State.NET_FORM_STACK


async def receive_stack(update: Update, context: CallbackContext) -> State:
    await net.save_stack(update.effective_user.id, update.message.text)
    await replace_current(
        update,
        context,
        text=strings.networking_form_text(3),
        keyboard=keyboards.menu_only(),
    )
    return State.NET_FORM_CONTACT


async def receive_contact(update: Update, context: CallbackContext) -> State:
    await net.save_contact_and_publish(
        update.effective_user.id, update.message.text
    )
    return await _browse_or_finish(update, context)


async def skip(update: Update, context: CallbackContext) -> State:
    current = context.user_data.get(CURRENT_KEY)
    if current is not None:
        _skipped(context).append(current)
    return await _browse_or_finish(update, context)


async def favorite(update: Update, context: CallbackContext) -> State:
    current = context.user_data.get(CURRENT_KEY)
    if current is not None:
        favorites = _favorites(context)
        if current not in favorites:
            favorites.append(current)
    return await _browse_or_finish(update, context)


async def show_favorites(update: Update, context: CallbackContext) -> State:
    favorite_ids = _favorites(context)
    profiles = await net.get_profiles_by_ids(favorite_ids)
    await _render(
        update,
        context,
        text=strings.networking_favorites_text(profiles),
        keyboard=keyboards.get_networking_favorites_menu(),
    )
    return State.NET_FAVORITES
