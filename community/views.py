from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from .models import Room, RoomPost, UserFeedback
from django.contrib.auth import get_user_model

User = get_user_model()

@login_required
def room_list(request):
    rooms = Room.objects.filter(is_public=True).order_by("title")
    return render(request, "community/room_list.html", {"rooms": rooms})


@login_required
def room_detail(request, slug):
    room = get_object_or_404(Room, slug=slug, is_public=True)
    posts = (
        room.posts.select_related("user")
        .filter(is_hidden=False)
        .order_by("-created_at")[:50]
    )
    return render(request, "community/room_detail.html", {"room": room, "posts": posts})


@login_required
@require_POST
def room_post_create(request, slug):
    room = get_object_or_404(Room, slug=slug, is_public=True)
    content = (request.POST.get("content") or "").strip()

    if len(content) < 2:
        messages.error(request, "Escreva uma mensagem antes de enviar.")
        return redirect("community_room_detail", slug=slug)

    RoomPost.objects.create(room=room, user=request.user, content=content)
    messages.success(request, "Post enviado ✅")
    return redirect("community_room_detail", slug=slug)


@login_required
@require_POST
def send_feedback(request, user_slug):
    to_user = get_object_or_404(User, public_slug=user_slug, is_public_profile=True)

    # bloqueia feedback para si mesmo
    if to_user.id == request.user.id:
        messages.error(request, "Você não pode enviar feedback para você mesma.")
        return redirect("public_profile", slug=user_slug)

    # só usuários comuns (MVP)
    if not request.user.groups.filter(name="Usuarios").exists():
        messages.error(request, "Apenas Usuários Individuais podem enviar feedback.")
        return redirect("public_profile", slug=user_slug)

    msg = (request.POST.get("message") or "").strip()
    rating = int(request.POST.get("rating") or 5)
    rating = min(5, max(1, rating))

    if len(msg) < 5:
        messages.error(request, "Escreva um feedback com pelo menos 5 caracteres.")
        return redirect("public_profile", slug=user_slug)

    UserFeedback.objects.create(from_user=request.user, to_user=to_user, rating=rating, message=msg)
    messages.success(request, "Feedback enviado ✅")
    return redirect("public_profile", slug=user_slug)