from django.contrib import admin
from .models import AvatarProfile, AvatarItem, UserInventory

admin.site.register(AvatarProfile)
admin.site.register(AvatarItem)
admin.site.register(UserInventory)

