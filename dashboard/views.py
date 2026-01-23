from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from missions.models import Mission, SubTask

@login_required
def dashboard_home(request):
    user = request.user
    
    active_missions = Mission.objects.filter(user=user, completed=False).order_by("deadline", "-created_at")[:5]
    done_subtasks = SubTask.objects.filter(mission__user=user, completed=True).select_related("mission").order_by("-id")[:8]

    suggestions = []
    if not active_missions.exists():
        suggestions.append("Crie uma missão diária pequena para ganhar XP rápido.")
    
    missions = (
        Mission.objects
        .filter(user=user, completed=False)
        .prefetch_related("subtasks")
        .order_by("-created_at")
    )

    context = {
        "missions": missions,
        "xp": user.xp,
        "level": user.level,
        "xp_percentage": user.xp_percentage,  # usa seu @property do User
        "xp_next": user.xp_for_next_level(),  # usa seu método do User
        "user": user,
        "xp_percent": getattr(user, "xp_percentage", 0),
        "active_missions": active_missions,
        "done_subtasks": done_subtasks,
        "suggestions": suggestions,
    }
    return render(request, "dashboard/home.html", context)
