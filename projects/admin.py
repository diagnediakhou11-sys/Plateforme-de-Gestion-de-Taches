from django.contrib import admin
from .models import Projet, Tache

# Register your models here.

@admin.register(Projet)
class ProjetAdmin(admin.ModelAdmin):
    # Colonnes affichées dans la liste des projets
    list_display = ('nom', 'createur', 'date_creation', 'date_modification')
    
    # Barre de recherche (recherche par nom du projet ou nom d'utilisateur du créateur)
    search_fields = ('nom', 'createur__username')
    
    # Filtres latéraux (pratique pour trier rapidement par date ou par créateur)
    list_filter = ('date_creation', 'createur')
    
    # Tri par défaut (du plus récent au plus ancien)
    ordering = ('-date_creation',)

@admin.register(Tache)
class TacheAdmin(admin.ModelAdmin):
    # Colonnes clés pour suivre l'avancement global depuis l'admin
    list_display = ('titre', 'projet', 'assignee', 'statut', 'priorite', 'deadline')
    
    # Permet de modifier le statut et la priorité directement depuis la liste sans ouvrir la tâche
    list_editable = ('statut', 'priorite')
    
    # Barre de recherche sur le titre, la description et le nom du projet
    search_fields = ('titre', 'description', 'projet__nom')
    
    # Filtres très utiles pour un manager (filtrer par statut, priorité ou date limite)
    list_filter = ('statut', 'priorite', 'deadline', 'projet')
    
    # Tri par défaut par priorité et deadline
    ordering = ('priorite', 'deadline')