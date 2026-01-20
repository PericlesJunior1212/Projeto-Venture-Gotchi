from django.urls import path
from . import views
from .views import HomeView,ProfileView


urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('', HomeView.as_view(), name='home'),
    path("profile/", ProfileView.as_view(), name="profile"),
]
