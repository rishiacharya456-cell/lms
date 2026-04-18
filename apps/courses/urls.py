from django.urls import path
from . import views

urlpatterns = [
    path('', views.course_list, name='course_list'),  # ✅ PUT THIS FIRST

    path('create/', views.create_course, name='create_course'),
    path('assign/<int:course_id>/', views.assign_course, name='assign_course'),

    path('school/', views.school_courses, name='school_courses'),
    path('toggle/<int:assignment_id>/', views.toggle_course, name='toggle_course'),

    path('student/', views.student_courses, name='student_courses'),
    path('register/<int:course_id>/', views.register_course, name='register_course'),

    path('approve/', views.approve_registrations, name='approve_registrations'),
    path('approve/<int:reg_id>/', views.approve_student, name='approve_student'),
    path('delete/<int:id>/', views.delete_course, name='delete_course'),
    path('register/<int:course_id>/', views.register_course, name='register_course'),
    path('reject/<int:reg_id>/', views.reject_student, name='reject_student'),
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    # apps/courses/urls.py

    path('trainee/marks/', views.trainee_internal_marks, name='trainee_marks'),
    path('trainee/marks/save/<int:reg_id>/', views.save_internal_marks, name='save_internal_marks'),
    path('internal-marks/', views.school_internal_marks, name='school_internal_marks'),
    path('admin/update-marks/<int:reg_id>/', views.admin_update_marks, name='admin_update_marks'),
]