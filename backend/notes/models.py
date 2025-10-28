# backend/notes/models.py

from django.db import models
from django.contrib.auth.models import User
from projects.models import Project
from tags.models import Tag


class Note(models.Model):
    """
    Modèle Note pour ShareTech
    Gestion de la documentation et du partage de connaissances
    """
    
    STATUS_CHOICES = [
        ('brouillon', 'Brouillon'),
        ('publie', 'Publié'),
        ('archive', 'Archivé'),
    ]
    
    title = models.CharField(
        max_length=200,
        verbose_name='Titre'
    )
    
    content = models.TextField(
        verbose_name='Contenu'
    )
    
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='brouillon',
        verbose_name='Statut'
    )
    
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='notes',
        verbose_name='Projet'
    )
    
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='authored_notes',
        verbose_name='Auteur'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date de création'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Dernière modification'
    )
    
    published_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Date de publication'
    )
    
    class Meta:
        db_table = 'note'
        verbose_name = 'Note'
        verbose_name_plural = 'Notes'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project'], name='idx_note_project'),
            models.Index(fields=['author'], name='idx_note_author'),
            models.Index(fields=['status'], name='idx_note_status'),
            models.Index(fields=['project', 'status'], name='idx_note_project_status'),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"


class NoteTag(models.Model):
    """
    Modèle NoteTag pour ShareTech
    Relation Many-to-Many entre Note et Tag
    """
    
    note = models.ForeignKey(
        Note,
        on_delete=models.CASCADE,
        related_name='note_tags',
        verbose_name='Note'
    )
    
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name='note_tags',
        verbose_name='Tag'
    )
    
    assigned_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date d\'assignation'
    )
    
    class Meta:
        db_table = 'note_tag'
        verbose_name = 'Tag de note'
        verbose_name_plural = 'Tags de notes'
        constraints = [
            models.UniqueConstraint(
                fields=['note', 'tag'],
                name='unique_note_tag'
            )
        ]
        indexes = [
            models.Index(fields=['note'], name='idx_note_tag_note'),
            models.Index(fields=['tag'], name='idx_note_tag_tag'),
        ]
    
    def __str__(self):
        return f"{self.note.title} - {self.tag.name}"