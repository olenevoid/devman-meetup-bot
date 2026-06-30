from asgiref.sync import sync_to_async

from metup_bot.models import NetworkingProfile, User


def _update_profile_field(tg_id: int, **fields) -> NetworkingProfile:
    user = User.objects.get(telegram_profile__telegram_id=tg_id)
    profile, _ = NetworkingProfile.objects.update_or_create(
        user=user,
        defaults=fields,
    )
    return profile


@sync_to_async
def get_profile(tg_id: int) -> NetworkingProfile | None:
    return NetworkingProfile.objects.filter(
        user__telegram_profile__telegram_id=tg_id
    ).first()


@sync_to_async
def save_bio(tg_id: int, bio: str) -> NetworkingProfile:
    return _update_profile_field(tg_id, bio=bio)


@sync_to_async
def save_stack(tg_id: int, stack: str) -> NetworkingProfile:
    return _update_profile_field(tg_id, stack=stack)


@sync_to_async
def save_contact_and_publish(tg_id: int, contact: str) -> NetworkingProfile:
    return _update_profile_field(tg_id, contact=contact, is_published=True)


@sync_to_async
def get_random_unviewed_profile(
    viewer_tg_id: int, exclude_ids: list[int]
) -> NetworkingProfile | None:
    return (
        NetworkingProfile.objects.filter(is_published=True)
        .exclude(user__telegram_profile__telegram_id=viewer_tg_id)
        .exclude(pk__in=exclude_ids)
        .select_related("user__telegram_profile")
        .order_by("?")
        .first()
    )


@sync_to_async
def has_other_published_profiles(viewer_tg_id: int) -> bool:
    return (
        NetworkingProfile.objects.filter(is_published=True)
        .exclude(user__telegram_profile__telegram_id=viewer_tg_id)
        .exists()
    )


@sync_to_async
def get_profiles_by_ids(profile_ids: list[int]) -> list:
    if not profile_ids:
        return []
    return list(
        NetworkingProfile.objects.filter(
            pk__in=profile_ids,
            is_published=True,
        )
        .select_related("user__telegram_profile")
        .order_by("?")
    )
