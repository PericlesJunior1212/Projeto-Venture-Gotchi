from django.urls import path
from .views import dashboard_home,mentor_panel, company_panel,leaderboard

urlpatterns = [
    path("", dashboard_home, name="dashboard"),
    path("mentor/", mentor_panel, name="mentor_panel"),
    path("empresa/", company_panel, name="company_panel"),
    path("ranking/", leaderboard, name="leaderboard"),
]


