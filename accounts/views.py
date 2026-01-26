import logging
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect,get_object_or_404
from django.views.generic import TemplateView
from .forms import RegisterForm, ProfileUpdateForm, LoginForm
from community.models import UserFeedback
from django.views.decorators.http import require_POST


logger = logging.getLogger(__name__)
User = get_user_model()


def login_view(request):
    """
    Tela de login customizada.
    """
    form = LoginForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        messages.success(request, "Login realizado com sucesso!")
        return redirect("home")

    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    logout(request)
    messages.info(request, "Você saiu da sua conta.")
    return redirect('login')



class HomeView(LoginRequiredMixin, TemplateView):
    """
    Home (Dashboard inicial) do usuário logado.
    Exibe dados de progresso, nível e prepara o terreno
    para XP, missões e gráficos futuramente.
    """

    template_name = 'dashboard/home.html'
    login_url = 'login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
     
    
        xp = getattr(user, 'xp', 0)
        level = getattr(user, 'level', 1)
        
        next_level_xp = level * 100

        if next_level_xp == 0:
            progress_percent = 0
        else:
            progress_percent = int((xp / next_level_xp) * 100)

        
        context["profile"] = {
            "user": user,
            "xp": xp,
            "level": level,
            "next_level_xp": next_level_xp,
            "progress_percent": progress_percent,
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
        
        xp = getattr(user, "xp", 0)
        level = getattr(user, "level", 1)
        next_level_xp = max(level, 1) * 100
        progress_percent = int((xp / next_level_xp) * 100) if next_level_xp else 0

        context["profile"] = {
            "username": user.username,
            "full_name": user.get_full_name(),
            "email": user.email,
            "bio": getattr(user, "bio", ""),
            "interests": getattr(user, "interests", ""),
            "avatar": user.avatar.url if hasattr(user, "avatar") and user.avatar else None,
            "xp": getattr(user, "xp", 0),
            "level": getattr(user, "level", 1),
            "next_level_xp": getattr(user, "level", 1) * 100,
            "progress_percent": int((getattr(user, "xp", 0) / (getattr(user, "level", 1) * 100)) * 100),
        }

        logger.info(f"PERFIL ACESSADO → usuário: {user.username}")

        return context

@login_required
def profile_edit(request):

    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil atualizado com sucesso!")
            return redirect("profile")
    else:
        form = ProfileUpdateForm(instance=request.user)

    return render(request, "accounts/profile.html", {"form": form})




def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Conta criada com sucesso!")
            if user.requested_role in ("mentor", "company"):
                messages.info(request, "Cadastro feito! Sua solicitação será analisada por um administrador.")
                return redirect("pending")

            return redirect("dashboard")
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})

@login_required
def pending_view(request):
    return render(request, "accounts/pending.html")

@login_required
def public_profile(request, slug):
    u = get_object_or_404(User, public_slug=slug, is_public_profile=True)

    feedbacks = (
        UserFeedback.objects
        .filter(to_user=u, is_hidden=False)
        .select_related("from_user")
        .order_by("-created_at")[:20]
    )

    can_send_feedback = (
        request.user.is_authenticated
        and request.user.id != u.id
        and request.user.groups.filter(name="Usuarios").exists()
    )

    return render(
        request,
        "accounts/public_profile.html",
        {
            "profile_user": u,
            "feedbacks": feedbacks,
            "can_send_feedback": can_send_feedback,
        },
    )
    
@login_required
@require_POST
def send_feedback(request, slug):
    to_user = get_object_or_404(User, public_slug=slug, is_public_profile=True)

    if to_user.id == request.user.id:
        messages.error(request, "Você não pode enviar feedback para você mesma.")
        return redirect("public_profile", slug=slug)

    # MVP: só Usuários Individuais enviam feedback
    if not request.user.groups.filter(name="Usuarios").exists():
        messages.error(request, "Apenas Usuários Individuais podem enviar feedback.")
        return redirect("public_profile", slug=slug)

    msg = (request.POST.get("message") or "").strip()
    rating_raw = request.POST.get("rating") or "5"

    try:
        rating = int(rating_raw)
    except ValueError:
        rating = 5

    rating = max(1, min(5, rating))

    if len(msg) < 5:
        messages.error(request, "Escreva um feedback com pelo menos 5 caracteres.")
        return redirect("public_profile", slug=slug)

    UserFeedback.objects.create(
        from_user=request.user,
        to_user=to_user,
        rating=rating,
        message=msg,
    )

    messages.success(request, "Feedback enviado ✅")
    return redirect("public_profile", slug=slug)
    