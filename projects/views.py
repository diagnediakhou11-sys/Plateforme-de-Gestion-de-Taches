from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required  # <-- AJOUTEZ CETTE LIGNE !
from .models import Projet, Tache
from .forms import ProjetForm, TacheForm
from django.contrib import messages
@login_required(login_url='accounts:login')
def task_create(request, project_id=None):
    projet = None
    if project_id:
        projet = get_object_or_404(Projet, id=project_id)
        if projet.createur != request.user and request.user not in projet.membres.all():
            messages.error(request, "Accès refusé à ce projet.")
            return redirect('projects:dashboard')

    if request.method == 'POST':
        form = TacheForm(request.POST, projet=projet, user=request.user)
        if form.is_valid():
            tache = form.save(commit=False)
            
            # 1. Si le projet est passé par l'URL, on l'attribue directement
            if projet:
                tache.projet = projet
            
            # 2. Vérification de sécurité : La tâche DOIT avoir un projet
            if not tache.projet:
                messages.error(request, "Veuillez sélectionner un projet valide.")
                return render(request, 'projects/tache_create.html', {'form': form, 'projet': projet})

            # 3. Validation des droits sur le projet
            if tache.projet.createur != request.user and request.user not in tache.projet.membres.all():
                messages.error(request, "Vous n'avez pas la permission d'ajouter une tâche à ce projet.")
                return redirect('projects:dashboard')

            tache.save()
            messages.success(request, f"La tâche '{tache.titre}' a été ajoutée !")
            return redirect('projects:project_detail', project_id=tache.projet.id)
        else:
            print("Erreurs du formulaire :", form.errors) # Débogage en console
    else:
        form = TacheForm(projet=projet, user=request.user)

    return render(request, 'projects/tache_create.html', {'form': form, 'projet': projet})