from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView
from .views import HomeView,ProfileView, profile_edit, BootstrapLoginView
from django.contrib.auth import views as auth_views
from .views import BootstrapLoginView
from .views import register_view

urlpatterns = [
    path(
        "password_reset/",
        auth_views.PasswordResetView.as_view(
            template_name="accounts/password_reset.html",
            email_template_name="accounts/password_reset_email.txt",
            subject_template_name="accounts/password_reset_subject.txt",
        ),
        name="password_reset",
    ),

    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="accounts/password_reset_done.html",
        ),
        name="password_reset_done",
    ),

    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="accounts/password_reset_confirm.html",
        ),
        name="password_reset_confirm",
    ),

    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="accounts/password_reset_complete.html",
        ),
        name="password_reset_complete",
    ),
    
    path("login/", LoginView.as_view(template_name="accounts/login.html"), name="login"),
    path('', HomeView.as_view(), name='home'),
    path("logout/", LogoutView.as_view(), name="logout"),

    path("profile/", ProfileView.as_view(), name="profile"),
    path("profile/edit/", profile_edit, name="profile_edit"),
    path("login/", BootstrapLoginView.as_view(), name="login"),
    path("register/", register_view, name="register"),
    path("register/", register_view, name="register"),


    ]
