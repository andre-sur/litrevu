from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, authenticate, login
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Review, Ticket, UserFollows, BlockRelation
from .forms import CustomUserCreationForm
from itertools import chain
from operator import attrgetter


def register(request):
    """
    Gère l'inscription d'un nouvel utilisateur : vérifie la disponibilité du nom d'utilisateur
    et la correspondance des mots de passe, puis crée l'utilisateur.
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Ce nom d'utilisateur est déjà pris.")
            return redirect('register')

        if password != password2:
            messages.error(request, "Les mots de passe ne correspondent pas.")
            return redirect('register')

        user = User.objects.create_user(username=username, password=password)
        user.save()

        messages.success(request, "Inscription réussie ! Vous pouvez maintenant vous connecter.")
        return redirect('login')

    return render(request, 'register.html')


def deconnexion_view(request):
    """
    Déconnecte l'utilisateur et le redirige vers la page de connexion.
    """
    logout(request)
    return redirect('login')


@login_required
def user_feed(request):
    """
    Affiche le flux personnalisé de l'utilisateur contenant les tickets 
    et les critiques des utilisateurs suivis.
    """
    followed_users_ids = list(
        UserFollows.objects.filter(user=request.user).values_list('followed_user', flat=True)
    )
    followed_users_ids.append(request.user.id)

    tickets = Ticket.objects.filter(user__in=followed_users_ids).order_by('-time_created')
    reviews = Review.objects.filter(ticket__in=tickets).order_by('-time_created')

    reviews_dict = {}
    for review in reviews:
        reviews_dict.setdefault(review.ticket_id, []).append(review)

    tickets_with_reviews = []
    for ticket in tickets:
        tickets_with_reviews.append({
            'ticket': ticket,
            'reviews': reviews_dict.get(ticket.id, [])
        })

    context = {
        'tickets_with_reviews': tickets_with_reviews,
    }

    return render(request, 'user_feed.html', context)


from django.contrib import messages
from django.shortcuts import redirect

@login_required
def create_review(request, ticket_id):
    """
    Permet à un utilisateur de créer une critique liée à un ticket existant,
    sauf s'il en a déjà écrit une pour ce ticket.
    """
    ticket = get_object_or_404(Ticket, id=ticket_id)

    # Vérifie si l'utilisateur a déjà écrit une review pour ce ticket
    if Review.objects.filter(ticket=ticket, user=request.user).exists():
        messages.error(request, "Vous avez déjà écrit une critique pour ce ticket.")
        return redirect('user_feed')

    if request.method == 'POST':
        headline = request.POST.get('headline')
        body = request.POST.get('body')
        rating = request.POST.get('rating')

        # Validation simple du champ rating
        try:
            rating = int(rating)
            if not (0 <= rating <= 5):
                messages.error(request, "La note doit être comprise entre 0 et 5.")
                return render(request, 'create_review.html', {'ticket': ticket})
        except ValueError:
            messages.error(request, "La note doit être un nombre entier.")
            return render(request, 'create_review.html', {'ticket': ticket})

        Review.objects.create(
            headline=headline,
            body=body,
            rating=rating,
            user=request.user,
            ticket=ticket
        )

        messages.success(request, "Votre critique a été enregistrée.")
        return redirect('user_feed')

    return render(request, 'create_review.html', {'ticket': ticket})

@login_required
def edit_ticket(request, ticket_id):
    """
    Permet à l'utilisateur de modifier l'un de ses tickets existants.
    """
    ticket = get_object_or_404(Ticket, id=ticket_id, user=request.user)

    if request.method == 'POST':
        ticket.title = request.POST.get('ticket_title', ticket.title)
        ticket.description = request.POST.get('ticket_description', ticket.description)

        if 'ticket_image' in request.FILES:
            ticket.image = request.FILES['ticket_image']

        ticket.save()
        return redirect('all_tickets')

    return render(request, 'edit_ticket.html', {'ticket': ticket})


from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from .models import Review

@login_required
def edit_review(request, review_id):
    """
    Permet à l'utilisateur de modifier une critique existante,
    avec validation du champ rating (entre 0 et 5).
    """
    review = get_object_or_404(Review, id=review_id)

    if request.method == 'POST':
        headline = request.POST.get('headline')
        body = request.POST.get('body')
        rating = request.POST.get('rating')

        try:
            rating = int(rating)
            if rating < 0 or rating > 5:
                raise ValueError
        except (ValueError, TypeError):
            return render(request, 'edit_review.html', {
                'review': review,
                'message': "La note doit être un nombre entier entre 0 et 5."
            })

        review.headline = headline
        review.body = body
        review.rating = rating
        review.save()

        return redirect('user_feed')
    
    return render(request, 'edit_review.html', {'review': review})


@login_required
def delete_ticket(request, ticket_id):
    """
    Supprime un ticket après confirmation de l'utilisateur.
    """
    ticket = get_object_or_404(Ticket, id=ticket_id)

    if request.method == 'POST' and request.POST.get('confirm_delete') == 'true':
        ticket.delete()
        return redirect('all_tickets')

    return render(request, 'confirm_delete_ticket.html', {'ticket': ticket})


@login_required
def create_ticket_and_review(request):
    """
    Permet à l'utilisateur de créer un nouveau ticket.
    """
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        image = request.FILES.get('image')

        ticket = Ticket.objects.create(
            title=title,
            description=description,
            user=request.user,
            image=image
        )

        return redirect('create_review', ticket_id=ticket.id)

    return render(request, 'create_ticket.html')

@login_required
def create_ticket(request):
    """
    Permet à un utilisateur de créer un ticket seul, 
    puis redirige vers le fil d'actualité.
    """
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        image = request.FILES.get('image')

        Ticket.objects.create(
            title=title,
            description=description,
            image=image,
            user=request.user
        )

        return redirect('user_feed')

    return render(request, 'create_ticket.html')

@login_required
def confirm_delete_review(request, review_id):
    """
    Affiche une page de confirmation pour supprimer une critique.
    """
    review = get_object_or_404(Review, id=review_id)

    if review.user != request.user:
        return HttpResponseForbidden("Vous ne pouvez pas supprimer cette critique.")

    if request.method == 'GET':
        return render(request, 'confirm_delete_review.html', {'review': review})

    elif request.method == 'POST':
        review.delete()
        return redirect('user_feed')


@login_required
def confirm_delete_ticket(request, ticket_id):
    """
    Affiche une page de confirmation pour supprimer un ticket.
    """
    ticket = get_object_or_404(Ticket, id=ticket_id)

    if ticket.user != request.user:
        return HttpResponseForbidden("Vous ne pouvez pas supprimer ce ticket.")

    if request.method == 'GET':
        return render(request, 'confirm_delete_ticket.html', {'ticket': ticket})

    elif request.method == 'POST':
        ticket.delete()
        return redirect('user_feed')

@login_required
def all_tickets_view(request):
    """
    Affiche uniquement les tickets créés par l'utilisateur connecté, triés par date décroissante avec pagination.
    """
    tickets = Ticket.objects.filter(user=request.user).order_by('-time_created')

    paginator = Paginator(tickets, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'all_tickets.html', {
        'page_obj': page_obj,
    })




@login_required
def block_user_view(request, user_id):
    """
    Bloque un utilisateur spécifié s'il n'est pas déjà bloqué.
    """
    user_to_block = get_object_or_404(User, id=user_id)

    if not BlockRelation.objects.filter(blocker=request.user, blocked=user_to_block).exists():
        BlockRelation.objects.create(blocker=request.user, blocked=user_to_block)
        messages.success(request, f"{user_to_block.username} a été bloqué.")
    else:
        messages.warning(request, f"{user_to_block.username} est déjà bloqué.")

    return redirect('follow_user')


from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth.models import User

@login_required
def follow_user_view(request):
    # Récupérer les utilisateurs déjà suivis
    followed_users = request.user.following.all().values_list('followed_user', flat=True)
    followers = request.user.followed_by.all().values_list('user', flat=True)

    followed_users_qs = User.objects.filter(id__in=followed_users)
    followers_qs = User.objects.filter(id__in=followers).exclude(id__isnull=True)

    blocked_users_ids = list(BlockRelation.objects.filter(blocker=request.user).values_list('blocked_id', flat=True))

    # Utilisateurs que l'on peut suivre : tous sauf soi-même et ceux déjà suivis
    users = User.objects.exclude(id__in=followed_users).exclude(id=request.user.id)

    if request.method == 'POST':
        if 'follow' in request.POST:
            followed_user_id = request.POST.get('followed_user')
            try:
                followed_user = User.objects.get(id=followed_user_id)
                if not UserFollows.objects.filter(user=request.user, followed_user=followed_user).exists():
                    UserFollows.objects.create(user=request.user, followed_user=followed_user)
                    messages.success(request, f"Vous suivez maintenant {followed_user.username}.")
                else:
                    messages.warning(request, "Vous suivez déjà cet utilisateur.")
            except User.DoesNotExist:
                messages.error(request, "Utilisateur introuvable.")
            return redirect('follow_user')

        elif 'unfollow' in request.POST:
            followed_user_id = request.POST.get('followed_user_id')
            try:
                followed_user = User.objects.get(id=followed_user_id)
                UserFollows.objects.filter(user=request.user, followed_user=followed_user).delete()
                messages.success(request, f"Vous vous êtes désabonné de {followed_user.username}.")
            except User.DoesNotExist:
                messages.error(request, "Utilisateur introuvable.")
            return redirect('follow_user')

    return render(request, 'follow_user.html', {
        'followed_users': followed_users_qs,
        'followers': followers_qs,
        'blocked_users_ids': blocked_users_ids,
        'users': users,
    })
