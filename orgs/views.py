from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.db.models import Sum, Avg, Count
from .services import get_user_team
from .models import TeamMembership


def is_mentor_or_company(user) -> bool:

    return getattr(user, "role_approved", False) and getattr(user, "requested_role", "user") in ("mentor", "company")


@login_required
def team_dashboard(request):
    if not is_mentor_or_company(request.user):
        return redirect("home")

    team = get_user_team(request.user)
    if not team:
        return render(request, "orgs/team_dashboard.html", {"no_team": True})
    if not request.user.role_approved:
        return redirect("dashboard")

    members = TeamMembership.objects.filter(team=team).select_related("user")

  
    total_xp = members.aggregate(total=Sum("user__xp"))["total"] or 0
    avg_xp = members.aggregate(avg=Avg("user__xp"))["avg"] or 0

    goals = team.goals.all().order_by("-created_at")
    goals_done = goals.filter(is_completed=True).count()
    goals_total = goals.count()

    context = {
        "team": team,
        "members": members,
        "total_xp": total_xp,
        "avg_xp": int(avg_xp),
        "goals": goals,
        "goals_done": goals_done,
        "goals_total": goals_total,
        "no_team": False,
    }
    return render(request, "orgs/team_dashboard.html", context)
