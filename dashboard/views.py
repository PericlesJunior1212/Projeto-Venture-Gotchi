from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from missions.models import Mission, SubTask



@login_required
def dashboard_home(request):
    user = request.user

    active_missions = (
        Mission.objects
        .filter(user=user, completed=False)
        .order_by("deadline", "-created_at")[:6]
    )

    done_subtasks = (
        SubTask.objects
        .filter(mission__user=user, completed=True)
        .select_related("mission")
        .order_by("-id")[:8]
    )

   
    suggestions = []
    if not active_missions.exists():
        suggestions.append("Crie uma missão diária pequena para ganhar XP rápido.")
    if user.xp < 20:
        suggestions.append("Complete 2 subtarefas hoje para acelerar sua evolução.")
    suggestions.append("Escolha uma trilha principal (Prog/UX/Biz/Soft) e foque nela por 7 dias.")


    achievements = []


    context = {
        "user": user,
        "xp_percent": getattr(user, "xp_percentage", 0),
        "xp_next": user.xp_for_next_level() if hasattr(user, "xp_for_next_level") else 100,
        "active_missions": active_missions,
        "done_subtasks": done_subtasks,
        "suggestions": suggestions,
        "achievements": achievements,
    }
    return render(request, "dashboard/home.html", context)
