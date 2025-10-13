from django.db import models


class Tag(models.Model):
    """
    Modèle Tag pour ShareTech
    Tags partagés pour classifier Notes et Tasks
    """
    
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Nom du tag'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date de création'
    )
    
    class Meta:
        db_table = 'tag'
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
        ordering = ['name']  # Ordre alphabétique simple
        indexes = [
            models.Index(fields=['name'], name='idx_tag_name'),
        ]
    
    def __str__(self):
        return self.name

    