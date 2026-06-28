import logging

from django.contrib.auth.models import User
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from metup_bot.models import (
    Donation,
    NetworkingProfile,
    Question,
    TelegramProfile,
)
from metup_bot.utils import (
    get_active_talk,
    get_current_event,
    get_or_create_user,
)

logger = logging.getLogger(__name__)

(
    NETWORKING_MENU,
    NETWORKING_BIO,
    NETWORKING_STACK,
    NETWORKING_CONTACT,
) = range(4)

(
    QUESTION_SELECT_TALK,
    QUESTION_ENTER_TEXT,
) = range(10, 12)

(DONATE_CONFIRM,) = range(20, 21)


def main_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("❓ Задать вопрос", callback_data="ask_question")],
        [InlineKeyboardButton("📋 Программа", callback_data="schedule")],
        [InlineKeyboardButton("🤝 Нетворкинг", callback_data="networking")],
        [InlineKeyboardButton("💛 Поддержать митап", callback_data="donate")],
    ]
    return InlineKeyboardMarkup(keyboard)


async def show_guest_menu(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    event = get_current_event()
    event_title = f'«{event.title}»' if event else "митапе"
    text = (
        f"👋 Привет! Я бот для участников {event_title}.\n\n"
        "Что умею:\n"
        "• Передать вопрос докладчику прямо во время выступления\n"
        "• Показать программу мероприятия\n"
        "• Познакомить тебя с другими разрабами\n"
        "• Принять донат для организаторов\n\n"
        "Выбери, что тебя интересует:"
    )
    await update.message.reply_text(text, reply_markup=main_menu_keyboard())


async def cmd_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Главное меню:", reply_markup=main_menu_keyboard()
    )


async def show_schedule(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    query = update.callback_query
    await query.answer()

    event = get_current_event()
    if not event:
        await query.edit_message_text("Сейчас нет активного мероприятия.")
        return

    talks = Talk.objects.filter(event=event).order_by("order_index")
    if not talks.exists():
        await query.edit_message_text("Программа пока не опубликована.")
        return

    now = timezone.now()
    lines = [f"📋 *{event.title}*\n"]
    for talk in talks:
        start = (
            talk.scheduled_start.strftime("%H:%M")
            if talk.scheduled_start
            else "—"
        )
        if (
            talk.scheduled_start
            and talk.scheduled_end
            and talk.scheduled_start <= now <= talk.scheduled_end
        ):
            prefix = "▶️"
        else:
            prefix = "🔹"
        lines.append(
            f"{prefix} {start} — *{talk.title}*\n"
            f"    👤 {talk.speaker.get_full_name() or talk.speaker.username}"
        )

    keyboard = [[InlineKeyboardButton("« Назад", callback_data="main_menu")]]
    await query.edit_message_text(
        "\n".join(lines),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def ask_question_start(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    query = update.callback_query
    await query.answer()

    event = get_current_event()
    if not event:
        await query.edit_message_text("Сейчас нет активного мероприятия.")
        return ConversationHandler.END

    talks = Talk.objects.filter(event=event).order_by("order_index")
    if not talks.exists():
        await query.edit_message_text("Докладчики ещё не добавлены.")
        return ConversationHandler.END

    active_talk = get_active_talk(event)
    buttons = []
    for talk in talks:
        label = talk.title
        if active_talk and talk.pk == active_talk.pk:
            label = f"▶️ {label} (сейчас)"
        buttons.append(
            [InlineKeyboardButton(label, callback_data=f"talk_{talk.pk}")]
        )
    buttons.append([InlineKeyboardButton("« Отмена", callback_data="main_menu")])

    await query.edit_message_text(
        "Выбери докладчика, которому хочешь задать вопрос:",
        reply_markup=InlineKeyboardMarkup(buttons),
    )
    return QUESTION_SELECT_TALK


async def question_talk_selected(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    query = update.callback_query
    await query.answer()

    talk_id = int(query.data.split("_")[1])
    try:
        talk = Talk.objects.select_related("speaker").get(pk=talk_id)
    except Talk.DoesNotExist:
        await query.edit_message_text("Доклад не найден.")
        return ConversationHandler.END

    context.user_data["question_talk_id"] = talk_id
    await query.edit_message_text(
        f"Напиши вопрос для доклада *«{talk.title}»*\n"
        f"👤 {talk.speaker.get_full_name() or talk.speaker.username}\n\n"
        "Или /cancel для отмены.",
        parse_mode="Markdown",
    )
    return QUESTION_ENTER_TEXT


async def question_text_received(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    user = get_or_create_user(update)
    talk_id = context.user_data.get("question_talk_id")

    try:
        talk = Talk.objects.select_related("speaker").get(pk=talk_id)
    except Talk.DoesNotExist:
        await update.message.reply_text("Что-то пошло не так. Попробуй снова.")
        return ConversationHandler.END

    Question.objects.create(
        talk=talk,
        author=user,
        text=update.message.text,
    )

    try:
        speaker_profile = TelegramProfile.objects.get(user=talk.speaker)
        await context.bot.send_message(
            chat_id=speaker_profile.telegram_id,
            text=(
                f"❓ Новый вопрос к твоему докладу «{talk.title}»:\n\n"
                f"{update.message.text}"
            ),
        )
    except TelegramProfile.DoesNotExist:
        logger.warning("У спикера %s нет Telegram-профиля", talk.speaker)

    await update.message.reply_text(
        "✅ Вопрос отправлен! Докладчик ответит после выступления.",
        reply_markup=main_menu_keyboard(),
    )
    context.user_data.pop("question_talk_id", None)
    return ConversationHandler.END


async def question_cancel(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    await update.message.reply_text(
        "Отменено.", reply_markup=main_menu_keyboard()
    )
    return ConversationHandler.END


async def networking_start(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    query = update.callback_query
    await query.answer()

    user = get_or_create_user(update)

    if NetworkingProfile.objects.filter(
        user=user, is_published=True
    ).exists():
        return await _show_partner(update, context, user)

    keyboard = [
        [InlineKeyboardButton("Погнали!", callback_data="networking_go")],
        [InlineKeyboardButton("« Назад", callback_data="main_menu")],
    ]
    await query.edit_message_text(
        "🤝 *Нетворкинг*\n\n"
        "Я соберу твою мини-анкету и покажу тебе анкету другого участника. "
        "Если понравится, получишь его контакт в Telegram. "
        "Можно пропустить и посмотреть следующего.\n\n",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return NETWORKING_MENU


async def networking_go(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "Как тебя зовут? (Имя, которое увидят другие участники)\n\n"
        "/cancel — отмена"
    )
    return NETWORKING_BIO


async def networking_bio(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    context.user_data["net_name"] = update.message.text
    await update.message.reply_text(
        "Расскажи немного о себе и своём стеке:\n"
        "Например: «3 года пишу на Python, интересует DevOps»\n\n"
        "/cancel — отмена"
    )
    return NETWORKING_STACK


async def networking_stack(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    context.user_data["net_bio"] = update.message.text
    await update.message.reply_text(
        "Напиши свой Telegram-контакт, который получит собеседник:\n"
        "Например: @username\n\n"
        "/cancel — отмена"
    )
    return NETWORKING_CONTACT


async def networking_contact(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    user = get_or_create_user(update)
    contact = update.message.text

    profile, _ = NetworkingProfile.objects.update_or_create(
        user=user,
        defaults={
            "bio": context.user_data.get("net_bio", ""),
            "stack": context.user_data.get("net_name", ""),
            "contact": contact,
            "is_published": True,
        },
    )

    for key in ("net_name", "net_bio"):
        context.user_data.pop(key, None)

    await update.message.reply_text("✅ Анкета сохранена! Ищу тебе собеседника...")
    return await _show_partner_message(update, context, user)


async def _show_partner(
    update: Update, context: ContextTypes.DEFAULT_TYPE, user: User
) -> int:
    query = update.callback_query
    await query.edit_message_text("🔍 Ищу тебе собеседника...")
    return await _show_partner_message(update, context, user, via_query=True)


async def _show_partner_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user: User,
    via_query: bool = False,
) -> int:
    skipped = context.user_data.get("net_skipped", [])

    partner_profile = (
        NetworkingProfile.objects.select_related("user")
        .filter(is_published=True)
        .exclude(user=user)
        .exclude(user__pk__in=skipped)
        .order_by("created_at")
        .first()
    )

    send = (
        update.callback_query.message.reply_text
        if via_query
        else update.message.reply_text
    )

    if not partner_profile:
        context.user_data["net_waiting"] = True
        await send(
            "😔 Пока больше никто не заполнил анкету.\n"
            "Как только кто-то зарегистрируется, я тебе сообщу!",
            reply_markup=main_menu_keyboard(),
        )
        return ConversationHandler.END

    partner = partner_profile.user
    keyboard = [
        [
            InlineKeyboardButton(
                "✅ Хочу пообщаться",
                callback_data=f"net_accept_{partner.pk}",
            ),
            InlineKeyboardButton(
                "➡️ Следующий",
                callback_data=f"net_skip_{partner.pk}",
            ),
        ],
        [InlineKeyboardButton("« В меню", callback_data="main_menu")],
    ]
    await send(
        f"👤 *{partner_profile.stack or partner.get_full_name()}*\n\n"
        f"{partner_profile.bio}\n\n"
        "Хочешь пообщаться?",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return ConversationHandler.END


async def networking_accept(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    query = update.callback_query
    await query.answer()
    user = get_or_create_user(update)

    partner_id = int(query.data.split("_")[2])
    try:
        partner_profile = NetworkingProfile.objects.select_related("user").get(
            user__pk=partner_id
        )
    except NetworkingProfile.DoesNotExist:
        await query.edit_message_text("Анкета недоступна.")
        return
    context.user_data["net_skipped"] = []

    await query.edit_message_text(
        f"🎉 Отлично! Вот контакт твоего собеседника:\n\n"
        f"*{partner_profile.stack or partner_profile.user.get_full_name()}*\n"
        f"Контакт: {partner_profile.contact}\n\n"
        "Удачного общения!",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard(),
    )


async def networking_skip(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    query = update.callback_query
    await query.answer()
    user = get_or_create_user(update)

    partner_id = int(query.data.split("_")[2])
    skipped = context.user_data.get("net_skipped", [])
    skipped.append(partner_id)
    context.user_data["net_skipped"] = skipped

    await query.edit_message_text("Ищу следующего...")
    await _show_partner_message(update, context, user, via_query=True)

# Донат

async def donate_start(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    query = update.callback_query
    await query.answer()

    keyboard = [
        [
            InlineKeyboardButton("100 ₽", callback_data="donate_100"),
            InlineKeyboardButton("300 ₽", callback_data="donate_300"),
            InlineKeyboardButton("500 ₽", callback_data="donate_500"),
        ],
        [InlineKeyboardButton("Не сейчас", callback_data="main_menu")],
    ]
    await query.edit_message_text(
        "💛 *Поддержи митап!*\n\n"
        "Все доходы идут на аренду зала и бесплатную пиццу 🍕\n\n"
        "Выбери сумму доната:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
    return DONATE_CONFIRM


async def donate_amount_selected(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    query = update.callback_query
    await query.answer()

    amount = int(query.data.split("_")[1])
    user = get_or_create_user(update)
    event = get_current_event()
    Donation.objects.create(
        user=user,
        amount_rub=amount,
        yookassa_payment_id="pending",
        status="pending",
    )

    await query.edit_message_text(
        f"✅ Спасибо! Задонатил {amount} ₽ 🙏",
        reply_markup=main_menu_keyboard(),
    )
    return ConversationHandler.END


async def donate_cancel(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    await update.message.reply_text(
        "Без проблем! Возвращаю в меню.",
        reply_markup=main_menu_keyboard(),
    )
    return ConversationHandler.END


async def main_menu_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "Главное меню:", reply_markup=main_menu_keyboard()
    )


def build_user_handlers():
    question_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(ask_question_start, pattern="^ask_question$")
        ],
        states={
            QUESTION_SELECT_TALK: [
                CallbackQueryHandler(
                    question_talk_selected, pattern=r"^talk_\d+$"
                )
            ],
            QUESTION_ENTER_TEXT: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, question_text_received
                )
            ],
        },
        fallbacks=[
            CommandHandler("cancel", question_cancel),
            CallbackQueryHandler(main_menu_callback, pattern="^main_menu$"),
        ],
    )

    networking_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(networking_start, pattern="^networking$")
        ],
        states={
            NETWORKING_MENU: [
                CallbackQueryHandler(networking_go, pattern="^networking_go$")
            ],
            NETWORKING_BIO: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, networking_bio)
            ],
            NETWORKING_STACK: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, networking_stack
                )
            ],
            NETWORKING_CONTACT: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, networking_contact
                )
            ],
        },
        fallbacks=[
            CommandHandler("cancel", question_cancel),
            CallbackQueryHandler(main_menu_callback, pattern="^main_menu$"),
        ],
    )

    donate_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(donate_start, pattern="^donate$")
        ],
        states={
            DONATE_CONFIRM: [
                CallbackQueryHandler(
                    donate_amount_selected, pattern=r"^donate_\d+$"
                )
            ],
        },
        fallbacks=[
            CommandHandler("cancel", donate_cancel),
            CallbackQueryHandler(main_menu_callback, pattern="^main_menu$"),
        ],
    )

    return [
        CommandHandler("menu", cmd_menu),
        CallbackQueryHandler(show_schedule, pattern="^schedule$"),
        CallbackQueryHandler(networking_accept, pattern=r"^net_accept_\d+$"),
        CallbackQueryHandler(networking_skip, pattern=r"^net_skip_\d+$"),
        CallbackQueryHandler(main_menu_callback, pattern="^main_menu$"),
        question_conv,
        networking_conv,
        donate_conv,
    ]
