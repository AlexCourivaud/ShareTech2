from django.contrib.auth.models import User
from django.db import models


class Project(models.Model):
    """
    Modèle Project pour ShareTech
    Gère les projets collaboratifs
    """
    
    # Nom du projet 
    name = models.CharField(
        max_length=100,
        verbose_name='Nom du projet'
    )
    
    # Description courte obligatoire (max 150 caractères)
    description = models.CharField(
        max_length=150,
        verbose_name='Description courte'
    )
    
    # Statut du projet : True = actif, False = terminé/annulé
    is_active = models.BooleanField(
        default=True,
        verbose_name='Projet actif'
    )
    
    # Créateur du projet (peut être NULL si l'utilisateur est supprimé)
    # SET_NULL garde le projet même si le créateur quitte l'entreprise
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='created_projects',
        verbose_name='Créé par'
    )

    
    # Date de création automatique (non modifiable après création) - automatique
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date de création'
    )
    
    # Date de dernière modification -  automatique
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Dernière modification'
    )
    
    class Meta:
        # Nom de la table en base de données
        db_table = 'project'
        
        # Noms affichés dans l'interface d'administration Django
        verbose_name = 'Projet'
        verbose_name_plural = 'Projets'
        
        # Tri par défaut : projets les plus récents en premier
        ordering = ['-created_at']
        
        # Index pour accélérer les recherches fréquentes
        # created_by : filtrer par créateur, is_active : filtrer actif/terminé
        indexes = [
            models.Index(fields=['created_by'], name='idx_project_created_by'),
            models.Index(fields=['is_active'], name='idx_project_is_active'),
        ]
    
    # Représentation textuelle du projet dans l'admin et les logs
    # Affiche "Nom du projet (Actif)" ou "Nom du projet (Terminé)"
    def __str__(self):
        status = "Actif" if self.is_active else "Terminé"
        return f"{self.name} ({status})"
    
    # Méthode pour terminer un projet
    def terminate(self):
        """Marque le projet comme terminé"""
        self.is_active = False
        self.save()


class ProjectMember(models.Model):
    """
    Modèle ProjectMember pour ShareTech
    Les permissions sont définies par le rôle global (UserProfile.role)
    """
    
    # Projet auquel appartient ce membre (suppression en cascade)
    # Si le projet est supprimé, toutes ses affiliations sont supprimées
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='members',
        verbose_name='Projet'
    )
    
    # Utilisateur membre du projet (PROTECT empêche la suppression)
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='project_memberships',
        verbose_name='Utilisateur'
    )
    
    # Date d'ajout au projet (automatique, non modifiable)
    joined_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date d\'ajout'
    )
    
    class Meta:
        # Nom de la table en base de données
        db_table = 'project_member'
        
        # Noms affichés dans l'interface d'administration Django
        verbose_name = 'Membre de projet'
        verbose_name_plural = 'Membres de projets'
        
        # Tri par défaut : membres les plus récents en premier
        ordering = ['-joined_at']
        
        # Contrainte d'unicité : un user ne peut être ajouté qu'une fois par projet
        constraints = [
            models.UniqueConstraint(
                fields=['project', 'user'],
                name='unique_project_user'
            )
        ]
        
        # Index pour accélérer les recherches sur project_id et user_id
        # Utilisés fréquemment pour lister les membres d'un projet ou les projets d'un user
        indexes = [
            models.Index(fields=['project'], name='idx_project_member_project'),
            models.Index(fields=['user'], name='idx_project_member_user'),
        ]
    
    # Représentation textuelle dans l'admin et les logs
    # Affiche "username - Nom du projet (Rôle)"
    def __str__(self):
        return f"{self.user.username} - {self.project.name} ({self.get_role_project_display()})"