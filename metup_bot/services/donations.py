from asgiref.sync import sync_to_async
from django.utils import timezone

from metup_bot.models import Donation, User


@sync_to_async
def create_pending_donation(
    user: User, amount_rub: int, yookassa_payment_id: str
) -> Donation:
    return Donation.objects.create(
        user=user,
        amount_rub=amount_rub,
        yookassa_payment_id=yookassa_payment_id,
        status="pending",
    )


@sync_to_async
def get_donation(donation_id: int) -> Donation | None:
    return Donation.objects.filter(pk=donation_id).first()


@sync_to_async
def mark_donation_paid(donation: Donation) -> Donation:
    donation.status = "paid"
    donation.paid_at = timezone.now()
    donation.save(update_fields=["status", "paid_at"])
    return donation
