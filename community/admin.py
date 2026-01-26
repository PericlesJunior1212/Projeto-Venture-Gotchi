from django.contrib import admin
from .models import Room, RoomPost, UserFeedback

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "is_public")
    list_filter = ("is_public",)
    search_fields = ("title", "slug")
    prepopulated_fields = {"slug": ("title",)}  # preenche slug automaticamente pelo título


@admin.register(RoomPost)
class RoomPostAdmin(admin.ModelAdmin):
    list_display = ("room", "user", "created_at", "is_hidden")
    list_filter = ("room", "is_hidden")
    search_fields = ("content", "user__username", "room__title")
    actions = ["hide_posts", "unhide_posts"]

    @admin.action(description="Ocultar posts selecionados")
    def hide_posts(self, request, queryset):
        queryset.update(is_hidden=True)

    @admin.action(description="Reexibir posts selecionados")
    def unhide_posts(self, request, queryset):
        queryset.update(is_hidden=False)


@admin.register(UserFeedback)
class UserFeedbackAdmin(admin.ModelAdmin):
    list_display = ("from_user", "to_user", "rating", "created_at", "is_hidden")
    list_filter = ("rating", "is_hidden")
    search_fields = ("message", "from_user__username", "to_user__username")
    actions = ["hide_feedbacks", "unhide_feedbacks"]

    @admin.action(description="Ocultar feedbacks selecionados")
    def hide_feedbacks(self, request, queryset):
        queryset.update(is_hidden=True)

    @admin.action(description="Reexibir feedbacks selecionados")
    def unhide_feedbacks(self, request, queryset):
        queryset.update(is_hidden=False)

