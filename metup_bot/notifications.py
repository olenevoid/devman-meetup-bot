import logging

logger = logging.getLogger(__name__)


async def notify_waiting_users(bot, new_profile, waiting_chat_ids: list[int]):
    name = new_profile.stack or new_profile.user.get_full_name() or "Кто-то"
    text = (
        f"🔔 Появился новый участник — *{name}*!\n"
        "Напиши /menu, чтобы найти собеседника."
    )
    for chat_id in waiting_chat_ids:
        try:
            await bot.send_message(
                chat_id=chat_id, text=text, parse_mode="Markdown"
            )
            logger.info("Уведомил %s о новом участнике", chat_id)
        except Exception as exc:
            logger.warning("Не удалось уведомить %s: %s", chat_id, exc)
