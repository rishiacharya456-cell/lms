from django.urls import path
from . import views

urlpatterns = [
    path("trainee/", views.trainee_assessments, name="trainee_assessments"),
    path("student/", views.student_assessments, name="student_assessments"),

    path("play/<int:assessment_id>/", views.play_assessment, name="play_assessment"),
    path("submit/<int:assessment_id>/", views.submit_assessment, name="submit_assessment"),

    path("tab-switch/<int:attempt_id>/", views.track_tab_switch, name="track_tab_switch"),
    path("add-questions/<int:assessment_id>/", views.add_questions, name="add_questions"),
    path("school/", views.school_assessments, name="school_assessments"),
    path("publish/<int:assessment_id>/", views.publish_assessment, name="publish_assessment"),
    path("delete/<int:assessment_id>/", views.delete_assessment, name="delete_assessment"),
    path("school/", views.school_assessments, name="school_assessments"),


]
