from django.contrib import admin
from django.contrib.auth.models import Group
from .models import User



@admin.action(description="Aprovar papel solicitado e mover para o grupo")
def approve_role(modeladmin, request, queryset):
    base_group = Group.objects.get(name="Usuarios")
    for u in queryset:
        if u.requested_role == 'mentor':
            role_group= Group.objects.get(name='Mentores')
        elif u.requested_role == 'company':
           role_group= Group.objects.get(name='Empresas')
        else:
            role_group= Group.objects.get(name='Usuarios')

        u.groups.clear()
        u.groups.add(base_group)
        
        if role_group != base_group:
            u.groups.add(role_group)

        u.role_approved = True
        u.save()

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "requested_role", "role_approved")
    actions = [approve_role]
