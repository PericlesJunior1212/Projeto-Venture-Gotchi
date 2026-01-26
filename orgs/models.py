from django.db import models
from django.conf import settings
from django.utils import timezone

User = settings.AUTH_USER_MODEL


class Company(models.Model):
    name = models.CharField(max_length=120, unique=True)
    owner = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="owned_companies"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Team(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="teams")
    name = models.CharField(max_length=120)

    def __str__(self):
        return f"{self.company.name} - {self.name}"


class TeamMembership(models.Model):
    ROLE_CHOICES = [
        ("member", "Membro"),
        ("mentor", "Mentor"),
        ("manager", "Gestor"),
    ]

    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="team_memberships")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="member")
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("team", "user")

    def __str__(self):
        return f"{self.user} em {self.team} ({self.role})"




class CorporateTrack(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="tracks")
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True, default="")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.company.name} - {self.name}"


class CorporateMission(models.Model):
    track = models.ForeignKey(CorporateTrack, on_delete=models.CASCADE, related_name="missions")
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True, default="")
    xp_reward = models.PositiveIntegerField(default=50)
    deadline = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.title


class TeamTrackAssignment(models.Model):
    """
    Atribui uma trilha corporativa para uma equipe.
    """
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="track_assignments")
    track = models.ForeignKey(CorporateTrack, on_delete=models.CASCADE, related_name="team_assignments")
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("team", "track")



class TeamGoal(models.Model):
    GOAL_TYPE = [
        ("xp_total", "XP Total da Equipe"),
        ("missions_done", "Subtarefas Concluídas (Equipe)"),
    ]

    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="goals")
    title = models.CharField(max_length=120)
    goal_type = models.CharField(max_length=20, choices=GOAL_TYPE, default="xp_total")
    target_value = models.PositiveIntegerField(default=500)
    current_value = models.PositiveIntegerField(default=0)
    deadline = models.DateField(null=True, blank=True)

    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def check_complete(self):
        if not self.is_completed and self.current_value >= self.target_value:
            self.is_completed = True
            self.completed_at = timezone.now()

