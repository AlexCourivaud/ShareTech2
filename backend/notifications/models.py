from django.db import models
from django.conf import settings

class Notification(models.Model):
    """
    Notifications in-app pour les utilisateurs
    """
    TYPE_CHOICES = [
        ('note_created', 'Note créée'),
        ('note_updated', 'Note mise à jour'),
        ('task_assigned', 'Tâche assignée'),
        ('task_completed', 'Tâche terminée'),
        ('comment_added', 'Commentaire ajouté'),
        ('mention', 'Mention'),
        ('project_invitation', 'Invitation projet'),
    ]
    
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    
    # Relations optionnelles vers les entités
    related_note = models.ForeignKey('core.Note', on_delete=models.SET_NULL, null=True, blank=True)
    related_task = models.ForeignKey('tasks.Task', on_delete=models.SET_NULL, null=True, blank=True)
    related_comment = models.ForeignKey('core.Comment', on_delete=models.SET_NULL, null=True, blank=True)
    related_project = models.ForeignKey('core.Project', on_delete=models.SET_NULL, null=True, blank=True)
    
    triggered_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='triggered_notifications')
    
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
    class Meta:
        db_table = 'NOTIFICATION'
        ordering = ['-created_at']