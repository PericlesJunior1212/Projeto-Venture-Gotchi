from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from django.utils import timezone
from missions.models import Mission, SubTask, TRACKS
from .models import Achievement, ActivityEvent, UserAchievement



@login_required
def dashboard_home(request):
    user = request.user

    active_missions = (
        Mission.objects
        .filter(user=user, completed=False)
        .order_by("deadline", "-created_at")[:6]
    )

    # histórico real (últimos 12 eventos)
    history = (
        ActivityEvent.objects
        .filter(user=user)
        .order_by("-created_at")[:12]
    )

    achievements = (
    UserAchievement.objects
    .filter(user=user)
    .select_related("achievement")[:6]
)

   

    # gráfico: XP ganho por dia (últimos 7 dias)
    xp_by_day_qs = (
        ActivityEvent.objects
        .filter(user=user, xp_delta__gt=0)
        .annotate(day=TruncDate("created_at"))
        .values("day")
        .annotate(total=Sum("xp_delta"))
        .order_by("-day")[:7]
    )
    xp_by_day_qs = list(reversed(list(xp_by_day_qs)))
    xp_days = [str(item["day"]) for item in xp_by_day_qs]
    xp_totals = [int(item["total"] or 0) for item in xp_by_day_qs]

    # cards por trilha (total de missões)
    by_track = (
        Mission.objects
        .filter(user=user)
        .values("track")
        .annotate(total=Count("id"))
    )
    by_track_map = {item["track"]: item["total"] for item in by_track}
    track_cards = [{"key": k, "label": label, "total": by_track_map.get(k, 0)} for k, label in TRACKS]

    # sugestões automáticas
    suggestions = []
    if not active_missions.exists():
        suggestions.append("Crie uma missão diária pequena para ganhar XP rápido.")

    # trilha com menos missões
    least_track = min(track_cards, key=lambda x: x["total"]) if track_cards else None
    if least_track and least_track["total"] == 0:
        suggestions.append(f"Você ainda não fez missões em {least_track['label']}. Crie uma missão nessa trilha!")

    # incentivo de weekly se ainda não existe
    if not Mission.objects.filter(user=user, mission_type="weekly").exists():
        suggestions.append("Crie uma missão semanal (meta grande) para evoluir mais rápido.")

    # fallback
    if not suggestions:
        suggestions.append("Você está indo bem! Complete 1 missão hoje para manter o ritmo.")

    context = {
        "user": user,
        "xp_percent": getattr(user, "xp_percentage", 0),
        "xp_next": user.xp_for_next_level() if hasattr(user, "xp_for_next_level") else 100,
        "active_missions": active_missions,
        "history": history,
        "achievements": achievements,
        "suggestions": suggestions,
        "track_cards": track_cards,
        "xp_days": xp_days,
        "xp_totals": xp_totals,
    }
    return render(request, "dashboard/home.html", context)
