from asgiref.sync import sync_to_async
from django.core.paginator import Paginator

from metup_bot.models import Event, Talk


@sync_to_async
def get_current_event() -> Event | None:
    return Event.objects.filter(is_current=True).first()


@sync_to_async
def get_active_talk() -> Talk | None:
    return Talk.objects.filter(state="active").first()


@sync_to_async
def get_next_talk() -> Talk | None:
    return (
        Talk.objects.filter(event__is_current=True, state="planned")
        .order_by("order_index")
        .first()
    )


@sync_to_async
def get_talks_paginated(
    page: int = 1, page_size: int = 5
) -> tuple[list[Talk], int]:
    queryset = Talk.objects.filter(event__is_current=True).order_by(
        "order_index"
    )
    paginator = Paginator(queryset, page_size)
    page_obj = paginator.get_page(page)
    return list(page_obj.object_list), paginator.num_pages


@sync_to_async
def get_speaker_talk(tg_id: int) -> Talk | None:
    return Talk.objects.filter(
        speaker__telegram_profile__telegram_id=tg_id,
        event__is_current=True,
    ).first()


@sync_to_async
def start_talk(talk: Talk) -> Talk:
    if talk.state != "planned":
        raise ValueError(f"Cannot start talk in state '{talk.state}'")
    if Talk.objects.filter(state="active").exclude(pk=talk.pk).exists():
        raise ValueError("Another talk is already active")
    talk.state = "active"
    talk.save(update_fields=["state"])
    return talk


@sync_to_async
def end_talk(talk: Talk) -> Talk:
    if talk.state != "active":
        raise ValueError(f"Cannot end talk in state '{talk.state}'")
    talk.state = "finished"
    talk.save(update_fields=["state"])
    return talk
