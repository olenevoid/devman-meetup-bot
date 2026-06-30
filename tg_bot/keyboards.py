from html import escape

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from tg_bot.callbacks import Callback, CallbackButton


def get_main_menu(
    roles: set[str], unanswered_count: int = 0
) -> InlineKeyboardMarkup:
    rows = [
        [
            CallbackButton("📅 Программа", Callback.SHOW_PROGRAM),
            CallbackButton("❓ Спросить", Callback.ASK_SPEAKER),
        ],
        [
            CallbackButton("🤝 Нетворкинг", Callback.NETWORKING),
            CallbackButton("💰 Донат", Callback.DONATE),
        ],
    ]
    if "speaker" in roles:
        if unanswered_count > 0:
            label = f"🎤 Мой доклад ({unanswered_count})"
        else:
            label = "🎤 Мой доклад"
        rows.append([CallbackButton(label, Callback.SPEAKER_CABINET)])
    return InlineKeyboardMarkup(rows)


def menu_only() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[CallbackButton("Меню", Callback.MENU)]])


def get_ask_prompt_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                CallbackButton("✖️ Отмена", Callback.MENU),
                CallbackButton("Меню", Callback.MENU),
            ]
        ]
    )


def get_question_sent_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                CallbackButton("❓ Ещё вопрос", Callback.ASK_SPEAKER),
                CallbackButton("Меню", Callback.MENU),
            ]
        ]
    )


def get_program_menu(has_active_talk: bool) -> InlineKeyboardMarkup:
    rows = []
    if has_active_talk:
        rows.append(
            [CallbackButton("❓ Спросить сейчас", Callback.ASK_SPEAKER)]
        )
    rows.append([CallbackButton("🗓 Полная программа", Callback.PROG_FULL)])
    rows.append([CallbackButton("Меню", Callback.MENU)])
    return InlineKeyboardMarkup(rows)


def get_full_program_menu(page: int, num_pages: int) -> InlineKeyboardMarkup:
    rows = []
    nav_row = []
    if page > 1:
        nav_row.append(
            CallbackButton("◀️ Назад", Callback.PROG_PAGE, page=page - 1)
        )
    if page < num_pages:
        nav_row.append(
            CallbackButton("Вперёд ▶️", Callback.PROG_PAGE, page=page + 1)
        )
    if nav_row:
        rows.append(nav_row)
    rows.append([CallbackButton("Меню", Callback.MENU)])
    return InlineKeyboardMarkup(rows)


def _question_preview(text: str) -> str:
    escaped = escape(text)
    if len(escaped) > 30:
        return f"«{escaped[:30]}…»"
    return f"«{escaped}»"


def _question_button(question) -> CallbackButton:
    marker = "✅" if question.is_answered else "✉️"
    return CallbackButton(
        f"{_question_preview(question.text)} {marker}",
        Callback.SPK_QUESTION,
        id=question.id,
    )


def get_speaker_cabinet_menu(
    talk,
    active_talk,
    total: int,
    unanswered: int,
) -> InlineKeyboardMarkup:
    rows = []
    if talk is None:
        rows.append([CallbackButton("Меню", Callback.MENU)])
        return InlineKeyboardMarkup(rows)
    state = talk.state
    if state == "active":
        rows.append([CallbackButton("⏹ Завершить доклад", Callback.SPK_END)])
    elif state == "planned":
        blocked = active_talk is not None and active_talk.pk != talk.pk
        if not blocked:
            rows.append(
                [CallbackButton("▶️ Начать доклад", Callback.SPK_START)]
            )
    if state in ("active", "finished") and total > 0:
        if unanswered > 0:
            label = f"✉️ Вопросы ({unanswered})"
        else:
            label = "✉️ Вопросы"
        rows.append([CallbackButton(label, Callback.SPK_LIST)])
    rows.append([CallbackButton("Меню", Callback.MENU)])
    return InlineKeyboardMarkup(rows)


def get_questions_list_menu(
    questions: list, page: int, num_pages: int
) -> InlineKeyboardMarkup:
    rows = []
    for question in questions:
        rows.append([_question_button(question)])
    nav_row = []
    if page > 1:
        nav_row.append(
            CallbackButton("◀️ Назад", Callback.SPK_LIST, page=page - 1)
        )
    if page < num_pages:
        nav_row.append(
            CallbackButton("Вперёд ▶️", Callback.SPK_LIST, page=page + 1)
        )
    if nav_row:
        rows.append(nav_row)
    rows.append(
        [
            CallbackButton("⬅️ К докладу", Callback.SPEAKER_CABINET),
            CallbackButton("Меню", Callback.MENU),
        ]
    )
    return InlineKeyboardMarkup(rows)


def get_question_detail_menu(question) -> InlineKeyboardMarkup:
    rows = []
    if not question.is_answered:
        rows.append(
            [
                CallbackButton(
                    "✅ Отметить отвеченным",
                    Callback.SPK_ANSWER,
                    id=question.id,
                )
            ]
        )
    rows.append(
        [
            CallbackButton("⬅️ К списку", Callback.SPK_LIST),
            CallbackButton("Меню", Callback.MENU),
        ]
    )
    return InlineKeyboardMarkup(rows)


def get_networking_intro_menu(
    button_label: str | None = None,
    fav_count: int = 0,
) -> InlineKeyboardMarkup:
    rows = []
    if button_label:
        rows.append([CallbackButton(button_label, Callback.NET_FILL_PROFILE)])
    if fav_count:
        rows.append(
            [
                CallbackButton(
                    f"⭐ Избранное ({fav_count})",
                    Callback.NET_FAVORITES,
                )
            ]
        )
    rows.append([CallbackButton("Меню", Callback.MENU)])
    return InlineKeyboardMarkup(rows)


def get_networking_card_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                CallbackButton("⭐ В избранное", Callback.NET_FAVORITE),
                CallbackButton("⏭ Пропустить", Callback.NET_NEXT),
            ],
            [CallbackButton("Меню", Callback.MENU)],
        ]
    )


def get_networking_favorites_menu() -> InlineKeyboardMarkup:
    return menu_only()


def get_donation_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                CallbackButton("100 ₽", Callback.DON_PRESET, amount=100),
                CallbackButton("300 ₽", Callback.DON_PRESET, amount=300),
                CallbackButton("500 ₽", Callback.DON_PRESET, amount=500),
            ],
            [CallbackButton("✍️ Другая сумма", Callback.DON_CUSTOM)],
            [CallbackButton("Меню", Callback.MENU)],
        ]
    )


def get_donation_payment_menu(
    amount: int, confirmation_url: str, donation_id: int
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    f"💳 Оплатить {amount} ₽", url=confirmation_url
                )
            ],
            [
                CallbackButton(
                    "✅ Я оплатил", Callback.DON_CHECK, id=donation_id
                )
            ],
            [CallbackButton("Меню", Callback.MENU)],
        ]
    )
