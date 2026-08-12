from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Projet, Tache
from .forms import ProjetForm, TacheForm
from django.contrib import messages


# 1. Dashboard (Tableau de bord)
@login_required(login_url='accounts:login')
def dashboard(request):
    projets = (Projet.objects.filter(createur=request.user) | Projet.objects.filter(membres=request.user)).distinct()
    taches_assignees = Tache.objects.filter(assignee=request.user)
    
    context = {
        'projets': projets,
        'taches_assignees': taches_assignees
    }
    return render(request, 'projects/dashboard.html', context)


# --- CRUD PROJETS ---

# 2. Création de projet
@login_required(login_url='accounts:login')
def project_create(request):
    if request.method == 'POST':
        form = ProjetForm(request.POST)
        if form.is_valid():
            projet = form.save(commit=False)
            projet.createur = request.user
            projet.save()
            form.save_m2m()  # Pour sauvegarder les membres
            messages.success(request, f"Le projet '{projet.nom}' a été créé !")
            return redirect('projects:dashboard')
    else:
        form = ProjetForm()
    
    # CORRECTION : Indentation fixée + 'projet_create.html'
    return render(request, 'projects/projet_create.html', {'form': form})


# 3. Détail d'un projet
@login_required(login_url='accounts:login')
def project_detail(request, project_id):
    projet = get_object_or_404(Projet, id=project_id)
    # Vérification des accès
    if projet.createur != request.user and request.user not in projet.membres.all():
        messages.error(request, "Accès refusé à ce projet.")
        return redirect('projects:dashboard')
        
    taches = projet.taches.all()
    return render(request, 'projects/projet_detail.html', {'projet': projet, 'taches': taches})


# 4. Modification d'un projet
@login_required(login_url='accounts:login')
def project_update(request, project_id):
    projet = get_object_or_404(Projet, id=project_id)
    if projet.createur != request.user:
        messages.error(request, "Seul le créateur peut modifier ce projet.")
        return redirect('projects:dashboard')

    if request.method == 'POST':
        form = ProjetForm(request.POST, instance=projet)
        if form.is_valid():
            form.save()
            messages.success(request, "Le projet a été mis à jour.")
            return redirect('projects:projet_detail', project_id=projet.id)
    else:
        form = ProjetForm(instance=projet)
    
    # CORRECTION ICI : Remplacement de projet_form.html par projet_create.html
    return render(request, 'projects/projet_create.html', {'form': form, 'projet': projet})


# 5. Suppression d'un projet
@login_required(login_url='accounts:login')
def project_delete(request, project_id):
    projet = get_object_or_404(Projet, id=project_id)
    if projet.createur != request.user:
        messages.error(request, "Seul le créateur peut supprimer ce projet.")
        return redirect('projects:dashboard')

    if request.method == 'POST':
        projet.delete()
        messages.success(request, "Le projet a été supprimé.")
        return redirect('projects:dashboard')
    return render(request, 'projects/projet_confirm_delete.html', {'projet': projet})


# --- CRUD TÂCHES ---

# 6. Création de tâche
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
            
            if projet:
                tache.projet = projet
            
            if not tache.projet:
                messages.error(request, "Veuillez sélectionner un projet valide.")
                return render(request, 'projects/tache_create.html', {'form': form, 'projet': projet})

            if tache.projet.createur != request.user and request.user not in tache.projet.membres.all():
                messages.error(request, "Vous n'avez pas la permission d'ajouter une tâche à ce projet.")
                return redirect('projects:dashboard')

            tache.save()
            messages.success(request, f"La tâche '{tache.titre}' a été ajoutée !")
            return redirect('projects:projet_detail', project_id=tache.projet.id)
    else:
        form = TacheForm(projet=projet, user=request.user)

    return render(request, 'projects/tache_create.html', {'form': form, 'projet': projet})


# 7. Détail d'une tâche
@login_required(login_url='accounts:login')
def task_detail(request, task_id):
    tache = get_object_or_404(Tache, id=task_id)
    return render(request, 'projects/tache_detail.html', {'tache': tache})


# 8. Modification d'une tâche
@login_required(login_url='accounts:login')
def task_update(request, task_id):
    tache = get_object_or_404(Tache, id=task_id)
    if request.method == 'POST':
        form = TacheForm(request.POST, instance=tache)
        if form.is_valid():
            form.save()
            messages.success(request, "La tâche a été mise à jour.")
            return redirect('projects:projet_detail', project_id=tache.projet.id)
    else:
        form = TacheForm(instance=tache)
    return render(request, 'projects/tache_create.html', {'form': form, 'tache': tache})


# 9. Suppression d'une tâche
@login_required(login_url='accounts:login')
def task_delete(request, task_id):
    tache = get_object_or_404(Tache, id=task_id)
    project_id = tache.projet.id
    if request.method == 'POST':
        tache.delete()
        messages.success(request, "La tâche a été supprimée.")
        return redirect('projects:projet_detail', project_id=project_id)
    return render(request, 'projects/tache_confirm_delete.html', {'tache': tache})