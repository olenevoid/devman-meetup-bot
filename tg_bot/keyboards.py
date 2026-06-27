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
