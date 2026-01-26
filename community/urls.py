from django.urls import path
from . import views

urlpatterns = [
    path("", views.room_list, name="community_room_list"),
    path("sala/<slug:slug>/", views.room_detail, name="community_room_detail"),
    path("sala/<slug:slug>/postar/", views.room_post_create, name="community_room_post"),
    path("feedback/<slug:user_slug>/enviar/", views.send_feedback, name="community_send_feedback"),
]
