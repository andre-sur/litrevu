from django.contrib.auth.models import User
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, MaxLengthValidator

class Ticket(models.Model):
    title = models.CharField(max_length=128)  
    description = models.TextField(max_length=2048, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    time_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.time_created}"


class Review(models.Model):  
    headline = models.CharField(max_length=128) 
    ticket = models.ForeignKey(Ticket, on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(0),
            MaxValueValidator(5)
        ]
    )
    body = models.TextField(
        blank=True,
        validators=[MaxLengthValidator(8192)]
    )
    time_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review '{self.headline}' for Ticket '{self.ticket.title}' - Rating: {self.rating}"

class UserFollows(models.Model):
    # L'utilisateur qui suit un autre utilisateur
    user = models.ForeignKey(
        User,  # Lien vers le modèle utilisateur (User ou CustomUser)
        on_delete=models.CASCADE,  # Si l'utilisateur est supprimé, relation suivi supprimée
        related_name='following'  # Nom de la relation inverse pour l'utilisateur qui suit
    )
    
    # L'utilisateur qui est suivi
    followed_user = models.ForeignKey(
        User,  # Lien vers le modèle utilisateur (User ou CustomUser)
        on_delete=models.CASCADE,  # Si l'utilisateur suivi est supprimé, la relation est supprimée
        related_name='followed_by'  # Nom de la relation inverse pour les utilisateurs qui suivent
    )

    class Meta:
     
        # Assurer qu'un utilisateur ne suive pas plusieurs fois le même utilisateur
        unique_together = ('user', 'followed_user')  # Contrainte d'unicité

    def __str__(self):
        return f"{self.user} follows {self.followed_user}"

# Create your models here.
class BlockRelation(models.Model):
    blocker = models.ForeignKey(User, related_name='blocking', on_delete=models.CASCADE)
    blocked = models.ForeignKey(User, related_name='blocked_by', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('blocker', 'blocked')

    def __str__(self):
        return f"{self.blocker.username} a bloqué {self.blocked.username}"
