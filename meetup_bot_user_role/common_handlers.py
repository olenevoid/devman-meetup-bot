"""
Общие хендлеры бота, точка входа для всех ролей

/start, который смотрит на роль пользователя
и передаёт управление нужной функции
guest → show_guest_menu()   из user_handlers.py
speaker → show_speaker_menu() из speaker_handlers.py
organizer → show_organizer_menu() из organizer_handlers.py

подключаться будет в run_bot.py
"""

import logging

from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from metup_bot.models import UserRole
from metup_bot.utils import get_or_create_user, get_user_role
from metup_bot.user_handlers import show_guest_menu
from metup_bot.organizer_handlers import show_organizer_menu
from metup_bot.speaker_handlers import show_speaker_menu


logger = logging.getLogger(__name__)


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    единая точка входа /start для всех пользователей
    будет определять роль и отправлять в нужное  меню
    """
    user = get_or_create_user(update)
    role = get_user_role(user)

    if role == UserRole.Role.SPEAKER:
        await show_speaker_menu(update, context, user)

    elif role == UserRole.Role.ORGANIZER:
        # подключим когда поймем кто будет делать
        from metup_bot.organizer_handlers import show_organizer_menu
        await show_organizer_menu(update, context, user)

    else:
        # по умолчанию гостевое меню
        from metup_bot.user_handlers import show_guest_menu
        await show_guest_menu(update, context)


def build_common_handlers():
    """
    Возвращает список общих хендлеров
    надо регистрировать их первыми, до хендлеров конкретной роли
    """
    return [
        CommandHandler("start", cmd_start),
    ]
