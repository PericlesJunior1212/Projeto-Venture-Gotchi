from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
import os


def avatar_upload_to(instance, filename):
    """
    Salva o avatar em uma pasta por usuário e com nome único.
    Ex: avatars/user_12/uuid.png
    """
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

    def xp_for_next_level(self) -> int:
        """XP necessário para ir do nível atual para o próximo."""
        return 100 * self.level

    def add_xp(self, amount: int):
        """Adiciona XP e sobe de nível automaticamente."""
        if amount <= 0:
            return

        self.xp += amount

        while self.xp >= self.xp_for_next_level():
            self.xp -= self.xp_for_next_level()
            self.level += 1

        self.save(update_fields=["xp", "level"])

    @property
    def xp_percentage(self) -> int:
        """Porcentagem (0 a 100) do progresso no nível atual."""
        needed = self.xp_for_next_level()
        return int((self.xp / needed) * 100) if needed else 0

    def __str__(self):
        return f"{self.username} (Level {self.level})"

tech = models.PositiveIntegerField(default=0)
creativity = models.PositiveIntegerField(default=0)
discipline = models.PositiveIntegerField(default=0)
leadership = models.PositiveIntegerField(default=0)
