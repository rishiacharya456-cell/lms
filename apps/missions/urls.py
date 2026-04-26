from django.urls import path
from . import views


urlpatterns = [
    path("play/<int:mission_id>/", views.play_mission, name="play_mission"),
    path("create/", views.create_mission, name="create_mission"),
    path("trainee/", views.trainee_missions, name="trainee_missions"),
    path("toggle-unlock/", views.toggle_mission_unlock, name="toggle_mission_unlock"),
    path("school/", views.school_missions, name="school_missions"),
]