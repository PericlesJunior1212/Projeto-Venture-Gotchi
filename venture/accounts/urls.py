
from django.urls import path
from . import views
from .views import HomeView, ProfileView


urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', HomeView.as_view(), name='home'),
    path('perfil/', ProfileView.as_view(), name='profile')
    
]
