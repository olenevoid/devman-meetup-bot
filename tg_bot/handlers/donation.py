import logging

from asgiref.sync import sync_to_async
from telegram import Update
from telegram.ext import CallbackContext

from metup_bot.services import donations, users
from tg_bot import keyboards, strings
from tg_bot.callbacks import parse_callback_data_string
from tg_bot.handlers.states import State
from tg_bot.messaging import edit_current, replace_current
from tg_bot.payment import create_payment, get_payment
from tg_bot.settings import YOOKASSA_RETURN_URL

logger = logging.getLogger(__name__)

MIN_AMOUNT = 10
MAX_AMOUNT = 1_000_000


async def _get_or_create_user(update: Update):
    tg_id = update.effective_user.id
    username = update.effective_user.username or ""
    return await users.get_or_create_profile(tg_id, username)


def _return_url(context: CallbackContext) -> str:
    if context.bot.username:
        return f"https://t.me/{context.bot.username}"
    if YOOKASSA_RETURN_URL:
        return YOOKASSA_RETURN_URL
    raise ValueError(
        "YOOKASSA_RETURN_URL must be set when the bot has no username"
    )


def _parse_amount(text: str) -> int | None:
    try:
        value = int(text.strip())
    except (ValueError, TypeError):
        return None
    if not MIN_AMOUNT <= value <= MAX_AMOUNT:
        return None
    return value


async def _create_donation_payment(
    update: Update, context: CallbackContext, amount: int
):
    profile = await _get_or_create_user(update)
    description = "Поддержка Python Meetup"
    payment = await sync_to_async(create_payment)(
        amount_rub=amount,
        description=description,
        return_url=_return_url(context),
        metadata={"telegram_id": profile.telegram_id},
    )
    user = await sync_to_async(lambda: profile.user)()
    donation = await donations.create_pending_donation(
        user=user,
        amount_rub=amount,
        yookassa_payment_id=payment.id,
    )
    return payment, donation


async def _render_payment_message(
    update: Update,
    context: CallbackContext,
    amount: int,
    confirmation_url: str,
    donation_id: int,
) -> None:
    text = strings.donation_payment_text(amount)
    keyboard = keyboards.get_donation_payment_menu(
        amount, confirmation_url, donation_id
    )
    if update.callback_query is not None:
        await edit_current(update, text, keyboard)
    else:
        await replace_current(update, context, text, keyboard)


async def enter(update: Update, context: CallbackContext) -> State:
    await edit_current(
        update,
        text=strings.donation_text(),
        keyboard=keyboards.get_donation_menu(),
    )
    return State.IN_DONATION


async def preset_amount(update: Update, context: CallbackContext) -> State:
    data = parse_callback_data_string(update.callback_query.data)
    amount = int(data.params["amount"])
    try:
        payment, donation = await _create_donation_payment(
            update, context, amount
        )
    except Exception:
        logger.exception(
            "Failed to create donation payment: amount=%s", amount
        )
        await edit_current(
            update,
            text=strings.donation_error_text(),
            keyboard=keyboards.menu_only(),
        )
        return State.MAIN_MENU
    await _render_payment_message(
        update,
        context,
        amount,
        payment.confirmation.confirmation_url,
        donation.id,
    )
    return State.MAIN_MENU


async def input_custom_amount(
    update: Update, context: CallbackContext
) -> State:
    await edit_current(
        update,
        text=strings.donation_custom_prompt_text(),
        keyboard=keyboards.menu_only(),
    )
    return State.DON_AWAIT_AMOUNT


async def receive_custom_amount(
    update: Update, context: CallbackContext
) -> State:
    amount = _parse_amount(update.message.text)
    if amount is None:
        await replace_current(
            update,
            context,
            text=strings.donation_invalid_amount_text(),
            keyboard=keyboards.menu_only(),
        )
        return State.DON_AWAIT_AMOUNT
    try:
        payment, donation = await _create_donation_payment(
            update, context, amount
        )
    except Exception:
        logger.exception(
            "Failed to create custom donation payment: amount=%s", amount
        )
        await replace_current(
            update,
            context,
            text=strings.donation_error_text(),
            keyboard=keyboards.menu_only(),
        )
        return State.MAIN_MENU
    await _render_payment_message(
        update,
        context,
        amount,
        payment.confirmation.confirmation_url,
        donation.id,
    )
    return State.MAIN_MENU


async def check_payment(update: Update, context: CallbackContext) -> State:
    data = parse_callback_data_string(update.callback_query.data)
    donation = await donations.get_donation(int(data.params["id"]))
    if donation is None:
        await edit_current(
            update,
            text=strings.donation_error_text(),
            keyboard=keyboards.menu_only(),
        )
        return State.MAIN_MENU
    try:
        payment = await sync_to_async(get_payment)(
            donation.yookassa_payment_id
        )
    except Exception:
        logger.exception(
            "Failed to check donation payment: donation_id=%s payment_id=%s",
            donation.id,
            donation.yookassa_payment_id,
        )
        await edit_current(
            update,
            text=strings.donation_error_text(),
            keyboard=keyboards.menu_only(),
        )
        return State.MAIN_MENU
    if payment.status == "succeeded":
        await donations.mark_donation_paid(donation)
        await edit_current(
            update,
            text=strings.donation_thanks_text(donation.amount_rub),
            keyboard=keyboards.menu_only(),
        )
    elif payment.status in ("canceled", "failed"):
        await edit_current(
            update,
            text=strings.donation_canceled_text(),
            keyboard=keyboards.menu_only(),
        )
    else:
        await edit_current(
            update,
            text=strings.donation_not_paid_text(),
            keyboard=keyboards.get_donation_payment_menu(
                donation.amount_rub,
                payment.confirmation.confirmation_url,
                donation.id,
            ),
        )
    return State.MAIN_MENU
