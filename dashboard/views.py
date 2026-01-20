from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from missions.models import Mission
from accounts.models import User

@login_required
def dashboard_home(request):
    user = request.user

    missions = Mission.objects.filter(user=user, completed=False)

    context = {
        "user": user,
        "missions": missions,
        "xp": user.xp,
        "level": user.level,
    }

    return render(request, "dashboard/home.html", context)
