from django.urls import path
from .views import attendance_list, student_attendance
from .views import attendance_detail
from .views import unlock_attendance
from .views import edit_attendance, student_attendance, school_attendance, take_attendance, lock_attendance, toggle_trainer_permission, toggle_school_permission
from .views import attendance_management
from .views import admin_school_attendance, export_attendance_excel

urlpatterns = [
    path('super-admin/attendance/', attendance_list, name='attendance_list'),
    path('super-admin/attendance/<int:session_id>/', attendance_detail, name='attendance_detail'),
    path('super-admin/attendance/<int:session_id>/unlock/', unlock_attendance, name='unlock_attendance'),
    path('super-admin/attendance/<int:session_id>/edit/', edit_attendance, name='edit_attendance'),
    path('student/', student_attendance, name='student_attendance'),
    path('school/', school_attendance, name='school_attendance'),
    path('edit/<int:id>/', edit_attendance, name='edit_attendance'),
     path('take/', take_attendance, name='take_attendance'),
     path('unlock/<int:id>/', unlock_attendance, name='unlock_attendance'),
    path('lock/<int:id>/', lock_attendance, name='lock_attendance'),

    path('toggle-trainer/<int:id>/', toggle_trainer_permission, name='toggle_trainer_permission'),
    path('toggle-school/<int:id>/', toggle_school_permission, name='toggle_school_permission'),
    path('management/', attendance_management, name='attendance_management'),
    path('school/<int:id>/', admin_school_attendance, name='admin_school_attendance'),
    path('export/', export_attendance_excel, name='export_attendance_excel'),
    path('student/attendance/', student_attendance, name='student_attendance'),

]