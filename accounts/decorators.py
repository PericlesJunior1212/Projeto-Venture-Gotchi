from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect


def require_perm(perm_codename: str, redirect_name: str = "pending"):
    """
    Bloqueia a view se o usuário não tiver a permissão.
    - perm_codename exemplo: 'missions.add_mission'
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            user = request.user

            if not user.is_authenticated:
                return redirect("login")  # ajuste se seu login tiver outro name

            # superuser passa sempre
            if user.is_superuser:
                return view_func(request, *args, **kwargs)

            if user.has_perm(perm_codename):
                return view_func(request, *args, **kwargs)

            messages.warning(request, "Você não tem permissão para acessar essa área.")
            return redirect(redirect_name)
        return _wrapped
    return decorator


def approval_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")

        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)

        if not getattr(request.user, "role_approved", False):
            messages.info(request, "Sua solicitação ainda está aguardando aprovação.")
            return redirect("pending")

        return view_func(request, *args, **kwargs)
    return _wrapped