from django.urls import path
from . import views
from .views import trainee_results
from .views import school_results
from .views import export_school_results_excel
from .views import student_results

urlpatterns = [

    # 🔥 STUDENT RESULT
    path('student/', views.student_result, name='student_result'),

    # 🔥 TRAINEE - UPLOAD MARKS
    path('upload/', views.upload_marks, name='upload_marks'),

    # 🔥 SUPER ADMIN - VIEW RESULTS
    path('admin/', views.admin_results, name='admin_results'),

    # 🔥 SUPER ADMIN - PUBLISH RESULTS
    path('publish/', views.publish_results, name='publish_results'),

    # 🔥 SCHOOL - VIEW RESULTS (LEDGER)
    path('school/', views.school_results, name='school_results'),
    path('admin/school/<int:school_id>/', views.admin_school_results, name='admin_school_results'),

    path('publish/', views.publish_results, name='publish_results'),

    path('school/', views.school_results, name='school_results'),
    path('trainee/results/', trainee_results, name='trainee_results'),
    path('school/results/', school_results, name='school_results'),
    path('school/results/export/', export_school_results_excel, name='export_school_results'),
    # apps/results/urls.py

path('school/results/export/', export_school_results_excel, name='export_school_results'),
path('student/results/', student_results, name='student_results'),
]


