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
        fields = ['titre', 'description', 'assignee', 'statut', 'priorite', 'deadline']
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de la tâche'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description...'}),
            'assignee': forms.Select(attrs={'class': 'form-control'}),
            'statut': forms.Select(attrs={'class': 'form-control'}),
            'priorite': forms.Select(attrs={'class': 'form-control'}),
            'deadline': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        # On récupère le projet passé depuis la vue pour filtrer la liste des membres
        projet = kwargs.pop('projet', None)
        super(TacheForm, self).__init__(*args, **kwargs)
        if projet:
            # L'assigné doit être soit le créateur du projet, soit un de ses membres invités
            createur_id = [projet.createur.id]
            membres_ids = list(projet.membres.values_list('id', flat=True))
            tous_les_membres = createur_id + membres_ids
            self.fields['assignee'].queryset = User.objects.filter(id__in=tous_les_membres)
        self.fields['assignee'].required = False