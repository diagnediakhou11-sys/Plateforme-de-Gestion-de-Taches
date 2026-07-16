from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Projet, Tache
from .forms import ProjetForm, TacheForm
from django.contrib import messages

# 1. Dashboard (Tableau de bord)
@login_required(login_url='accounts:login')
def dashboard(request):
    projets = Projet.objects.filter(createur=request.user) | Projet.objects.filter(membres=request.user)
    projets = projets.distinct()
    taches_assignees = Tache.objects.filter(assignee=request.user)
    
    context = {
        'projets': projets,
        'taches_assignees': taches_assignees
    }
    return render(request, 'projects/dashboard.html', context)

# 2. Project Create (project_create.html)
@login_required(login_url='accounts:login')
def project_create(request):
    if request.method == 'POST':
        form = ProjetForm(request.POST)
        if form.is_valid():
            projet = form.save(commit=False)
            projet.createur = request.user
            projet.save()
            form.save_m2m()
            messages.success(request, f"Le projet '{projet.nom}' a été créé avec succès !")
            return redirect('projects:dashboard')
    else:
        form = ProjetForm()
    return render(request, 'projects/projet_create.html', {'form': form})

# 3. Project Detail (project_detail.html)
@login_required(login_url='accounts:login')
def project_detail(request, project_id):
    projet = get_object_or_404(Projet, id=project_id)
    if projet.createur != request.user and request.user not in projet.membres.all():
        messages.error(request, "Accès refusé : Vous ne faites pas partie de ce projet.")
        return redirect('projects:dashboard')
    
    taches = projet.taches.all()
    context = {
        'projet': projet,
        'taches': taches
    }
    return render(request, 'projects/projet_detail.html', context)

# 4. Project Update (project_update.html)
@login_required(login_url='accounts:login')
def project_update(request, project_id):
    projet = get_object_or_404(Projet, id=project_id)
    if projet.createur != request.user:
        messages.error(request, "Seul le créateur peut modifier ce projet.")
        return redirect('projects:project_detail', project_id=projet.id)
        
    if request.method == 'POST':
        form = ProjetForm(request.POST, instance=projet)
        if form.is_valid():
            form.save()
            messages.success(request, f"Le projet '{projet.nom}' a été mis à jour !")
            return redirect('projects:project_detail', project_id=projet.id)
    else:
        form = ProjetForm(instance=projet)
    return render(request, 'projects/projet_update.html', {'form': form, 'projet': projet})

# 5. Project Delete (projet_delete.html)
@login_required(login_url='accounts:login')
def project_delete(request, project_id):
    # On récupère le projet
    projet = get_object_or_404(Projet, id=project_id)
    
    # Vérification de sécurité
    if projet.createur != request.user:
        messages.error(request, "Seul le créateur peut supprimer ce projet.")
        return redirect('projects:dashboard')
        
    if request.method == 'POST':
        projet.delete()
        messages.success(request, "Le projet a été supprimé avec succès.")
        return redirect('projects:dashboard')
        
    # On envoie à la fois 'projet' et 'project' pour éviter les erreurs dans le template !
    return render(request, 'projects/projet_delete.html', {
        'projet': projet,
        'project': projet 
    })


# 6. Task Create (tache_create.html)
@login_required(login_url='accounts:login')
def task_create(request, project_id):
    projet = get_object_or_404(Projet, id=project_id)
    if projet.createur != request.user and request.user not in projet.membres.all():
        messages.error(request, "Accès refusé.")
        return redirect('projects:dashboard')
        
    if request.method == 'POST':
        form = TacheForm(request.POST, projet=projet)
        if form.is_valid():
            tache = form.save(commit=False)
            tache.projet = projet
            tache.save()
            messages.success(request, f"La tâche '{tache.titre}' a été ajoutée !")
            return redirect('projects:projet_detail', project_id=projet.id)
    else:
        form = TacheForm(projet=projet)
    return render(request, 'projects/tache_create.html', {'form': form, 'projet': projet})

# 7. Task Detail (tache_detail.html)
@login_required(login_url='accounts:login')
def task_detail(request, task_id):
    tache = get_object_or_404(Tache, id=task_id)
    projet = tache.projet
    if projet.createur != request.user and request.user not in projet.membres.all():
        messages.error(request, "Accès refusé.")
        return redirect('projects:dashboard')
    return render(request, 'projects/tache_detail.html', {'tache': tache})

# 8. Task Update (tache_update.html)
@login_required(login_url='accounts:login')
def task_update(request, task_id):
    tache = get_object_or_404(Tache, id=task_id)
    projet = tache.projet
    if projet.createur != request.user and request.user not in projet.membres.all():
        messages.error(request, "Accès refusé.")
        return redirect('projects:dashboard')
        
    if request.method == 'POST':
        form = TacheForm(request.POST, instance=tache, projet=projet)
        if form.is_valid():
            form.save()
            messages.success(request, "La tâche a été mise à jour avec succès.")
            return redirect('projects:project_detail', project_id=projet.id)
    else:
        form = TacheForm(instance=tache, projet=projet)
    return render(request, 'projects/tache_update.html', {'form': form, 'tache': tache})

# 9. Task Delete (tache_delete.html)
@login_required(login_url='accounts:login')
def task_delete(request, task_id):
    tache = get_object_or_404(Tache, id=task_id)
    projet = tache.projet
    if projet.createur != request.user and request.user not in projet.membres.all():
        messages.error(request, "Accès refusé.")
        return redirect('projects:dashboard')
        
    if request.method == 'POST':
        tache.delete()
        messages.success(request, "La tâche a été supprimée avec succès.")
        return redirect('projects:project_detail', project_id=projet.id)
    return render(request, 'projects/tache_delete.html', {'tache': tache})

def project_list(request):
    """
    Affiche la liste de tous les projets de l'utilisateur.
    """
    # On récupère uniquement les projets de l'utilisateur connecté
    projets = Projet.objects.filter(createur=request.user) 
    return render(request, 'projects/project_list.html', {'projets': projets})


def task_list(request):
    """
    Affiche la liste de toutes les tâches de l'utilisateur, tous projets confondus.
    """
    # On récupère les tâches liées aux projets de l'utilisateur connecté
    taches = Tache.objects.filter(projet__createur=request.user)
    return render(request, 'projects/task_list.html', {'taches': taches})