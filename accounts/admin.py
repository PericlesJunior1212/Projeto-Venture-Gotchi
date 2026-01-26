from django.contrib import admin
from django.contrib.auth.models import Group
from .models import User



@admin.action(description="Aprovar papel solicitado e mover para o grupo")
def approve_role(modeladmin, request, queryset):
    for u in queryset:
        if u.requested_role == 'mentor':
            g = Group.objects.get(name='Mentores')
        elif u.requested_role == 'company':
            g = Group.objects.get(name='Empresas')
        else:
            g = Group.objects.get(name='Usuarios')

        u.groups.clear()
        u.groups.add(g)
        u.role_approved = True
        u.save()

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "requested_role", "role_approved")
    actions = [approve_role]
