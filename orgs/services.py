from django.db.models import Sum, Count
from .models import TeamMembership, TeamGoal


def get_user_team(user):
    
    membership = user.team_memberships.select_related("team").first()
    return membership.team if membership else None


def update_team_goals_on_xp(user, xp_gained: int, subtasks_done: int = 0):
 
    team = get_user_team(user)
    if not team:
        return

    goals = team.goals.all()

    for goal in goals:
        if goal.is_completed:
            continue

        if goal.goal_type == "xp_total":
            goal.current_value = min(goal.current_value + max(xp_gained, 0), 10**9)
        elif goal.goal_type == "missions_done":
            goal.current_value = min(goal.current_value + max(subtasks_done, 0), 10**9)

        goal.check_complete()
        goal.save(update_fields=["current_value", "is_completed", "completed_at"])
