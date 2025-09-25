from django.db import models
from django.conf import settings

class Attachment(models.Model):
    """
    Fichiers joints aux notes et commentaires
    """
    original_name = models.CharField(max_length=255)
    stored_name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500)
    file_size = models.IntegerField()
    mime_type = models.CharField(max_length=100)
    file_hash = models.CharField(max_length=64, blank=True, null=True)
    
    # Relations optionnelles (fichier lié à une note OU un commentaire)
    note = models.ForeignKey('core.Note', on_delete=models.CASCADE, null=True, blank=True, related_name='attachments')
    comment = models.ForeignKey('core.Comment', on_delete=models.CASCADE, null=True, blank=True, related_name='attachments')
    
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='uploaded_files')
    upload_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.original_name
    
    class Meta:
        db_table = 'ATTACHMENT'