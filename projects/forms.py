from django import forms
from .models import Projet, Tache
from django.contrib.auth.models import User

class ProjetForm(forms.ModelForm):
    class Meta:
        model = Projet
        fields = ['nom', 'description', 'membres']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du projet'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Description détaillée...'}),
            # On utilise SelectMultiple avec la classe Bootstrap form-select pour une sélection claire
            'membres': forms.SelectMultiple(attrs={'class': 'form-select', 'size': '6'}),
        }

    def __init__(self, *args, **kwargs):
        # Récupération optionnelle de l'utilisateur connecté depuis la vue
        user = kwargs.pop('user', None)
        super(ProjetForm, self).__init__(*args, **kwargs)
        
        # Si un utilisateur est transmis, on l'exclut de la liste des membres à cocher
        # (car il est DÉJÀ le créateur du projet)
        if user:
            self.fields['membres'].queryset = User.objects.exclude(id=user.id)
        else:
            self.fields['membres'].queryset = User.objects.all()
            
        self.fields['membres'].required = False
        self.fields['membres'].help_text = "Maintenez 'Ctrl' (ou 'Cmd' sur Mac) pour sélectionner plusieurs membres."


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
        projet = kwargs.pop('projet', None)
        user = kwargs.pop('user', None)
        
        super(TacheForm, self).__init__(*args, **kwargs)

        # 1. GESTION DU CHAMP PROJET
        if user:
            self.fields['projet'].queryset = (
                Projet.objects.filter(createur=user) | Projet.objects.filter(membres=user)
            ).distinct()
        else:
            self.fields['projet'].queryset = Projet.objects.all()

        if projet:
            self.fields['projet'].initial = projet
            self.fields['projet'].widget = forms.HiddenInput()

        # 2. GESTION DES MEMBRES ASSIGNABLES
        if projet:
            self.fields['assignee'].queryset = (
                User.objects.filter(id=projet.createur.id) | projet.membres.all()
            ).distinct()
        else:
            self.fields['assignee'].queryset = User.objects.all()

        self.fields['assignee'].required = False