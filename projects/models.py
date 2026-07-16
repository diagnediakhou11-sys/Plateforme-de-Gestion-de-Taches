from django.db import models
from django.contrib.auth.models import User
# Create your models here.

# Modèle Projet
class Projet(models.Model):
    nom = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    createur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projets_crees')
    membres = models.ManyToManyField(User, related_name='projets_rejoints', blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nom


# Modèle Tache
class Tache(models.Model):
    STATUT_CHOICES = [
        ('todo', 'À faire'),
        ('en_cours', 'En cours'),
        ('termine', 'Terminé'),
    ]
    PRIORITE_CHOICES = [
        ('basse', 'Basse'),
        ('moyenne', 'Moyenne'),
        ('haute', 'Haute'),
    ]

    titre = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE, related_name='taches')
    assignee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='todo')
    priorite = models.CharField(max_length=20, choices=PRIORITE_CHOICES, default='moyenne')
    deadline = models.DateField(null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titre