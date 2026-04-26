from django.urls import path
from . import views
from .views import (
    role_login,
    student_list,
    add_student,
    edit_student,
    delete_student,
    add_trainer,
    trainer_appointment,
)

app_name = 'accounts'  # ✅ enables namespacing (best practice)

urlpatterns = [
    # 🔥 LOGIN (Nexolabs Portal - Role Selection Page)
    path('login/', views.choose_role, name='login'),

    # 🔥 Role-based login pages
    path('login/<str:role>/', role_login, name='role_login'),

    # 🔥 STUDENT MANAGEMENT
    path('students/', student_list, name='student_list'),
    path('students/add/', add_student, name='add_student'),
    path('students/edit/<int:id>/', edit_student, name='edit_student'),
    path('students/delete/<int:id>/', delete_student, name='delete_student'),

    # 🔥 TRAINER
    path('super-admin/add-trainer/', add_trainer, name='add_trainer'),
    path('trainer/appointment/<int:id>/', trainer_appointment, name='trainer_appointment'),

    # 🔥 ACCOUNT HELP
    path('forgot-username/', views.forgot_username, name='forgot_username'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
]