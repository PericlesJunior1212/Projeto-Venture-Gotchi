from django.db import models
from django.conf import settings


class ActivityEvent(models.Model):
    """
    Histórico do usuário (feed).
    Serve para:
    - Dashboard: histórico
    - Dashboard: gráficos (XP por dia)
    - Dashboard: sugestões
    """
    EVENT_TYPES = [
        ("subtask_completed", "Subtarefa concluída"),
        ("mission_completed", "Missão concluída"),
        ("level_up", "Subiu de nível"),
        ("achievement", "Conquista desbloqueada"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="activity_events",
    )

    event_type = models.CharField(max_length=30, choices=EVENT_TYPES)
    message = models.CharField(max_length=255)

    xp_delta = models.IntegerField(default=0)
    track = models.CharField(max_length=10, blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.event_type} - {self.created_at}"


class Achievement(models.Model):
    key = models.SlugField(unique=True)  # ex: "first_subtask"
    title = models.CharField(max_length=80)
    description = models.CharField(max_length=160)

    def __str__(self):
        return self.title


class UserAchievement(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "achievement")
        ordering = ["-earned_at"]

    def __str__(self):
        return f"{self.user} - {self.achievement}"
    
class ThemedEvent(models.Model):
    name = models.CharField(max_length=100)
    active = models.BooleanField(default=False)
    xp_multiplier = models.FloatField(default=1.0)

    def __str__(self):
        return self.name
