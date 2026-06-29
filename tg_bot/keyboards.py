from telegram import InlineKeyboardMarkup

from tg_bot.callbacks import Callback, CallbackButton


def get_main_menu(roles: set[str]) -> InlineKeyboardMarkup:
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
        rows.append(
            [CallbackButton("🎤 Мой доклад", Callback.SPEAKER_CABINET)]
        )
    return InlineKeyboardMarkup(rows)


def menu_only() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[CallbackButton("Меню", Callback.MENU)]])


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
