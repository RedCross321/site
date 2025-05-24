from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('profile/', views.profile, name='profile'),
    path('create_poll/', views.create_poll, name='create_poll'),
    path('poll/<int:poll_id>/add_questions/', views.add_questions, name='add_questions'),
    path('poll/<int:poll_id>/edit/', views.edit_poll, name='edit_poll'),
    path('poll/<int:poll_id>/edit_questions/', views.edit_questions, name='edit_questions'),
    path('poll/<int:poll_id>/take/', views.take_poll, name='take_poll'),
    path('poll/<int:poll_id>/results/', views.poll_results, name='poll_results'),
    path('poll/<int:poll_id>/delete/', views.delete_poll, name='delete_poll'),
    path('register/', views.register, name='register'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('create_poll_full/', views.create_poll_full, name='create_poll_full'),
    path('create_poll_full_v2/', views.create_poll_full_v2, name='create_poll_full_v2'),
] 