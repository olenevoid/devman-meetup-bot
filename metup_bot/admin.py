from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import User
from django.db.models import Count

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


admin.site.register(Donation)
admin.site.register(NetworkingProfile)
admin.site.register(Question)
admin.site.register(Talk)
admin.site.register(TelegramProfile)
admin.site.register(UserRole)
