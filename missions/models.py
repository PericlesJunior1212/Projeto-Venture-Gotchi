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
        "Mission",
        on_delete=models.CASCADE,
        related_name="subtasks"
    )
    title = models.CharField(max_length=120)
    xp_reward = models.PositiveIntegerField(default=10)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def complete(self):
        """Marca como concluída, dá XP e (se existir) aumenta status do Gotchi baseado na trilha."""
        if self.completed:
            return

        # marca como concluída
        self.completed = True
        self.save(update_fields=["completed"])

        user = self.mission.user

        # --- XP ---
        amount = self.xp_reward or 10

        if hasattr(user, "add_xp") and callable(getattr(user, "add_xp")):
            user.add_xp(amount)
        else:
            # fallback simples
            if hasattr(user, "xp"):
                user.xp = (user.xp or 0) + amount
                user.save(update_fields=["xp"])

        # --- STATS (opcional, só se o User tiver esses campos) ---
        track_to_field = {
            "prog": "tech",
            "ux": "creativity",
            "biz": "leadership",
            "soft": "discipline",
        }
        field = track_to_field.get(getattr(self.mission, "track", None))

        # ganho de status
        base_stat_gain = 2
        type_bonus = {"daily": 0, "weekly": 1, "monthly": 2}.get(getattr(self.mission, "mission_type", "daily"), 0)
        stat_gain = base_stat_gain + type_bonus

        # só aplica se o campo existir no model User
        if field and hasattr(user, field):
            current = getattr(user, field) or 0
            new_value = min(100, current + stat_gain)
            setattr(user, field, new_value)

            # aqui é o ponto que costuma quebrar se o campo não existe
            user.save(update_fields=[field])
            
        Achievement.objects.get_or_create(
            user=user,
            code="first_xp",
            defaults={
                "title": "Primeiro XP!",
                "description": "Você ganhou XP pela primeira vez."
    }
)
    