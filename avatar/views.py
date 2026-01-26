from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from missions.models import Mission, SubTask

from .models import AvatarProfile, AvatarItem, UserInventory


def _get_or_create_profile(user):
    profile, _ = AvatarProfile.objects.get_or_create(user=user)
    return profile



@login_required
def avatar_view(request):
    user = request.user

    xp = user.xp
    level = user.level
    xp_next = level * 100

    progress_percent = int((xp / xp_next) * 100) if xp_next else 0
    
    if user.level < 5:
        gotchi_image = "gotchi/gotchi_lvl1.png"
    elif user.level < 10:
        gotchi_image = "gotchi/gotchi_lvl2.png" 
    else:
        gotchi_image = "gotchi/gotchi_lvl3.png"
        
    missions_count = Mission.objects.filter(user=user).count()
    done_subtasks_count = SubTask.objects.filter(mission__user=user,completed=True).count()


    achievements = []

    if done_subtasks_count >= 1:
        achievements.append({"title": "Primeira Subtarefa!", "desc": "Você concluiu sua primeira subtarefa."})

    if missions_count >= 1:
        achievements.append({"title": "Primeira Missão!", "desc": "Você criou sua primeira missão."})

    if user.level > 1:
        achievements.append({"title": "Subiu de Nível!", "desc": f"Você alcançou o nível {user.level}."})

    profile = _get_or_create_profile(user)

    inventory = (
        UserInventory.objects
        .filter(user=user)
        .select_related("item")
        .order_by("item__slot", "item__rarity", "item__name")
    )
    context = {
        
        "user": user,
        "gotchi_image": gotchi_image,
        "achievements": achievements,
        "xp": xp,
        "level": level,
        "xp_next": xp_next,
        "level": level,
        "progress_percent": progress_percent,
        "stats": {
            "tech": user.tech,
            "creativity": user.creativity,
            "discipline": user.discipline,
            "leadership": user.leadership,
        },
        "profile": profile,
        "inventory": inventory,
        
    }

    return render(request, "avatar/meu_gotchi.html", context)


@login_required
@transaction.atomic
def buy_item(request, item_id):
    item = get_object_or_404(AvatarItem, id=item_id)

    # já tem?
    if UserInventory.objects.filter(user=request.user, item=item).exists():
        messages.info(request, "Você já possui esse item.")
        return redirect("avatar")

    # checa xp
    user = request.user
    price = item.price_xp

    if (user.xp or 0) < price:
        messages.error(request, f"XP insuficiente. Precisa de {price} XP.")
        return redirect("avatar")

    # desconta xp
    user.xp = (user.xp or 0) - price
    user.save(update_fields=["xp"])

    UserInventory.objects.create(user=user, item=item)
    messages.success(request, f"Item comprado: {item.name} ✅")
    return redirect("avatar")


@login_required
@transaction.atomic
def equip_item(request, item_id):
    item = get_object_or_404(AvatarItem, id=item_id)

    # só pode equipar se tiver no inventário
    if not UserInventory.objects.filter(user=request.user, item=item).exists():
        messages.error(request, "Você não possui esse item.")
        return redirect("avatar")

    profile = _get_or_create_profile(request.user)

    if item.slot == "hat":
        profile.hat = item
    elif item.slot == "body":
        profile.body = item
    elif item.slot == "accessory":
        profile.accessory = item

    profile.save()
    messages.success(request, f"Equipado: {item.name} 🎉")
    return redirect("avatar")


@login_required
def unequip_slot(request, slot):
    profile = _get_or_create_profile(request.user)

    if slot == "hat":
        profile.hat = None
    elif slot == "body":
        profile.body = None
    elif slot == "accessory":
        profile.accessory = None

    profile.save()
    messages.success(request, "Item removido.")
    return redirect("avatar")

