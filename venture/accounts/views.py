from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
import logging

logger = logging.getLogger(__name__)

class HomeView(LoginRequiredMixin, TemplateView):
    """
    Home (Dashboard inicial) do usuário logado.
    Exibe dados de progresso, nível e prepara o terreno
    para XP, missões e gráficos futuramente.
    """

    template_name = 'accounts/home.html'
    login_url = 'login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

       
        xp = getattr(user, 'xp', 0)
        level = getattr(user, 'level', 1)
        
        next_level_xp = level * 100
        progress_percent = min((xp / next_level_xp) * 100, 100)

        context['profile'] = {
            'user': user,
            'xp': xp,
            'level': level,
            'next_level_xp': next_level_xp,
            'progress_percent': int(progress_percent),
        }

        logger.info(f"HOME ACESSADA → usuário: {user.username}")

        return context

class ProfileView(LoginRequiredMixin, TemplateView):
    """
    Página de perfil do usuário.
    Mostra informações pessoais, avatar e progresso.
    """

    template_name = 'accounts/profile.html'
    login_url = 'login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context['profile'] = {
            'username': user.username,
            'full_name': user.get_full_name(),
            'email': user.email,
            'bio': getattr(user, 'bio', ''),
            'interests': getattr(user, 'interests', ''),
            'avatar': user.avatar.url if hasattr(user, 'avatar') and user.avatar else None,
            'xp': getattr(user, 'xp', 0),
            'level': getattr(user, 'level', 1),
        }

        logger.info(f"PERFIL ACESSADO → usuário: {user.username}")

        return context

