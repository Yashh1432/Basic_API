from django.urls import path
from . import views

urlpatterns = [
    path('students/', views.student_list, name='student_list'),
    path('students/<str:id>/', views.read_student, name='read_student'),
    path('students/<str:id>/update/', views.update_student, name='update_student'),
    path('students/<str:id>/delete/', views.delete_student, name='delete_student'),
]