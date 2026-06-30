import logging
from uuid import uuid4

from yookassa import Configuration, Payment

from tg_bot.settings import YOOKASSA_SECRET_KEY, YOOKASSA_SHOP_ID

logger = logging.getLogger(__name__)

Configuration.configure(YOOKASSA_SHOP_ID, YOOKASSA_SECRET_KEY)
logger.info(
    "YooKassa configured with shop_id=%s secret_set=%s",
    YOOKASSA_SHOP_ID,
    bool(YOOKASSA_SECRET_KEY),
)


def create_payment(
    amount_rub: int,
    description: str,
    return_url: str,
    metadata: dict | None = None,
):
    if not return_url:
        raise ValueError("YooKassa return_url must not be empty")
    if not YOOKASSA_SHOP_ID or not YOOKASSA_SECRET_KEY:
        raise ValueError(
            "YOOKASSA_SHOP_ID and YOOKASSA_SECRET_KEY must be set"
        )

    idempotence_key = str(uuid4())
    payload = {
        "amount": {
            "value": f"{amount_rub}.00",
            "currency": "RUB",
        },
        "confirmation": {
            "type": "redirect",
            "return_url": return_url,
        },
        "capture": True,
        "description": description,
        "metadata": metadata or {},
    }
    logger.info(
        "Creating YooKassa payment: amount=%s return_url=%s",
        amount_rub,
        return_url,
    )
    return Payment.create(payload, idempotence_key)


def get_payment(payment_id: str):
    return Payment.find_one(payment_id)
