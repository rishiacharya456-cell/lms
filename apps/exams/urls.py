from django.urls import path
from . import views

urlpatterns = [
    path('my-exams/', views.student_exams, name='student_exams'),
]