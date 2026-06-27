from django.core.management.base import BaseCommand
from telegram.ext import ApplicationBuilder

from tg_bot.handlers.state_machines import get_root_conversation_handler
from tg_bot.settings import TG_BOT_TOKEN


class Command(BaseCommand):
    help = "Run the Telegram bot in polling mode."

    def handle(self, *args, **options):
        application = ApplicationBuilder().token(TG_BOT_TOKEN).build()
        application.add_handler(get_root_conversation_handler())
        application.run_polling()
