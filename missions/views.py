from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from .models import Mission, SubTask
from .forms import MissionForm, SubTaskForm



@login_required
def mission_detail(request, mission_id):
    mission = get_object_or_404(Mission, id=mission_id, user=request.user)
    subtasks = mission.subtasks.all().order_by("id")

    if request.method == "POST":
        subtask_form = SubTaskForm(request.POST)
        if subtask_form.is_valid():
            subtask = subtask_form.save(commit=False)
            subtask.mission = mission
            subtask.save()
            messages.success(request, "Subtarefa adicionada!")
            return redirect("mission_detail", mission_id=mission.id)
    else:
        subtask_form = SubTaskForm()

    return render(
        request,
        "missions/mission_detail.html",
        {"mission": mission, "subtasks": subtasks, "subtask_form": subtask_form},
    )



@login_required
def mission_detail(request, mission_id):
    mission = get_object_or_404(Mission, id=mission_id, user=request.user)
    subtasks = mission.subtasks.all().order_by("id")

    if request.method == "POST":
        subtask_form = SubTaskForm(request.POST)
        if subtask_form.is_valid():
            subtask = subtask_form.save(commit=False)
            subtask.mission = mission
            subtask.save()
            messages.success(request, "Subtarefa adicionada!")
            return redirect("mission_detail", mission_id=mission.id)
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
@transaction.atomic
def complete_subtask(request, subtask_id):
    subtask = get_object_or_404(SubTask, id=subtask_id, mission__user=request.user)

    # Evita xp repetido
    if subtask.completed:
        messages.info(request, "Essa subtarefa já foi concluída.")
        return redirect('mission_detail', subtask.mission.id)

    # Marca subtarefa como feita
    subtask.completed = True
    subtask.completed_at = timezone.now()
    subtask.save()

    # Recompensa XP pela subtarefa
    xp_gained = subtask.xp_reward
    request.user.add_xp(xp_gained)


    messages.success(request, f"Tarefa concluída! Você ganhou {xp_gained} XP!")

    mission = subtask.mission

    # Se a missão chegou a 100%, finaliza
    if mission.progress == 100:
        mission.completed = True
        mission.completed_at = timezone.now()
        mission.save()

        update_xp(request.user, mission.mission_xp)
        messages.success(request, f"Parabéns! Você completou a missão e ganhou +{mission.mission_xp} XP extra!")

    return redirect('mission_detail', mission.id)


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
