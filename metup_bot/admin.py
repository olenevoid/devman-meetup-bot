from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import User

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


admin.site.register(Donation)
admin.site.register(Event)
admin.site.register(NetworkingProfile)
admin.site.register(Question)
admin.site.register(Talk)
admin.site.register(TelegramProfile)
admin.site.register(UserRole)
