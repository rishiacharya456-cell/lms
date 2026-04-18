# apps/schools/urls.py

from django.urls import path
from . import views




urlpatterns = [
    path('register/', views.register_school, name='register_school'),
    path('approve/<int:pk>/', views.approve_school, name='approve_school'),
    path('reject/<int:pk>/', views.reject_school, name='reject_school'),
    path('add/', views.add_school, name='add_school'),
    path('edit/<int:pk>/', views.edit_school, name='edit_school'),
    path('delete/<int:pk>/', views.delete_school, name='delete_school'),
    path('export/csv/', views.export_schools_csv, name='export_schools_csv'),
    path('export/excel/', views.export_schools_excel, name='export_schools_excel'),
    path('detail/<int:id>/', views.school_detail, name='school_detail'),
]