from django.contrib import admin
from .models import Project, ProjectMember, Note, Tag, Comment, NoteFavorite


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_by', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ['title', 'project', 'author', 'created_at']
    list_filter = ['project', 'created_at']
    search_fields = ['title', 'content']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['note', 'author', 'created_at']
    list_filter = ['created_at']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'color']


admin.site.register(ProjectMember)
admin.site.register(NoteFavorite)