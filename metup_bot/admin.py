import logging

from asgiref.sync import async_to_sync
from django import forms
from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import Count
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.urls import path, reverse
from django.utils.text import Truncator
from telegram import Bot
from telegram.request import HTTPXRequest

from metup_bot.models import (
    Donation,
    Event,
    NetworkingProfile,
    Question,
    Talk,
    TelegramProfile,
    UserRole,
)
from tg_bot.settings import BOT_PROXY, TG_BOT_TOKEN

logger = logging.getLogger(__name__)


def send_telegram_broadcast(chat_ids, text):
    if BOT_PROXY:
        bot = Bot(
            token=TG_BOT_TOKEN,
            request=HTTPXRequest(proxy=BOT_PROXY),
        )
    else:
        bot = Bot(token=TG_BOT_TOKEN)

    async def _send():
        sent = 0
        failed = 0
        for chat_id in chat_ids:
            try:
                await bot.send_message(chat_id=chat_id, text=text)
                sent += 1
            except Exception:
                logger.exception("Broadcast failed for chat_id %s", chat_id)
                failed += 1
        return sent, failed

    return async_to_sync(_send)()


class BroadcastForm(forms.Form):
    text = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 5, "cols": 60}),
        label="Сообщение",
    )
    role = forms.ChoiceField(
        choices=[("", "Все")] + list(UserRole.Role.choices),
        required=False,
        label="Роль получателей",
    )


class TelegramProfileInline(admin.StackedInline):
    model = TelegramProfile
    fk_name = "user"
    can_delete = False
    max_num = 1
    extra = 0


class UserRoleInline(admin.TabularInline):
    model = UserRole
    extra = 1


@admin.display(description="Роли")
def _roles_display(user):
    roles = [role.get_role_display() for role in user.roles.all()]
    return ", ".join(roles) if roles else "—"


class RoleListFilter(admin.SimpleListFilter):
    title = "роль"
    parameter_name = "role"

    def lookups(self, request, model_admin):
        return UserRole.Role.choices

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            return queryset.filter(roles__role=value).distinct()
        return queryset


admin.site.unregister(User)


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = (
        "username",
        "first_name",
        "last_name",
        "is_staff",
        _roles_display,
    )
    list_filter = ("is_staff", "is_superuser", "is_active", RoleListFilter)
    search_fields = ("username", "email", "first_name", "last_name")
    inlines = (TelegramProfileInline, UserRoleInline)

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("roles")


class TalkAdminForm(forms.ModelForm):
    class Meta:
        model = Talk
        fields = "__all__"

    def clean_state(self):
        new_state = self.cleaned_data["state"]
        is_new = self.instance.pk is None
        old_state = None if is_new else self.instance.state

        if old_state == Talk.State.FINISHED:
            raise ValidationError("Завершённый доклад не может менять статус.")

        if new_state == Talk.State.ACTIVE:
            event = self.cleaned_data.get("event") or self.instance.event
            qs = Talk.objects.filter(state=Talk.State.ACTIVE, event=event)
            if not is_new:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError("Другой доклад уже идёт.")

        return new_state


class TalkInline(admin.TabularInline):
    model = Talk
    form = TalkAdminForm
    extra = 1
    fields = ("speaker", "title", "scheduled_start", "state", "order_index")


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "starts_at", "is_current", "talks_count")
    readonly_fields = ("created_at",)
    search_fields = ("title",)
    inlines = (TalkInline,)
    change_form_template = "admin/metup_bot/event/change_form.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "<path:object_id>/broadcast/",
                self.admin_site.admin_view(self.broadcast_view),
                name="metup_bot_event_broadcast",
            ),
        ]
        return custom_urls + urls

    def broadcast_view(self, request, object_id):
        event = self.get_object(request, object_id)
        if event is None:
            raise Http404("Event not found.")

        if request.method == "POST":
            form = BroadcastForm(request.POST)
            if form.is_valid():
                text = form.cleaned_data["text"]
                role = form.cleaned_data["role"]
                profiles = TelegramProfile.objects.select_related("user").all()
                if role:
                    profiles = profiles.filter(user__roles__role=role)

                chat_ids = list(profiles.values_list("telegram_id", flat=True))
                sent, failed = send_telegram_broadcast(chat_ids, text)
                level = messages.SUCCESS if failed == 0 else messages.WARNING
                self.message_user(
                    request,
                    f"Отправлено: {sent}, не удалось: {failed}.",
                    level,
                )
                return HttpResponseRedirect(
                    reverse(
                        "admin:metup_bot_event_change",
                        args=[object_id],
                    )
                )
        else:
            form = BroadcastForm()

        context = {
            **self.admin_site.each_context(request),
            "title": f"Рассылка: {event.title}",
            "subtitle": None,
            "event": event,
            "form": form,
            "opts": self.model._meta,
            "is_popup": False,
        }
        return render(request, "admin/metup_bot/event/broadcast.html", context)

    def get_queryset(self, request):
        return (
            super().get_queryset(request).annotate(_talks_count=Count("talks"))
        )

    @admin.display(description="Доклады", ordering="_talks_count")
    def talks_count(self, obj):
        return obj._talks_count

    def save_model(self, request, obj, form, change):
        if obj.is_current:
            Event.objects.filter(is_current=True).exclude(pk=obj.pk).update(
                is_current=False,
            )
        super().save_model(request, obj, form, change)


@admin.register(Talk)
class TalkAdmin(admin.ModelAdmin):
    form = TalkAdminForm
    list_display = (
        "title",
        "event",
        "speaker",
        "state",
        "scheduled_start",
        "order_index",
    )
    list_editable = ("state",)
    list_filter = ("state", "event")
    search_fields = ("title",)
    autocomplete_fields = ("speaker", "event")
    ordering = ("event", "order_index")
    readonly_fields = ("created_at",)

    def changelist_view(self, request, extra_context=None):
        try:
            return super().changelist_view(request, extra_context)
        except IntegrityError:
            self.message_user(
                request,
                "В рамках события может идти только один доклад одновременно.",
                messages.ERROR,
            )
            return HttpResponseRedirect(request.get_full_path())


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ("user", "amount_rub", "status", "created_at", "paid_at")
    list_filter = ("status",)
    date_hierarchy = "paid_at"

    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in self.model._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(NetworkingProfile)
class NetworkingProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "stack", "is_published", "updated_at")
    list_filter = ("is_published",)
    search_fields = ("bio", "stack", "contact")


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = (
        "truncated_text",
        "talk",
        "author",
        "is_answered",
        "created_at",
    )
    list_filter = ("talk", "is_answered")
    search_fields = ("text",)
    readonly_fields = ("talk", "author", "text", "created_at")

    @admin.display(description="Текст")
    def truncated_text(self, obj):
        return Truncator(obj.text).chars(50)


admin.site.register(TelegramProfile)
admin.site.register(UserRole)
