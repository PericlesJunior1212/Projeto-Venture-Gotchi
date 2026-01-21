from django.urls import path
from .views import (
    missions_list,
    mission_detail,
    mission_create,
    mission_edit,
    mission_delete,
    subtask_create,
    complete_subtask,
    create_mission
)

urlpatterns = [
    path('', missions_list, name='missions_list'),
    path('<int:mission_id>/', mission_detail, name='mission_detail'),
    path('criar/', mission_create, name='mission_create'),
    path('<int:mission_id>/editar/', mission_edit, name='mission_edit'),
    path('<int:mission_id>/excluir/', mission_delete, name='mission_delete'),
    path('<int:mission_id>/subtask/add/', subtask_create, name='subtask_create'),
    path('subtask/<int:subtask_id>/concluir/', complete_subtask, name='complete_subtask'),
    path("create/", create_mission, name="create_mission"),
]
