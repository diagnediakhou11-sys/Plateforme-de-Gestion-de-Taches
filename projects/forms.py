ffrom django import forms
from .models import Projet, Tache
from django.contrib.auth.models import User

class ProjetForm(forms.ModelForm):
    class Meta:
        model = Projet
        fields = ['nom', 'description', 'membres']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du projet'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Description détaillée...'}),
            'membres': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super(ProjetForm, self).__init__(*args, **kwargs)
        self.fields['membres'].queryset = User.objects.all()
        self.fields['membres'].required = False


class TacheForm(forms.ModelForm):
    class Meta:
        model = Tache
        fields = ['projet', 'titre', 'description', 'assignee', 'statut', 'priorite', 'deadline']
        widgets = {
            'projet': forms.Select(attrs={'class': 'form-select'}),
            'titre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de la tâche'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description...'}),
            'assignee': forms.Select(attrs={'class': 'form-select'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
            'priorite': forms.Select(attrs={'class': 'form-select'}),
            'deadline': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        # On peut recevoir le projet ET l'utilisateur connecté depuis la vue
        projet = kwargs.pop('projet', None)
        user = kwargs.pop('user', None)
        
        super(TacheForm, self).__init__(*args, **kwargs)
        
        # 1. GESTION DU CHAMP PROJET :
        if user:
            # L'utilisateur ne voit que ses projets créés ou rejoints
            self.fields['projet'].queryset = (Projet.objects.filter(createur=user) | Projet.objects.filter(membres=user)).distinct()
        
        if projet:
            # Si la tâche est créée depuis la page d'un projet spécifique, on le pré-sélectionne
            self.fields['projet'].initial = projet

        # 2. GESTION DES MEMBRES ASSIGNABLES :
        if projet:
            createur_id = [projet.createur.id]
            membres_ids = list(projet.membres.values_list('id', flat=True))
            tous_les_membres = createur_id + membres_ids
            self.fields['assignee'].queryset = User.objects.filter(id__in=tous_les_membres)
        elif user:
            # Si pas de projet précis sélectionné au départ, on autorise les utilisateurs globaux
            self.fields['assignee'].queryset = User.objects.all()

        self.fields['assignee'].required = False
        self.fields['projet'].required = True