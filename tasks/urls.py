from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    # User authentication routes
    path('register/', views.register_user, name='register'),
    path('', views.login_user, name='login'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Task management routes
    path('dashboard/', views.dashboard, name='dashboard'),
    path('task/create/', views.create_task, name='create_task'),
    path('task/update/<int:pk>/', views.update_task, name='update_task'),
    path('task/delete/<int:pk>/', views.delete_task, name='delete_task'),
    path('task/complete/<int:pk>/', views.mark_task_completed, name='mark_task_completed'),
]