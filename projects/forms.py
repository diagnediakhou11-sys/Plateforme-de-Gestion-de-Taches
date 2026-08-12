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
            'membres': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super(ProjetForm, self).__init__(*args, **kwargs)
        self.fields['membres'].queryset = User.objects.all()
        self.fields['membres'].required = False


class TacheForm(forms.ModelForm):
    class Meta:
        model = Tache
        # CORRECTION : On retire 'projet' des fields car il est géré automatiquement par la vue !
        fields = ['titre', 'description', 'assignee', 'statut', 'priorite', 'deadline']
        widgets = {
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

        # GESTION DES MEMBRES ASSIGNABLES (Créateur + Membres)
        if projet:
            self.fields['assignee'].queryset = (
                User.objects.filter(id=projet.createur.id) | projet.membres.all()
            ).distinct()
        else:
            self.fields['assignee'].queryset = User.objects.all()

        self.fields['assignee'].required = False