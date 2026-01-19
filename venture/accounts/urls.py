from django.urls import path
from .views import login_view, logout_view, HomeView, ProfileView

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('', HomeView.as_view(), name='home'),
    path('perfil/', ProfileView.as_view(), name='profile'),
]
