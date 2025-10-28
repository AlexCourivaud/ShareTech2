# backend/projects/models.py

from django.db import models
from django.contrib.auth.models import User
from notes.models import Note


class Comment(models.Model):
    """Commentaire sur une note"""
    
    content = models.TextField(verbose_name='Contenu')
    
    note = models.ForeignKey(
        Note,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Note'
    )
    
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL, 
        null=True,
        blank=True,
        related_name='comments',
        verbose_name='Auteur'
    )
    
    parent_comment = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='replies',
        blank=True,
        null=True,
        verbose_name='Commentaire parent'
    )
    
    is_edited = models.BooleanField(
        default=False,
        verbose_name='Modifié'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Créé le'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Modifié le'
    )
    
    class Meta:
        db_table = 'comment'
        verbose_name = 'Commentaire'
        verbose_name_plural = 'Commentaires'
        ordering = ['created_at']
    
    def __str__(self):
        author_name = self.author.username if self.author else '[Compte supprimé]'
        preview = self.content[:50]
        return f"{author_name} - {preview}"