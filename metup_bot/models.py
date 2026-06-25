from django.contrib.auth.models import User
from django.db import models


class TelegramProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="telegram_profile",
    )
    telegram_id = models.BigIntegerField(unique=True)
    telegram_username = models.CharField(max_length=64, blank=True)

    def __str__(self):
        return f"@{self.telegram_username or self.telegram_id}"


class UserRole(models.Model):
    class Role(models.TextChoices):
        GUEST = "guest", "Guest"
        SPEAKER = "speaker", "Speaker"
        ORGANIZER = "organizer", "Organizer"

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="roles",
    )
    role = models.CharField(max_length=20, choices=Role.choices)
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "role"],
                name="unique_user_role",
            ),
        ]

    def __str__(self):
        return f"{self.user} · {self.role}"


class Event(models.Model):
    title = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    starts_at = models.DateTimeField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Talk(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="talks",
    )
    speaker = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="talks",
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    scheduled_start = models.DateTimeField(null=True, blank=True)
    scheduled_end = models.DateTimeField(null=True, blank=True)
    state = models.CharField(max_length=20)
    order_index = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Question(models.Model):
    talk = models.ForeignKey(
        Talk,
        on_delete=models.CASCADE,
        related_name="questions",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="questions",
    )
    text = models.TextField()
    is_answered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Q for {self.talk}"


class NetworkingProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="networking_profile",
    )
    bio = models.TextField(blank=True)
    stack = models.CharField(max_length=200, blank=True)
    contact = models.CharField(max_length=128)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Networking: {self.user}"


class Donation(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="donations",
    )
    amount_rub = models.IntegerField()
    yookassa_payment_id = models.CharField(max_length=64)
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.amount_rub} RUB by {self.user}"
