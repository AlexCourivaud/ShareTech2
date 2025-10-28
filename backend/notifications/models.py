from django.db import models

# Create your models here.

class Notification(models.Model):
    """Notification"""
    
    content = models.TextField(verbose_name='Contenu')
    
    notification = models.ForeignKey(
        User,
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
    

    
    # created_at = models.DateTimeField(
    #     auto_now_add=True,
    #     verbose_name='Créé le'
    # )
    
    # updated_at = models.DateTimeField(
    #     auto_now=True,
    #     verbose_name='Modifié le'
    # )
    
    class Meta: #done
        db_table = 'notification'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['created_at']
    
    def __str__(self): # no change 
        author_name = self.author.username if self.author else '[Compte supprimé]'
        preview = self.content[:50]
        return f"{author_name} - {preview}"