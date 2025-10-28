# backend/accounts/models.py

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """
    Profil utilisateur étendu pour ShareTech
    Lié au User Django par défaut via une relation OneToOne
    """
    
    ROLE_CHOICES = [
        ('junior', 'Junior Developer'),
        ('senior', 'Senior Developer'),
        ('lead', 'Lead Developer'),
        ('admin', 'Admin'),
    ]
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='Utilisateur'
    )
    
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='junior',
        verbose_name='Rôle'
    )
    
    avatar_url = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Avatar URL'
    )
    
    class Meta:
        db_table = 'user_profile'
        verbose_name = 'Profil Utilisateur'
        verbose_name_plural = 'Profils Utilisateurs'
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"


# Signal pour créer automatiquement un profil quand un User est créé
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Crée automatiquement un UserProfile quand un User est créé.
    Les superusers obtiennent automatiquement le role='admin'.
    """
    if created:
        # Superuser = admin, autres = junior par défaut
        role = 'admin' if instance.is_superuser else 'junior'
        UserProfile.objects.create(user=instance, role=role)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Sauvegarde le profil quand le user est sauvegardé"""
    try:
        instance.profile.save()
    except UserProfile.DoesNotExist:
        # Si le profil n'existe pas encore (cas rare), le créer
        role = 'admin' if instance.is_superuser else 'junior'
        UserProfile.objects.create(user=instance, role=role)