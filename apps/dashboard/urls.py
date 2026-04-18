from django.urls import path
from .views import school_admin_dashboard, super_admin_dashboard
from .views import school_admin_dashboard, student_dashboard
from .views import trainee_dashboard, assign_trainer_dashboard

urlpatterns = [
    path('super-admin/', super_admin_dashboard, name='super_admin'),
    path('school-admin/', school_admin_dashboard, name='school_admin_dashboard'),
     path('student-dashboard/', student_dashboard, name='student_dashboard'),
     path('trainee/', trainee_dashboard, name='trainee_dashboard'),
     path('assign-trainer/', assign_trainer_dashboard, name='assign_trainer_dashboard'),
]