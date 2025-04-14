from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.shortcuts import render, get_object_or_404, redirect
from .models import Review, Ticket, UserFollows
from django.contrib.auth.models import User
from .forms import CustomUserCreationForm
from django.contrib.auth.hashers import make_password 
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.http import HttpResponseForbidden
from django.core.paginator import Paginator
from .models import BlockRelation


def hello(request):
  
    tickets = Ticket.objects.all()
    return render(request, 'myapp/hello.html',{'tickets':tickets})

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib import messages


def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        # Vérifier si le nom d'utilisateur existe déjà
        if User.objects.filter(username=username).exists():
            messages.error(request, "Ce nom d'utilisateur est déjà pris.")
            return redirect('register')

        # Vérifier si les mots de passe correspondent
        if password != password2:
            messages.error(request, "Les mots de passe ne correspondent pas.")
            return redirect('register')

        # Créer l'utilisateur
        user = User.objects.create_user(username=username, password=password)
        user.save()

        messages.success(request, "Inscription réussie ! Vous pouvez maintenant vous connecter.")
        return redirect('login')

    return render(request, 'register.html')

def deconnexion_view(request):
    logout(request)
    return redirect('hello')

def inscription(request):
    return render(request, 'myapp/inscription.html')

def username_form(request):
    if request.method == 'POST':
        username = request.POST.get('username')  # Récupérer le nom d'utilisateur
        password = request.POST.get('password')  # Récupérer le mot de passe

        # Vérifier si les identifiants sont valides
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Si l'utilisateur existe et le mot de passe est correct, connecter l'utilisateur
            login(request, user)
            return redirect('user_feed')  # Redirige vers la page d'accueil ou une autre page après connexion
        else:
            # Si l'utilisateur n'existe pas ou le mot de passe est incorrect, afficher un message d'erreur
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
            return render(request, 'myapp/username_form.html')

    return render(request, 'myapp/username_form.html')

@login_required
def user_feed(request):
    # Récupérer les utilisateurs suivis par l'utilisateur connecté
    followed_users = UserFollows.objects.filter(user=request.user).values_list('followed_user', flat=True)
    
    # Récupérer tous les billets (tickets) des utilisateurs suivis
    tickets = Ticket.objects.filter(user__in=followed_users).order_by('-time_created')  # tri antichronologique
    
    # Récupérer les critiques pour ces tickets
    reviews = Review.objects.filter(ticket__in=tickets).order_by('-time_created')  # tri antichronologique
    
    context = {
        'tickets': tickets,
        'reviews': reviews
    }
    
    return render(request, 'myapp/user_feed.html', context)

@login_required
def follow_user(request):
    # Récupérer les utilisateurs suivis par l'utilisateur connecté
    followed_users = UserFollows.objects.filter(user=request.user).select_related('followed_user')
    followed_users = [uf.followed_user for uf in followed_users]

    # Récupérer les utilisateurs qui suivent l'utilisateur connecté
    followers = UserFollows.objects.filter(followed_user=request.user).select_related('user')
    followers = [uf.user for uf in followers]

    # Récupérer tous les utilisateurs sauf celui connecté
    users = User.objects.exclude(id=request.user.id)

    if request.method == "POST":
        if "unfollow" in request.POST:
            # Désabonnement : retirer la relation d'abonnement
            followed_user_id = request.POST.get("followed_user_id")
            followed_user = User.objects.get(id=followed_user_id)
            UserFollows.objects.filter(user=request.user, followed_user=followed_user).delete()
        elif "follow" in request.POST:
            # Abonnement : ajouter une relation d'abonnement
            followed_user_id = request.POST.get("followed_user")
            followed_user = User.objects.get(id=followed_user_id)
            # S'assurer que l'utilisateur ne suit pas déjà cet utilisateur
            if not UserFollows.objects.filter(user=request.user, followed_user=followed_user).exists():
                UserFollows.objects.create(user=request.user, followed_user=followed_user)

        # Rediriger après le traitement du formulaire
        return redirect('follow_user')

    context = {
        'followed_users': followed_users,
        'followers': followers,
        'users': users,
    }

    return render(request, 'follow_user.html', context)

@login_required
def choose_ticket(request):
    # Récupérer tous les billets créés par l'utilisateur connecté
    tickets = Ticket.objects.filter(user=request.user)

    if request.method == 'POST':
        # Récupérer l'ID du ticket sélectionné
        ticket_id = request.POST.get('ticket')
        ticket = Ticket.objects.get(id=ticket_id)  # Trouver le ticket correspondant

        # Passer le ticket sélectionné au template
        return render(request, 'ticket_detail.html', {'ticket': ticket})

    return render(request, 'choose_ticket.html', {'tickets': tickets})

@login_required
def manage_follows(request):
    # Récupérer les utilisateurs que l'utilisateur connecté suit
    followed_users = User.objects.filter(followed_by__user=request.user)

    if request.method == 'POST':
        # Désabonnement (suppression de la relation de suivi)
        followed_user_id = request.POST.get('followed_user_id')
        followed_user = User.objects.get(id=followed_user_id)

        # Vérifier si la relation existe et la supprimer
        try:
            user_follow = UserFollows.objects.get(user=request.user, followed_user=followed_user)
            user_follow.delete()
            messages.success(request, f"Vous avez désabonné {followed_user.username}.")
        except UserFollows.DoesNotExist:
            messages.error(request, "Relation de suivi non trouvée.")

        return redirect('manage_follows')  # Rediriger après avoir supprimé le suivi

    return render(request, 'manage_follows.html', {'followed_users': followed_users})


@login_required
def add_review(request, ticket_id):
    ticket = Ticket.objects.get(id=ticket_id)

    if request.method == 'POST':
        headline = request.POST.get('headline')
        body = request.POST.get('body')
        rating = request.POST.get('rating')

        # Créer la review
        Review.objects.create(
            headline=headline,
            body=body,
            rating=rating,
            user=request.user,
            ticket=ticket
        )

        # Passer un message de succès à la page de confirmation
        return render(request, 'add_review.html', {
            'ticket': ticket,
            'message': 'Vous avez ajouté une critique'
        })

    return render(request, 'add_review.html', {'ticket': ticket})

@login_required
def edit_ticket(request):
    if request.method == 'POST':
        # Récupérer l'ID du billet sélectionné depuis le formulaire POST
        ticket_id = request.POST.get('ticket_id')

        if ticket_id:
            # Récupérer le billet correspondant à l'ID sélectionné et vérifier que c'est le billet de l'utilisateur connecté
            ticket = get_object_or_404(Ticket, id=ticket_id, user=request.user)

            # Si les données de modification sont présentes (titre, description, image), les mettre à jour
            if 'ticket_title' in request.POST:
                ticket.title = request.POST.get('ticket_title', ticket.title)
                ticket.description = request.POST.get('ticket_description', ticket.description)

                # Si une image est téléchargée, la mettre à jour
                if 'ticket_image' in request.FILES:
                    ticket.image = request.FILES['ticket_image']

                # Sauvegarder les modifications du billet
                ticket.save()

                # Après la mise à jour, on peut rediriger vers une autre page, ici on redirige vers la même page
                return redirect('edit_ticket')  # Ou une autre URL de redirection, comme 'ticket_detail' ou 'home'

        else:
            return HttpResponse("Aucun billet sélectionné.", status=400)

    # Afficher tous les billets de l'utilisateur connecté dans le menu déroulant
    tickets = Ticket.objects.filter(user=request.user)
    ticket = None  # Initialisation à None si aucun billet n'est sélectionné

    # Si un billet a été sélectionné, on récupère le billet correspondant
    if 'ticket_id' in request.POST:
        ticket_id = request.POST.get('ticket_id')
        ticket = get_object_or_404(Ticket, id=ticket_id, user=request.user)

    return render(request, 'edit_ticket.html', {'tickets': tickets, 'ticket': ticket})

def create_ticket(request):
    # Logique pour afficher le formulaire de création d'un billet
    return render(request, 'create_ticket.html')

def create_review(request):
    # Logique pour afficher le formulaire de création d'une critique
    return render(request, 'create_review.html')

@login_required
def edit_review(request, review_id):
    # Récupérer la revue à modifier
    review = get_object_or_404(Review, id=review_id)

    if request.method == 'POST':
        # Récupérer les données du formulaire
        headline = request.POST.get('headline')
        body = request.POST.get('body')
        rating = request.POST.get('rating')

        # Mettre à jour la revue
        review.headline = headline
        review.body = body
        review.rating = rating
        review.save()

        # Rediriger vers la page des reviews du ticket après mise à jour
        return redirect('user_feed')
    
    return render(request, 'edit_review.html', {'review': review})

from django.shortcuts import render

def posts(request):
    # Logique de la vue, par exemple récupérer des posts depuis la base de données
    # posts = Post.objects.all()  # Exemple si vous récupérez des posts d'un modèle
    
    return render(request, 'posts.html')  # Cela rendra le template 'posts.html'

@login_required
def ticket_reviews(request):
    # Récupérer tous les tickets, peu importe leur propriétaire
    tickets = Ticket.objects.all()
    selected_ticket = None
    reviews = []

    # Si le formulaire est soumis (POST)
    if request.method == 'POST':
        ticket_id = request.POST.get('ticket')
        # Récupérer le ticket sélectionné et ses reviews
        selected_ticket = get_object_or_404(Ticket, id=ticket_id)
        reviews = Review.objects.filter(ticket=selected_ticket)

    return render(request, 'ticket_reviews.html', {
        'tickets': tickets,
        'selected_ticket': selected_ticket,
        'reviews': reviews
    })




@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    if request.method == 'POST' and request.POST.get('confirm_delete') == 'true':
        # Supprimer la revue
        review.delete()
        return redirect('all_tickets')  # Rediriger vers la page all_tickets après la suppression

    return render(request, 'confirm_delete_review.html', {'review': review})

@login_required
def ticket_selection(request):
    selected_owner = None
    selected_ticket = None
    tickets = []
    reviews = []

    # Vérifier si l'utilisateur a soumis le formulaire de sélection du propriétaire ou du ticket
    if request.method == 'POST':
        # Si un propriétaire est sélectionné
        if 'owner' in request.POST:
            selected_owner = User.objects.get(id=request.POST['owner'])
            tickets = Ticket.objects.filter(user=selected_owner)  # Récupérer les tickets de l'utilisateur sélectionné
            
            # Si un ticket est également sélectionné, récupérer les reviews associées
            if 'ticket' in request.POST:
                selected_ticket = Ticket.objects.get(id=request.POST['ticket'])
                reviews = Review.objects.filter(ticket=selected_ticket)

    # Récupérer tous les utilisateurs
    users = User.objects.all()

    return render(request, 'ticket_selection.html', {
        'users': users,
        'selected_owner': selected_owner,
        'tickets': tickets,
        'selected_ticket': selected_ticket,
        'reviews': reviews,
    })

@login_required
def create_ticket(request):
    if request.method == 'POST':
        # Si le formulaire est soumis
        title = request.POST.get('title')
        description = request.POST.get('description')
        image = request.FILES.get('image')  # Récupérer l'image téléchargée

        # Créer un nouveau ticket
        ticket = Ticket.objects.create(
            title=title,
            description=description,
            user=request.user,
            image=image
        )

        # Rediriger vers la page de la review du ticket créé
        return redirect('add_review', ticket_id=ticket.id)

    return render(request, 'create_ticket.html')

@login_required
def confirm_delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    # Vérifie si l'utilisateur est celui qui a écrit la review
    if review.user != request.user:
        return HttpResponseForbidden("Vous ne pouvez pas supprimer cette critique.")

    # Si c'est une requête GET, on affiche la confirmation
    if request.method == 'GET':
        return render(request, 'confirm_delete.html', {'review': review})

    # Si la requête est une POST, on supprime la review
    elif request.method == 'POST':
        review.delete()
        return redirect('user_feed')
    
@login_required
def all_tickets_view(request):
    order = request.GET.get('order', 'date')

    if order == 'user':
        tickets = Ticket.objects.all().order_by('user__username', '-time_created')  # Tri par utilisateur, puis par date
    else:
        tickets = Ticket.objects.all().order_by('-time_created')  # Tri par défaut : antichronologique

    paginator = Paginator(tickets, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'all_tickets.html', {
        'page_obj': page_obj,
    })

@login_required
def block_user_view(request, user_id):
    if request.method == 'POST':
        user_to_block = get_object_or_404(User, id=user_id)
        BlockRelation.objects.get_or_create(blocker=request.user, blocked=user_to_block)
        messages.success(request, f"{user_to_block.username} a été bloqué.")
    return redirect('follow_user')

@login_required
def follow_user_view(request):
    # Récupérer les utilisateurs suivis (followed_user) et les abonnés (user)
    followed_users = request.user.following.all().values_list('followed_user', flat=True)
    followers = request.user.followed_by.all().values_list('user', flat=True)

    followed_users = User.objects.filter(id__in=followed_users)
    followers = User.objects.filter(id__in=followers)

    followers = followers.exclude(id__isnull=True)

    blocked_users_ids = list(
        BlockRelation.objects.filter(blocker=request.user).values_list('blocked_id', flat=True)
    )

    # Traiter l'ajout d'un utilisateur à la liste des abonnements
    if request.method == 'POST':
        if 'follow' in request.POST:
            followed_user_id = request.POST.get('followed_user')
            followed_user = User.objects.get(id=followed_user_id)

            if not UserFollows.objects.filter(user=request.user, followed_user=followed_user).exists():
                UserFollows.objects.create(user=request.user, followed_user=followed_user)
                messages.success(request, f"Vous suivez maintenant {followed_user.username}.")
            else:
                messages.warning(request, "Vous suivez déjà cet utilisateur.")
            return redirect('follow_user')

        elif 'unfollow' in request.POST:
            followed_user_id = request.POST.get('followed_user_id')
            
            try:
                followed_user = User.objects.get(id=followed_user_id)  # Récupérer l'utilisateur à désabonner
                # Supprimer la relation d'abonnement
                UserFollows.objects.filter(user=request.user, followed_user=followed_user).delete()
                messages.success(request, f"Vous vous êtes désabonné de {followed_user.username}.")
            except User.DoesNotExist:
                messages.error(request, "Utilisateur introuvable.")
            
            return redirect('follow_user')

    # Contexte
    context = {
        'followed_users': followed_users,
        'followers': followers,
        'blocked_users_ids': blocked_users_ids,
        'users': User.objects.exclude(id=request.user.id),  # Exclure l'utilisateur connecté de la liste des utilisateurs
    }
    return render(request, 'follow_user.html', context)

@login_required
def confirm_block_user_view(request, user_id):
    user_to_block = get_object_or_404(User, id=user_id)
    return render(request, 'confirm_block_user.html', {'user_to_block': user_to_block})

@login_required
def block_user_view(request, user_id):
    user_to_block = get_object_or_404(User, id=user_id)

    # Vérifie si l'utilisateur n'est pas déjà bloqué
    if not BlockRelation.objects.filter(blocker=request.user, blocked=user_to_block).exists():
        # Crée une relation de blocage
        BlockRelation.objects.create(blocker=request.user, blocked=user_to_block)
        messages.success(request, f"{user_to_block.username} a été bloqué.")
    else:
        messages.warning(request, f"{user_to_block.username} est déjà bloqué.")

    # Rediriger vers la page des abonnements après le blocage
    return redirect('follow_user')