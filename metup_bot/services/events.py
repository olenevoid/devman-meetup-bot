from asgiref.sync import sync_to_async

from metup_bot.models import Event


@sync_to_async
def get_future_events():
    current = Event.objects.filter(is_current=True).first()
    if current is None or current.starts_at is None:
        return []
    return list(
        Event.objects.filter(
            is_current=False,
            starts_at__isnull=False,
            starts_at__gt=current.starts_at,
        ).order_by("starts_at")
    )


@sync_to_async
def get_future_events_count():
    current = Event.objects.filter(is_current=True).first()
    if current is None or current.starts_at is None:
        return 0
    return Event.objects.filter(
        is_current=False,
        starts_at__isnull=False,
        starts_at__gt=current.starts_at,
    ).count()
