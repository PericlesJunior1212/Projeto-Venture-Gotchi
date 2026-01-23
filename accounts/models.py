from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
import os


def avatar_upload_to(instance, filename):
    ext = os.path.splitext(filename)[1]
    filename = f"{uuid.uuid4()}{ext}"
    user_id = instance.id or "temp"
    return f"avatars/user_{user_id}/{filename}"


class User(AbstractUser):
    xp = models.PositiveIntegerField(default=0)
    level = models.PositiveIntegerField(default=1)

    bio = models.TextField(blank=True, default="")
    interests = models.TextField(blank=True, default="")

    avatar = models.ImageField(upload_to=avatar_upload_to, blank=True, null=True)

    tech = models.PositiveIntegerField(default=0)
    creativity = models.PositiveIntegerField(default=0)
    discipline = models.PositiveIntegerField(default=0)
    leadership = models.PositiveIntegerField(default=0)

    def xp_for_next_level(self) -> int:
        return 100 * self.level

    def add_xp(self, amount: int):
        if amount <= 0:
            return

        self.xp += amount
        while self.xp >= self.xp_for_next_level():
            self.xp -= self.xp_for_next_level()
            self.level += 1

        self.save(update_fields=["xp", "level"])

    @property
    def xp_percentage(self) -> int:
        needed = self.xp_for_next_level()
        return int((self.xp / needed) * 100) if needed else 0

    def __str__(self):
        return f"{self.username} (Level {self.level})"
