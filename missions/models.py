from django.db import models
from django.conf import settings
from dashboard.models import Achievement


MISSION_TYPE = [
    ("daily", "Diária"),
    ("weekly", "Semanal"),
    ("monthly", "Mensal"),
]

TRACKS = [
    ("prog", "Programação"),
    ("ux", "UX/UI"),
    ("biz", "Empreendedorismo"),
    ("soft", "Soft Skills"),
]



class Mission(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="missions"
    )

    title = models.CharField(max_length=120)
    description = models.TextField(blank=True, default="")
    deadline = models.DateField(null=True, blank=True)

    mission_type = models.CharField(
        max_length=10,
        choices=MISSION_TYPE,
        default="daily"
    )

    track = models.CharField(
        max_length=10,
        choices=TRACKS,
        default="prog"
    )

    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class SubTask(models.Model):
    mission = models.ForeignKey(
        Mission,
        on_delete=models.CASCADE,
        related_name="subtasks"
    )

    title = models.CharField(max_length=120)
    xp_reward = models.PositiveIntegerField(default=10)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return self.title


    def complete(self):
        """Marca como concluída e dá XP ao usuário."""
        if self.completed:
            return
        self.completed = True
        self.save(update_fields=["completed"])

        user = self.mission.user
        
        if hasattr(user, "add_xp"):
            user.add_xp(self.xp_reward)
        else:
            
            user.xp += self.xp_reward
            user.save(update_fields=["xp"])
        
        Achievement.objects.get_or_create(
            user=user,
            code="first_xp",
            defaults={
                "title": "Primeiro XP!",
                "description": "Você ganhou XP pela primeira vez."
    }
)
    