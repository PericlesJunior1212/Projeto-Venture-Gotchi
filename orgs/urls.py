from django.urls import path
from .views import team_dashboard

urlpatterns = [
    path("team/", team_dashboard, name="team_dashboard"),
]
