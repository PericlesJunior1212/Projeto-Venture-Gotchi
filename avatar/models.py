from django.conf import settings
from django.db import models


class AvatarProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="avatar_profile",
    )

    
    base = models.CharField(max_length=30, default="egg")

    hat = models.ForeignKey("AvatarItem", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    body = models.ForeignKey("AvatarItem", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    accessory = models.ForeignKey("AvatarItem", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"AvatarProfile({self.user.username})"


class AvatarItem(models.Model):
    SLOT_CHOICES = [
        ("hat", "Cabeça"),
        ("body", "Corpo"),
        ("accessory", "Acessório"),
    ]

    RARITY_CHOICES = [
        ("common", "Comum"),
        ("rare", "Raro"),
        ("epic", "Épico"),
        ("legendary", "Lendário"),
    ]
    code = models.CharField(max_length=50, unique=True)  # ex: "cap_red"
    name = models.CharField(max_length=80)
    description = models.TextField(
        blank=True,
        help_text="Descrição do item (história, efeito ou curiosidade)"
    )
    slot = models.CharField(max_length=15, choices=SLOT_CHOICES)
    price_xp = models.PositiveIntegerField(default=50)

    rarity = models.CharField(
        max_length=20,
        choices=RARITY_CHOICES,
        default="common"
    )
   
    image = models.ImageField(
        upload_to="avatar/items/",
        blank=True,
        null=True
    )

    def __str__(self):
        return f"{self.name} ({self.slot})"


class UserInventory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="inventory_items")
    item = models.ForeignKey(AvatarItem, on_delete=models.CASCADE)
    acquired_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "item")

    def __str__(self):
        return f"{self.user.username} -> {self.item.code}"

