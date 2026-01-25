from django.db import transaction
from .models import Achievement, UserAchievement
from missions.models import SubTask, Mission

ACHIEVEMENTS = [
    {
        "key": "first_subtask",
        "title": "Primeira Subtarefa!",
        "description": "Você concluiu sua primeira subtarefa.",
    },
    {
        "key": "first_mission",
        "title": "Primeira Missão!",
        "description": "Você criou sua primeira missão.",
    },
    {
        "key": "xp_100",
        "title": "100 XP!",
        "description": "Você alcançou 100 XP no total.",
    },
    {
        "key": "level_5",
        "title": "Nível 5!",
        "description": "Seu Gotchi chegou ao nível 5.",
    },
]


def _get_or_create_achievement(key: str, title: str, description: str) -> Achievement:
    obj, _ = Achievement.objects.get_or_create(
        key=key,
        defaults={"title": title, "description": description},
    )
    return obj


@transaction.atomic
def check_and_award(user):
    """
    Checa condições e libera conquistas (idempotente: não duplica).
    Chame isso sempre que ganhar XP, concluir subtarefa, criar missão etc.
    """

    # garante que as conquistas existem no banco
    for a in ACHIEVEMENTS:
        _get_or_create_achievement(a["key"], a["title"], a["description"])

    # chaves já conquistadas pelo usuário
    earned_keys = set(
        UserAchievement.objects.filter(user=user)
        .values_list("achievement__key", flat=True)
    )

    def award(key: str):
        if key in earned_keys:
            return
        ach = Achievement.objects.get(key=key)
        UserAchievement.objects.create(user=user, achievement=ach)
        earned_keys.add(key)

    # ✅ valores sempre definidos antes de usar
    xp = getattr(user, "xp", 0) or 0
    level = getattr(user, "level", 1) or 1

    # ✅ regras
    if SubTask.objects.filter(mission__user=user, completed=True).exists():
        award("first_subtask")

    if Mission.objects.filter(user=user).exists():
        award("first_mission")

    if xp >= 100:
        award("xp_100")

    if level >= 5:
        award("level_5")
