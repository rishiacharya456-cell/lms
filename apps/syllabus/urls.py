from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('student/<int:syllabus_id>/', views.student_syllabus, name='student_syllabus'),
    path('unlock/<int:phase_id>/', views.unlock_phase, name='unlock_phase'),
    path('complete/<int:lesson_id>/', views.mark_complete, name='mark_complete'),
    path('manage/', views.manage_syllabus, name='manage_syllabus'),
    path('add-syllabus/', views.add_syllabus, name='add_syllabus'),
    path('add-phase/', views.add_phase, name='add_phase'),
    path('add-topic/', views.add_topic, name='add_topic'),
    path('assign-topics/', views.assign_topics, name='assign_topics'),
    path('manage/', views.manage_syllabus, name='manage_syllabus'),
    path('assign-topics/', views.assign_topics, name='assign_topics'),
    path('delete-phase/<int:phase_id>/', views.delete_phase, name='delete_phase'),
    path('delete-topic/<int:topic_id>/', views.delete_topic, name='delete_topic'),
    path('trainee/syllabus/<int:syllabus_id>/', views.trainee_syllabus, name='trainee_syllabus'),
    path('syllabus/toggle-phase/', views.toggle_phase, name='toggle_phase'),
    path('toggle-topic/', views.toggle_topic, name='toggle_topic'),
    path('school/syllabus/<int:syllabus_id>/', views.school_syllabus, name='school_syllabus'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)