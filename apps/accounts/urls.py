from django.urls import path
from django.shortcuts import render
from .views import role_login
from .views import student_list, add_student
from .views import edit_student, delete_student 
from .views import add_trainer
from .views import trainer_appointment

urlpatterns = [
    # 🔥 Role selection page
    path('login/', lambda request: render(request, 'accounts/choose_role.html'), name='choose_role'),

    # 🔥 Role-based login pages
    path('login/<str:role>/', role_login, name='role_login'),
    path('students/', student_list, name='student_list'),   # 🔥 ADD THIS
    path('students/add/', add_student, name='add_student'),
    
path('students/edit/<int:id>/', edit_student, name='edit_student'),
path('students/delete/<int:id>/', delete_student, name='delete_student'),
path('super-admin/add-trainer/', add_trainer, name='add_trainer'),
path('trainer/appointment/<int:id>/', trainer_appointment, name='trainer_appointment'),
]