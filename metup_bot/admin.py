from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import Count

from django.utils.text import Truncator

from metup_bot.models import (
    Donation,
    Event,
    NetworkingProfile,
    Question,
    Talk,
    TelegramProfile,
    UserRole,
)


class TelegramProfileInline(admin.StackedInline):
    model = TelegramProfile
    fk_name = "user"
    can_delete = False
    verbose_name_plural = "Telegram profile"
    max_num = 1
    extra = 0


class UserRoleInline(admin.TabularInline):
    model = UserRole
    extra = 1


@admin.display(description="Roles")
def _roles_display(user):
    roles = [role.get_role_display() for role in user.roles.all()]
    return ", ".join(roles) if roles else "—"


class RoleListFilter(admin.SimpleListFilter):
    title = "role"
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


class TalkInline(admin.TabularInline):
    model = Talk
    extra = 1
    fields = ("speaker", "title", "scheduled_start", "state", "order_index")


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "starts_at", "is_current", "talks_count")
    readonly_fields = ("created_at",)
    search_fields = ("title",)
    inlines = (TalkInline,)

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .annotate(_talks_count=Count("talks"))
        )

    @admin.display(description="Talks", ordering="_talks_count")
    def talks_count(self, obj):
        return obj._talks_count

    def save_model(self, request, obj, form, change):
        if obj.is_current:
            Event.objects.filter(is_current=True).exclude(pk=obj.pk).update(
                is_current=False,
            )
        super().save_model(request, obj, form, change)


TALK_STATE_CHOICES = (
    ("planned", "Planned"),
    ("active", "Active"),
    ("finished", "Finished"),
)


class TalkAdminForm(forms.ModelForm):
    state = forms.ChoiceField(choices=TALK_STATE_CHOICES)

    class Meta:
        model = Talk
        fields = "__all__"

    def clean_state(self):
        new_state = self.cleaned_data["state"]
        is_new = self.instance.pk is None
        old_state = None if is_new else self.instance.state

        if old_state == "finished":
            raise ValidationError(
                "A finished talk cannot change state."
            )

        if new_state == "active":
            qs = Talk.objects.filter(state="active")
            if not is_new:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError(
                    "Another talk is already active."
                )

        return new_state


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
    list_filter = ("state", "event")
    search_fields = ("title",)
    autocomplete_fields = ("speaker", "event")
    ordering = ("event", "order_index")
    readonly_fields = ("created_at",)


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

    @admin.display(description="Text")
    def truncated_text(self, obj):
        return Truncator(obj.text).chars(50)


admin.site.register(TelegramProfile)
admin.site.register(UserRole)
