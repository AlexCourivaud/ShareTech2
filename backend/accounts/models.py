from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Utilisateur étendu avec rôles et informations supplémentaires
    """
    ROLE_CHOICES = [
        ('junior', 'Développeur Junior'),
        ('senior', 'Développeur Senior'), 
        ('lead', 'Lead Developer'),
        ('admin', 'Admin'),
    ]
    
    # Champs supplémentaires
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='junior')
    avatar_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    class Meta:
        db_table = 'accounts_user'