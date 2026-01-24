from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from .models import AvatarProfile, AvatarItem, UserInventory


def _get_or_create_profile(user):
    profile, _ = AvatarProfile.objects.get_or_create(user=user)
    return profile


@login_required
def avatar_view(request):
    profile = _get_or_create_profile(request.user)

    # inventário do usuário
    inv_items = (
        UserInventory.objects.filter(user=request.user)
        .select_related("item")
        .order_by("item__slot", "item__price_xp")
    )

    # itens disponíveis (loja)
    shop_items = AvatarItem.objects.all().order_by("slot", "price_xp")

    return render(
        request,
        "avatar/avatar.html",
        {
            "profile": profile,
            "inv_items": inv_items,
            "shop_items": shop_items,
        },
    )


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
