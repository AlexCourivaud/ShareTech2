from django.contrib import admin
from .models import Project, ProjectMember, Note, Tag, Comment

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Interface d'administration pour les projets"""
    
    list_display = ('name', 'created_by', 'created_at', 'members_count')
    list_filter = ('created_at', 'created_by')
    search_fields = ('name', 'description')
    ordering = ('-created_at',)
    
    def members_count(self, obj):
        return obj.members.count()
    members_count.short_description = 'Nb membres'


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    """Interface d'administration pour les notes"""
    
    list_display = ('title', 'project', 'author', 'created_at', 'tags_list')
    list_filter = ('project', 'author', 'tags', 'created_at')
    search_fields = ('title', 'content')
    filter_horizontal = ('tags',)
    ordering = ('-created_at',)
    
    def tags_list(self, obj):
        return ", ".join([tag.name for tag in obj.tags.all()])
    tags_list.short_description = 'Tags'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Interface d'administration pour les tags"""
    
    list_display = ('name', 'color', 'notes_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name',)
    ordering = ('name',)
    
    def notes_count(self, obj):
        return obj.notes.count()
    notes_count.short_description = 'Nb notes'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Interface d'administration pour les commentaires"""
    
    list_display = ('note', 'author', 'parent_comment', 'created_at', 'content_preview')
    list_filter = ('note__project', 'author', 'created_at')
    search_fields = ('content', 'note__title')
    ordering = ('-created_at',)
    
    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Aperçu contenu'


@admin.register(ProjectMember)
class ProjectMemberAdmin(admin.ModelAdmin):
    """Interface d'administration pour les membres de projets"""
    
    list_display = ('project', 'user', 'joined_at')
    list_filter = ('project', 'joined_at')
    search_fields = ('project__name', 'user__username')
    ordering = ('-joined_at',)