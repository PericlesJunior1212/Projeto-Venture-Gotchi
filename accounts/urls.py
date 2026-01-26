from django.urls import path
from django.contrib.auth.views import LogoutView
from django.contrib.auth import views as auth_views
from .views import pending_view


from .views import (
    HomeView,
    ProfileView,
    profile_edit,
    login_view,
    register_view,
    public_profile,
    send_feedback,
)

urlpatterns = [
    # Home
    path("", HomeView.as_view(), name="home"),

    # Auth
    path("login/", login_view, name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("register/", register_view, name="register"),

    # Perfil
    path("profile/", profile_edit, name="profile"),


    # Senhas
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
    path("pending/", pending_view, name="pending"),
    
    path("u/<slug:slug>/", public_profile, name="public_profile"),
    path("u/<slug:slug>/feedback/", send_feedback, name="send_feedback"),


]

