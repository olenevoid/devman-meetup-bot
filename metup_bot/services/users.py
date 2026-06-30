from asgiref.sync import sync_to_async
from django.db import transaction

from metup_bot.models import TelegramProfile, User, UserRole


@sync_to_async
def get_roles_for_telegram_id(tg_id: int) -> set[str]:
    queryset = UserRole.objects.filter(
        user__telegram_profile__telegram_id=tg_id
    )
    return set(queryset.values_list("role", flat=True))


@sync_to_async
def get_or_create_profile(tg_id: int, username: str = "") -> TelegramProfile:
    profile = TelegramProfile.objects.filter(telegram_id=tg_id).first()
    if profile is None:
        with transaction.atomic():
            user = User.objects.create(username=f"tg_{tg_id}")
            profile = TelegramProfile.objects.create(
                user=user,
                telegram_id=tg_id,
                telegram_username=username,
            )
    elif username and profile.telegram_username != username:
        profile.telegram_username = username
        profile.save(update_fields=["telegram_username"])
    return profile


@sync_to_async
def assign_role(tg_id: int, role: str) -> bool:
    from django.core.exceptions import ObjectDoesNotExist

    try:
        user = User.objects.get(telegram_profile__telegram_id=tg_id)
    except ObjectDoesNotExist:
        raise ValueError(f"No user for tg_id {tg_id}")
    _, created = UserRole.objects.get_or_create(user=user, role=role)
    return created
