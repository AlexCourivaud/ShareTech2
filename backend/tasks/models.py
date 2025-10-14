from django.db import models
from django.contrib.auth.models import User
from projects.models import Project
from tags.models import Tag


class Task(models.Model):
    """Tâche de projet"""
    
    STATUS_CHOICES = [
        ('ouverte', 'Ouverte'),
        ('assignee', 'Assignée'),
        ('terminee', 'Terminée'),
    ]
    
    PRIORITY_CHOICES = [
        ('basse', 'Basse'),
        ('normale', 'Normale'),
        ('haute', 'Haute'),
        ('urgente', 'Urgente'),
    ]
    
    title = models.CharField(max_length=200, verbose_name='Titre')
    description = models.TextField(blank=True, null=True, verbose_name='Description')
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='ouverte', 
        verbose_name='Statut'
    )
    priority = models.CharField(
        max_length=20, 
        choices=PRIORITY_CHOICES, 
        default='normale', 
        verbose_name='Priorité'
    )
    
    estimated_hours = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        blank=True, 
        null=True, 
        verbose_name='Heures estimées'
    )
    actual_hours = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        blank=True, 
        null=True, 
        verbose_name='Heures réelles'
    )
    
    due_date = models.DateField(blank=True, null=True, verbose_name='Date d\'échéance')
    completed_date = models.DateField(blank=True, null=True, verbose_name='Date de complétion')
    
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,  # Si projet supprimé → tâches supprimées
        related_name='tasks',
        verbose_name='Projet'
    )
    
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,  # Si user supprimé → tâche reste mais assignation perdue
        related_name='assigned_tasks',
        blank=True,
        null=True,
        verbose_name='Assigné à'
    )
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,  # Si créateur supprimé → tâches supprimées
        related_name='created_tasks',
        verbose_name='Créé par'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Créé le')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Modifié le')
    
    class Meta:
        db_table = 'task'
        verbose_name = 'Tâche'
        verbose_name_plural = 'Tâches'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class TaskTag(models.Model):
    """Relation N:M entre tâches et tags"""
    
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='task_tags'
    )
    
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name='task_tags'
    )
    
    assigned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'task_tag'
        unique_together = ['task', 'tag']
    
    def __str__(self):
        return f"{self.task.title} - {self.tag.name}"