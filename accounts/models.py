from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
import os
from django.utils.text import slugify

def avatar_upload_to(instance, filename):
    ext = os.path.splitext(filename)[1]
    filename = f"{uuid.uuid4()}{ext}"
    user_id = instance.id or "temp"
    return f"avatars/user_{user_id}/{filename}"


class User(AbstractUser):
    is_public_profile = models.BooleanField(default=False)
    public_slug = models.SlugField(max_length=60, unique=True, blank=True, null=True)
    REQUEST_ROLE_CHOICES = (
        ('user', 'Usuário'),
        ('mentor', 'Mentor'),
        ('company', 'Empresa'),
    )

    requested_role = models.CharField(
        max_length=20,
        choices=(('user','Usuário'), ('mentor','Mentor'), ('company','Empresa')),
        default='user'
    )
    role_approved = models.BooleanField(default=False)
    
    bio = models.TextField(blank=True, default="")
    interests = models.CharField(max_length=255, blank=True, default="")

   
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)

    xp = models.PositiveIntegerField(default=0)
    level = models.PositiveIntegerField(default=1)

    tech = models.PositiveIntegerField(default=0)
    creativity = models.PositiveIntegerField(default=0)
    discipline = models.PositiveIntegerField(default=0)
    leadership = models.PositiveIntegerField(default=0)

    def xp_for_next_level(self):
        return self.level * 100
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

    def save(self, *args, **kwargs):
        if self.is_public_profile and not self.public_slug:
            base = slugify(self.username)[:50] or "user"
            self.public_slug = f"{base}-{uuid.uuid4().hex[:6]}"
        super().save(*args, **kwargs)