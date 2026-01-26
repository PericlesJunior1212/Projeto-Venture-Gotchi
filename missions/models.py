from django.db import models
from django.conf import settings




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

    mission_type = models.CharField(max_length=10, choices=MISSION_TYPE, default="daily")
    track = models.CharField(max_length=10, choices=TRACKS, default="prog")
    
    mission_xp = models.PositiveIntegerField(default=50)
    
    completed_at = models.DateTimeField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def progress(self) -> int:
        total = self.subtasks.count()
        if total == 0:
            return 0
        done = self.subtasks.filter(completed=True).count()
        return int((done / total) * 100)

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

    def complete(self) -> int:
       
        if self.completed:
            return 0

        self.completed = True
        self.save(update_fields=["completed"])

        user = self.mission.user
        xp_gained = self.xp_reward or 10

        from dashboard.models import ThemedEvent
        event = ThemedEvent.objects.filter(active=True).first()
        if event and event.xp_multiplier:
                xp_gained = int(xp_gained * event.xp_multiplier)

        # XP
        if hasattr(user, "add_xp") and callable(getattr(user, "add_xp")):
            user.add_xp(xp_gained)
        else:
            user.xp = (user.xp or 0) + xp_gained
            user.save(update_fields=["xp"])

        # Histórico do dashboard (evita import circular)
        from dashboard.models import ActivityEvent
        ActivityEvent.objects.create(
            user=user,
            event_type="subtask_completed",
            message=f"Subtarefa concluída: {self.title}",
            xp_delta=xp_gained,
            track=self.mission.track,
            
        )

        # STATS do avatar por trilha
        track_to_field = {
            "prog": "tech",
            "ux": "creativity",
            "biz": "leadership",
            "soft": "discipline",
        }
        field = track_to_field.get(self.mission.track)
        if field and hasattr(user, field):
            base_stat_gain = 2
            type_bonus = {"daily": 0, "weekly": 1, "monthly": 2}.get(self.mission.mission_type, 0)
            stat_gain = base_stat_gain + type_bonus

            current = getattr(user, field) or 0
            setattr(user, field, min(100, current + stat_gain))
            user.save(update_fields=[field])

        # Conquistas
        from dashboard.achievements import check_and_award
        check_and_award(user)
             
        try:
            from orgs.services import update_team_goals_on_xp
            update_team_goals_on_xp(user, xp_gained=xp_gained, subtasks_done=1)
        except Exception:
            
            pass

       
        return xp_gained