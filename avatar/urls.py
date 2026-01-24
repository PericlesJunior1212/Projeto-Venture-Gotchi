from django.urls import path
from . import views

urlpatterns = [
    path("", views.avatar_view, name="avatar"),
    path("buy/<int:item_id>/", views.buy_item, name="avatar_buy"),
    path("equip/<int:item_id>/", views.equip_item, name="avatar_equip"),
    path("unequip/<str:slot>/", views.unequip_slot, name="avatar_unequip"),
]
