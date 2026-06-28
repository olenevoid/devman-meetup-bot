import logging
import os

from django.core.management.base import BaseCommand
from telegram.ext import Application

from metup_bot.common_handlers import build_common_handlers
from metup_bot.user_handlers import build_user_handlers

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Запускает Telegram-бота митапа"

    def handle(self, *args, **options):
        token = os.environ.get("TELEGRAM_BOT_TOKEN")
        if not token:
            self.stderr.write(
                "Ошибка: переменная TELEGRAM_BOT_TOKEN не задана."
            )
            return

        self.stdout.write("Запускаю бота...")
        app = Application.builder().token(token).build()

        # общий /start
        for handler in build_common_handlers():
            app.add_handler(handler)

        # гостевые хендлеры
        for handler in build_user_handlers():
            app.add_handler(handler)

        # хендлеры спикера

        # хендлеры организатора


        logger.info("Бот запущен. Ctrl+C для остановки.")
        app.run_polling()
