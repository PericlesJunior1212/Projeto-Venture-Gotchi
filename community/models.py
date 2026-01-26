from django.conf import settings
from django.db import models

class Room(models.Model):
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=80)
    description = models.CharField(max_length=200, blank=True)
    is_public = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class RoomPost(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="posts")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField(max_length=800)
    created_at = models.DateTimeField(auto_now_add=True)

    # moderação simples
    is_hidden = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} @ {self.room}"

class UserFeedback(models.Model):
    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="feedback_sent"
    )
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="feedback_received"
    )
    rating = models.PositiveSmallIntegerField(default=5)  # 1..5
    message = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    # moderação simples
    is_hidden = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.from_user} -> {self.to_user} ({self.rating})"