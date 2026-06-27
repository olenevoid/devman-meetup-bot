from asgiref.sync import sync_to_async

from metup_bot.models import UserRole


@sync_to_async
def get_roles_for_telegram_id(tg_id: int) -> set[str]:
    queryset = UserRole.objects.filter(
        user__telegram_profile__telegram_id=tg_id
    )
    return set(queryset.values_list("role", flat=True))
