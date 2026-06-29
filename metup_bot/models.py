from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q


class TelegramProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="telegram_profile",
        verbose_name="пользователь",
    )
    telegram_id = models.BigIntegerField(
        unique=True,
        verbose_name="ID в Telegram",
    )
    telegram_username = models.CharField(
        max_length=64,
        blank=True,
        verbose_name="имя пользователя в Telegram",
    )

    class Meta:
        verbose_name = "профиль Telegram"
        verbose_name_plural = "профили Telegram"

    def __str__(self):
        return f"@{self.telegram_username or self.telegram_id}"


class UserRole(models.Model):
    class Role(models.TextChoices):
        GUEST = "guest", "Гость"
        SPEAKER = "speaker", "Докладчик"
        ORGANIZER = "organizer", "Организатор"

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="roles",
        verbose_name="пользователь",
    )
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        verbose_name="роль",
    )
    assigned_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="назначен",
    )

    class Meta:
        verbose_name = "роль пользователя"
        verbose_name_plural = "роли пользователей"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "role"],
                name="unique_user_role",
            ),
        ]

    def __str__(self):
        return f"{self.user} · {self.role}"


class Event(models.Model):
    title = models.CharField(max_length=128, verbose_name="название")
    description = models.TextField(blank=True, verbose_name="описание")
    starts_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="начало",
    )
    is_current = models.BooleanField(default=False, verbose_name="текущее")
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="создано",
    )

    class Meta:
        verbose_name = "событие"
        verbose_name_plural = "события"
        constraints = [
            models.UniqueConstraint(
                fields=["is_current"],
                condition=Q(is_current=True),
                name="single_current_event",
            ),
        ]

    def __str__(self):
        return self.title


class Talk(models.Model):
    class State(models.TextChoices):
        PLANNED = "planned", "Запланирован"
        ACTIVE = "active", "Идёт"
        FINISHED = "finished", "Завершён"

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="talks",
        verbose_name="событие",
    )
    speaker = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="talks",
        verbose_name="докладчик",
    )
    title = models.CharField(max_length=200, verbose_name="название")
    description = models.TextField(blank=True, verbose_name="описание")
    scheduled_start = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="запланированное начало",
    )
    scheduled_end = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="запланированное окончание",
    )
    state = models.CharField(
        max_length=20,
        choices=State.choices,
        default=State.PLANNED,
        verbose_name="статус",
    )
    order_index = models.IntegerField(
        default=0,
        verbose_name="порядковый номер",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="создано",
    )

    class Meta:
        verbose_name = "доклад"
        verbose_name_plural = "доклады"
        constraints = [
            models.UniqueConstraint(
                fields=["event"],
                condition=Q(state="active"),
                name="single_active_talk_per_event",
            ),
        ]

    def __str__(self):
        return self.title


class Question(models.Model):
    talk = models.ForeignKey(
        Talk,
        on_delete=models.CASCADE,
        related_name="questions",
        verbose_name="доклад",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="questions",
        verbose_name="автор",
    )
    text = models.TextField(verbose_name="текст")
    is_answered = models.BooleanField(default=False, verbose_name="отвечен")
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="создан",
    )

    class Meta:
        verbose_name = "вопрос"
        verbose_name_plural = "вопросы"

    def __str__(self):
        return f"Q for {self.talk}"


class NetworkingProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="networking_profile",
        verbose_name="пользователь",
    )
    bio = models.TextField(blank=True, verbose_name="о себе")
    stack = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="стек технологий",
    )
    contact = models.CharField(max_length=128, verbose_name="контакт")
    is_published = models.BooleanField(
        default=False,
        verbose_name="опубликован",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="создан",
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name="обновлён")

    class Meta:
        verbose_name = "профиль нетворкинга"
        verbose_name_plural = "профили нетворкинга"

    def __str__(self):
        return f"Networking: {self.user}"


class Donation(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="donations",
        verbose_name="пользователь",
    )
    amount_rub = models.IntegerField(verbose_name="сумма (руб.)")
    yookassa_payment_id = models.CharField(
        max_length=64,
        verbose_name="ID платежа YooKassa",
    )
    status = models.CharField(max_length=20, verbose_name="статус")
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="создано",
    )
    paid_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="оплачено",
    )

    class Meta:
        verbose_name = "пожертвование"
        verbose_name_plural = "пожертвования"

    def __str__(self):
        return f"{self.amount_rub} RUB by {self.user}"
