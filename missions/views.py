from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from .models import Mission, SubTask
from .forms import MissionForm, SubTaskForm
from django.views.decorators.http import require_POST
from django.apps import apps


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
def mission_edit(request, mission_id):
    mission = get_object_or_404(Mission, id=mission_id, user=request.user)

    if request.method == 'POST':
        mission.title = request.POST.get('title')
        mission.description = request.POST.get('description', '')
        mission.save()

        messages.success(request, "Missão atualizada!")
        return redirect('mission_detail', mission.id)

    return render(request, 'missions/mission_edit.html', {
        'mission': mission
    })



@login_required
def mission_delete(request, mission_id):
    mission = get_object_or_404(Mission, id=mission_id, user=request.user)

    if request.method == 'POST':
        mission.delete()
        messages.success(request, "Missão excluída!")
        return redirect('missions_list')

    return render(request, 'missions/mission_delete.html', {
        'mission': mission
    })



@login_required
def subtask_create(request, mission_id):
    mission = get_object_or_404(Mission, id=mission_id, user=request.user)

    if request.method == 'POST':
        title = request.POST.get('title')
        xp_reward = int(request.POST.get('xp_reward', 10))

        SubTask.objects.create(
            mission=mission,
            title=title,
            xp_reward=xp_reward
        )

        messages.success(request, "Tarefa adicionada à missão!")
        return redirect('mission_detail', mission.id)

    return render(request, 'missions/subtask_create.html', {
        'mission': mission
    })


@login_required
@require_POST
@transaction.atomic
def complete_subtask(request, subtask_id):
    Achievement = apps.get_model("dashboard", "Achievement")
    ActivityEvent = apps.get_model("dashboard", "ActivityEvent")

    subtask = get_object_or_404(SubTask, id=subtask_id, mission__user=request.user)

    if subtask.completed:
        messages.info(request, "Essa subtarefa já foi concluída.")
        return redirect("mission_detail", mission_id=subtask.mission.id)

    user = request.user
    before_level = user.level
    mission = subtask.mission

    
    xp_gained = subtask.complete()

 
    ActivityEvent.objects.create(
        user=user,
        event_type="subtask_completed",
        message=f"Concluiu a subtarefa: {subtask.title}",
        xp_delta=xp_gained,
        track=mission.track,
    )


    Achievement.objects.get_or_create(
        user=user,
        code="first_subtask",
        defaults={
            "title": "Primeira Subtarefa!",
            "description": "Você concluiu sua primeira subtarefa.",
        },
    )

 
    user.refresh_from_db(fields=["level", "xp"])
    if user.level > before_level:
        ActivityEvent.objects.create(
            user=user,
            event_type="level_up",
            message=f"Subiu para o nível {user.level}!",
            xp_delta=0,
            track="",
        )

        if user.level >= 5:
            Achievement.objects.get_or_create(
                user=user,
                code="level_5",
                defaults={
                    "title": "Nível 5!",
                    "description": "Você chegou ao nível 5. Continue evoluindo!",
                },
            )

    
    mission.refresh_from_db()
    if mission.progress == 100 and not mission.completed:
        mission.completed = True
        mission.save(update_fields=["completed"])

       
        bonus_map = {"daily": 20, "weekly": 50, "monthly": 100}
        mission_bonus = bonus_map.get(mission.mission_type, 20)

        before_level2 = user.level
        user.add_xp(mission_bonus)
        user.refresh_from_db(fields=["level", "xp"])

        ActivityEvent.objects.create(
            user=user,
            event_type="mission_completed",
            message=f"Concluiu a missão: {mission.title}",
            xp_delta=mission_bonus,
            track=mission.track,
        )

        Achievement.objects.get_or_create(
            user=user,
            code="first_mission",
            defaults={
                "title": "Primeira Missão!",
                "description": "Você concluiu sua primeira missão completa.",
            },
        )

        if user.level > before_level2:
            ActivityEvent.objects.create(
                user=user,
                event_type="level_up",
                message=f"Subiu para o nível {user.level}!",
                xp_delta=0,
                track="",
            )

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
