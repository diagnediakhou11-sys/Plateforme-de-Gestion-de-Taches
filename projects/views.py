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


# 2. Project Create (projet_create.html)
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


# 3. Project Detail (projet_detail.html)
@login_required(login_url='accounts:login')
def project_detail(request, project_id):
    projet = get_object_or_404(Projet, id=project_id)
    if projet.createur != request.user and request.user not in projet.membres.all():
        messages.error(request, "Accès refusé : Vous ne faites pas partie de ce projet.")
        return redirect('projects:dashboard')
    
    taches = projet.taches.all()
    context = {
        'projet': projet,
        'project': projet,
        'taches': taches
    }
    return render(request, 'projects/projet_detail.html', context)


# 4. Project Update (projet_update.html)
@login_required(login_url='accounts:login')
def project_update(request, project_id):
    projet = get_object_or_404(Projet, id=project_id)
    if projet.createur != request.user:
        messages.error(request, "Seul le créateur peut modifier ce projet.")
        return redirect('projects:project_detail', project_id=projet.id)
        
    if request.method == 'POST':
        form = ProjetForm(request.POST, instance=projet)
        if form.is_valid():
            projet_mis_a_jour = form.save(commit=False)
            projet_mis_a_jour.save()
            form.save_m2m()
            messages.success(request, f"Le projet '{projet.nom}' a été mis à jour !")
            return redirect('projects:project_detail', project_id=projet.id)
    else:
        form = ProjetForm(instance=projet)
    return render(request, 'projects/projet_update.html', {'form': form, 'projet': projet, 'project': projet})


# 5. Project Delete (projet_delete.html)
@login_required(login_url='accounts:login')
def project_delete(request, project_id):
    projet = get_object_or_404(Projet, id=project_id)
    
    if projet.createur != request.user:
        messages.error(request, "Seul le créateur peut supprimer ce projet.")
        return redirect('projects:dashboard')
        
    if request.method == 'POST':
        projet.delete()
        messages.success(request, "Le projet a été supprimé avec succès.")
        return redirect('projects:dashboard')
        
    return render(request, 'projects/projet_delete.html', {
        'projet': projet,
        'project': projet 
    })


# 6. Task Create (tache_create.html) - AVEC SÉLECTION DU PROJET
@login_required(login_url='accounts:login')
def task_create(request, project_id=None):
    projet = None
    if project_id:
        projet = get_object_or_404(Projet, id=project_id)
        if projet.createur != request.user and request.user not in projet.membres.all():
            messages.error(request, "Accès refusé à ce projet.")
            return redirect('projects:dashboard')

    if request.method == 'POST':
        # On passe à la fois 'projet' et 'user' au TacheForm
        form = TacheForm(request.POST, projet=projet, user=request.user)
        if form.is_valid():
            tache = form.save(commit=False)
            # Si le projet n'est pas issu de l'URL, il provient du champ choisi dans le formulaire
            if not tache.projet_id and projet:
                tache.projet = projet
            
            # Vérification de sécurité finale sur le projet rattaché
            if tache.projet.createur != request.user and request.user not in tache.projet.membres.all():
                messages.error(request, "Vous n'avez pas la permission d'ajouter une tâche à ce projet.")
                return redirect('projects:dashboard')

            tache.save()
            messages.success(request, f"La tâche '{tache.titre}' a été ajoutée !")
            return redirect('projects:project_detail', project_id=tache.projet.id)
    else:
        form = TacheForm(projet=projet, user=request.user)

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
        form = TacheForm(request.POST, instance=tache, projet=projet, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "La tâche a été mise à jour avec succès.")
            return redirect('projects:project_detail', project_id=projet.id)
    else:
        form = TacheForm(instance=tache, projet=projet, user=request.user)
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


# 10. Project List
@login_required(login_url='accounts:login')
def project_list(request):
    projets = (Projet.objects.filter(createur=request.user) | Projet.objects.filter(membres=request.user)).distinct()
    return render(request, 'projects/project_list.html', {'projets': projets})


# 11. Task List
@login_required(login_url='accounts:login')
def task_list(request):
    taches = Tache.objects.filter(projet__createur=request.user) | Tache.objects.filter(projet__membres=request.user)
    return render(request, 'projects/task_list.html', {'taches': taches.distinct()})