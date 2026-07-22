from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Listes globales
    path('projects/', views.project_list, name='project_list'),
    path('taches/', views.task_list, name='task_list'),
    
    # CRUD Projets
    path('projects/create/', views.project_create, name='projet_create'),
    path('projects/<int:project_id>/', views.project_detail, name='projet_detail'),
    path('projects/<int:project_id>/update/', views.project_update, name='projet_update'),
    path('projects/<int:project_id>/delete/', views.project_delete, name='projet_delete'),
    
    # CRUD Tâches
    path('taches/create/', views.task_create, name='tache_create_direct'),
    
    # 2. Création pré-rattachée à un projet précis
    path('projects/<int:project_id>/taches/create/', views.task_create, name='tache_create'),
    
    # Détails, Modification et Suppression de Tâche
    path('taches/<int:task_id>/', views.task_detail, name='tache_detail'),
    path('taches/<int:task_id>/update/', views.task_update, name='tache_update'),
    path('taches/<int:task_id>/delete/', views.task_delete, name='tache_delete'),
]