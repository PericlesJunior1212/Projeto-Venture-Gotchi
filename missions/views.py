from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from .models import Mission, SubTask
from .forms import MissionForm, SubTaskForm
from django.views.decorators.http import require_POST
from django.apps import apps
from accounts.decorators import require_perm
from avatar.models import AvatarItem, UserInventory

def award_random_item(user):
    owned_ids = UserInventory.objects.filter(user=user).values_list("item_id", flat=True)
    item = AvatarItem.objects.exclude(id__in=owned_ids).order_by("?").first()

    if not item:
        return None  # usuário já tem todos os itens

    UserInventory.objects.create(user=user, item=item)
    return item


@login_required
def mission_detail(request, mission_id):
    mission = get_object_or_404(Mission, id=mission_id, user=request.user)
    subtasks = mission.subtasks.all().order_by("id")

    if request.method == "POST":
        subtask_form = SubTaskForm(request.POST)
        if subtask_form.is_valid():
            subtask = subtask_form.save(commit=False)
            subtask.mission = mission

            if subtask.xp_reward is None:
                subtask.xp_reward = 10

            subtask.save()
            messages.success(request, "Subtarefa adicionada!")
            return redirect("mission_detail", mission_id=mission.id)
        else:
            messages.error(request, "Erro ao adicionar subtarefa. Verifique os campos.")
    else:
        subtask_form = SubTaskForm()

    return render(
        request,
        "missions/mission_detail.html",
        {"mission": mission, "subtasks": subtasks, "subtask_form": subtask_form},
    )


@login_required
@require_perm("missions.add_mission")
def mission_create(request):
    if request.method == "POST":
        form = MissionForm(request.POST)
        if form.is_valid():
            mission = form.save(commit=False)
            mission.user = request.user
            mission.save()
            messages.success(request, "Missão criada! Agora adicione subtarefas.")
            return redirect("mission_detail", mission_id=mission.id)
    else:
        form = MissionForm()

    return render(request, "missions/mission_create.html", {"form": form})


@login_required
@require_perm("missions.change_mission")
def mission_edit(request, mission_id):
    mission = get_object_or_404(Mission, id=mission_id, user=request.user)

    if request.method == "POST":
        mission.title = request.POST.get("title")
        mission.description = request.POST.get("description", "")
        mission.save()

        messages.success(request, "Missão atualizada!")
        return redirect("mission_detail", mission.id)

    return render(request, "missions/mission_edit.html", {"mission": mission})


@login_required
def mission_delete(request, mission_id):
    mission = get_object_or_404(Mission, id=mission_id, user=request.user)

    if request.method == "POST":
        mission.delete()
        messages.success(request, "Missão excluída!")
        return redirect("missions_list")

    return render(request, "missions/mission_delete.html", {"mission": mission})


@login_required
@require_perm("missions.add_subtask")
def subtask_create(request, mission_id):
    mission = get_object_or_404(Mission, id=mission_id, user=request.user)

    if request.method == "POST":
        title = request.POST.get("title")
        xp_reward = int(request.POST.get("xp_reward", 10))

        SubTask.objects.create(
            mission=mission,
            title=title,
            xp_reward=xp_reward
        )

        messages.success(request, "Tarefa adicionada à missão!")
        return redirect("mission_detail", mission.id)

    return render(request, "missions/subtask_create.html", {"mission": mission})


@login_required
@require_POST
@transaction.atomic
def complete_subtask(request, subtask_id):
    ActivityEvent = apps.get_model("dashboard", "ActivityEvent")

    subtask = get_object_or_404(SubTask, id=subtask_id, mission__user=request.user)

    if subtask.completed:
        messages.info(request, "Essa subtarefa já foi concluída.")
        return redirect("mission_detail", mission_id=subtask.mission.id)

    user = request.user
    before_level = getattr(user, "level", 1) or 1
    mission = subtask.mission

    # Conclui subtarefa (isso já dá XP + stats no seu model SubTask.complete())
    xp_gained = subtask.complete()

    # Histórico: subtarefa concluída
    ActivityEvent.objects.create(
        user=user,
        event_type="subtask_completed",
        message=f"Concluiu a subtarefa: {subtask.title}",
        xp_delta=xp_gained,
        track=mission.track,
    )

    # Detecta level up
    user.refresh_from_db()
    if getattr(user, "level", 1) > before_level:
        ActivityEvent.objects.create(
            user=user,
            event_type="level_up",
            message=f"Subiu para o nível {user.level}!",
            xp_delta=0,
            track="",
        )

    # Se a missão chegou a 100%, marca como concluída e dá bônus
    mission.refresh_from_db()
    
    all_done = not mission.subtasks.filter(completed=False).exists()

    before_level2 = getattr(user, "level", 1) or 1
    if all_done and not mission.completed:
        mission.completed = True
                # ✅ Recompensa: item colecionável ao concluir a missão
        if hasattr(mission, "completed_at"):
            from django.utils import timezone
            mission.completed_at = timezone.now()
            mission.save(update_fields=["completed", "completed_at"])
        else:
            mission.save(update_fields=["completed"])

        # ✅ Recompensa: item colecionável ao concluir a missão
        if user.groups.filter(name="Usuarios").exists():
            rewarded_item = award_random_item(user)
            if rewarded_item:
                messages.success(request, f"Você ganhou um item: {rewarded_item.name} 🎁")
            else:
                messages.info(request, "Você já possui todos os itens disponíveis 🎉")

        bonus_map = {"daily": 20, "weekly": 50, "monthly": 100}
        mission_bonus = bonus_map.get(mission.mission_type, 20)

        before_level2 = getattr(user, "level", 1) or 1
        if hasattr(user, "add_xp"):
            user.add_xp(mission_bonus)
        else:
            user.xp = (getattr(user, "xp", 0) or 0) + mission_bonus
            user.save(update_fields=["xp"])

        user.refresh_from_db()

        ActivityEvent.objects.create(
            user=user,
            event_type="mission_completed",
            message=f"Concluiu a missão: {mission.title}",
            xp_delta=mission_bonus,
            track=mission.track,
        )

    if getattr(user, "level", 1) > before_level2:
        ActivityEvent.objects.create(
            user=user,
            event_type="level_up",
            message=f"Subiu para o nível {user.level}!",
            xp_delta=0,
            track="",
        )


    # Conquistas: deixa centralizado no arquivo dashboard/achievements.py
    # (evita duplicar regra aqui)
    try:
        from dashboard.achievements import check_and_award
        check_and_award(user)
    except Exception:
        # se ainda não existir ou der algum erro, não quebra a conclusão
        pass

    messages.success(request, f"Subtarefa concluída! Você ganhou {xp_gained} XP ✅")
    return redirect("mission_detail", mission_id=mission.id)


@login_required
def create_mission(request):
    if request.method == "POST":
        form = MissionForm(request.POST)
        if form.is_valid():
            mission = form.save(commit=False)
            mission.user = request.user
            mission.save()
            return redirect("dashboard")
    else:
        form = MissionForm()

    return render(request, "missions/create.html", {"form": form})


@login_required
def missions_list(request):
    missions = Mission.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "missions/missions_list.html", {"missions": missions})
