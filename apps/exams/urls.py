from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.exam_registration, name='exam_registration'),
    path('admin/', views.admin_exam_dashboard, name='admin_exam_dashboard'),

    # 🔥 ACTIONS
    path('approve/<int:id>/', views.approve_payment, name='approve_payment'),
    path('reject/<int:id>/', views.reject_payment, name='reject_payment'),
    path('set-date/<int:id>/', views.set_exam_date, name='set_exam_date'),
    path('school/', views.school_exam_dashboard, name='school_exam_dashboard'),
    path('hall-ticket/<int:student_id>/', views.student_hall_ticket, name='student_hall_ticket'),
    path('print-all/<str:class_name>/', views.print_all_hall_tickets, name='print_all_hall_tickets'),


]