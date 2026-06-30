import logging

from django.contrib.auth.models import User
from django.utils import timezone
from telegram import Update

from metup_bot.models import Event, Talk, TelegramProfile, UserRole

logger = logging.getLogger(__name__)


def get_or_create_user(update: Update) -> User:
    
    #возвращает django-пользователя по tg id.

    tg_user = update.effective_user
    try:
        profile = TelegramProfile.objects.select_related("user").get(
            telegram_id=tg_user.id
        )
        return profile.user
    except TelegramProfile.DoesNotExist:
        user = User.objects.create_user(
            username=f"tg_{tg_user.id}",
            first_name=tg_user.first_name or "",
            last_name=tg_user.last_name or "",
        )
        TelegramProfile.objects.create(
            user=user,
            telegram_id=tg_user.id,
            telegram_username=tg_user.username or "",
        )
        UserRole.objects.create(user=user, role=UserRole.Role.GUEST)
        logger.info("Новый пользователь: tg_id=%s", tg_user.id)
        return user


def get_user_role(user: User) -> str | None:
    role_obj = UserRole.objects.filter(user=user).first()
    return role_obj.role if role_obj else None


def get_current_event() -> Event | None:
    return Event.objects.filter(is_current=True).first()


def get_active_talk(event: Event) -> Talk | None:
    now = timezone.now()
    return (
        Talk.objects.filter(
            event=event,
            state="active",
            scheduled_start__lte=now,
            scheduled_end__gte=now,
        )
        .order_by("scheduled_start")
        .first()
    )
