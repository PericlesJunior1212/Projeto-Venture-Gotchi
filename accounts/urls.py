from django.urls import path
from . import views
from django.contrib.auth.views import LoginView
from .views import HomeView,ProfileView


urlpatterns = [
    path("login/", LoginView.as_view(template_name="accounts/login.html"), name="login"),
    path('', HomeView.as_view(), name='home'),
    path("profile/", ProfileView.as_view(), name="profile"),
]
