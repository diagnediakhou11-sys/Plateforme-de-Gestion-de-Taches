from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Projet, Tache

class ProjectManagementTests(TestCase):

    def setUp(self):
        # Création de deux utilisateurs de test
        self.user_chef = User.objects.create_user(username='diakhou', password='password123')
        self.user_intrus = User.objects.create_user(username='awa', password='password123')
        
        # Création d'un projet de test possédé par 'diakhou'
        self.projet = Projet.objects.create(
            nom="Gestion de Tâches",
            description="Application web pour planifier et suivre les tâches d'une équipe.",
            createur=self.user_chef
        )

    # 1. Tests sur le modèle Projet (Requis par le rapport)
    def test_creation_projet_en_base_de_donnees(self):
        """Vérifie la création et la sauvegarde d'un projet"""
        projet_test = Projet.objects.get(id=self.projet.id)
        self.assertEqual(projet_test.nom, "Gestion de Tâches")
        self.assertEqual(projet_test.createur.username, "diakhou")

    def test_str_projet(self):
        """Vérifie que la méthode __str__ retourne bien le nom du projet"""
        self.assertEqual(str(self.projet), "Gestion de Tâches")

    # 2. Tests sur le modèle Tâche (Requis par le rapport)
    def test_statut_defaut(self):
        """Vérifie que le statut par défaut d'une tâche est bien 'todo'"""
        tache = Tache.objects.create(
            titre="Faire les tests unitaires",
            projet=self.projet
        )
        self.assertEqual(tache.statut, 'todo')

    def test_relation_projet(self):
        """Vérifie que la tâche est liée au bon projet"""
        tache = Tache.objects.create(
            titre="Faire les tests unitaires",
            projet=self.projet
        )
        self.assertEqual(tache.projet, self.projet)

    # 3. Tests sur l'intégration et la sécurité des vues (Requis par le rapport)
    def test_acces_dashboard_sans_connexion(self):
        """Vérifie la redirection automatique vers le login si non connecté"""
        url = reverse('projects:dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_acces_dashboard_avec_connexion(self):
        """Vérifie l'accès réussi au dashboard quand connecté"""
        self.client.login(username='diakhou', password='password123')
        url = reverse('projects:dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_securite_detail_projet(self):
        """Vérifie que l'accès d'un intrus à un projet est bien bloqué/redirigé"""
        self.client.login(username='awa', password='password123')
        url = reverse('projects:projet_detail', kwargs={'project_id': self.projet.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)