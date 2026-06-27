from django.contrib import admin

from metup_bot.models import (
    Donation,
    Event,
    NetworkingProfile,
    Question,
    Talk,
    TelegramProfile,
    UserRole,
)

admin.site.register(Donation)
admin.site.register(Event)
admin.site.register(NetworkingProfile)
admin.site.register(Question)
admin.site.register(Talk)
admin.site.register(TelegramProfile)
admin.site.register(UserRole)
