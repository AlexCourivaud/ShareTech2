from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Project(models.Model):
    """Projets collaboratifs"""
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_projects')
    members = models.ManyToManyField(User, through='ProjectMember', related_name='projects')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'core_project'


class ProjectMember(models.Model):
    """Relation many-to-many entre User et Project"""
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'core_projectmember'
        unique_together = ('project', 'user')


class Tag(models.Model):
    """Tags pour classifier les notes"""
    
    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=7, default='#gray')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'core_tag'


class Note(models.Model):
    """Notes techniques avec contenu mixte"""
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='notes')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='authored_notes')
    tags = models.ManyToManyField(Tag, blank=True, related_name='notes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        db_table = 'core_note'


class Comment(models.Model):
    """Commentaires hiérarchiques sur les notes"""
    
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Commentaire sur {self.note.title}"
    
    class Meta:
        db_table = 'core_comment'