from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """Profil utilisateur étendu pour ShareTech"""
    
    ROLE_CHOICES = [
        ('junior', 'Développeur Junior'),
        ('senior', 'Développeur Senior'),
        ('lead', 'Lead Developer'),
        ('admin', 'Administrateur'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='junior')
    avatar_url = models.URLField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"
    
    class Meta:
        db_table = 'accounts_userprofile'