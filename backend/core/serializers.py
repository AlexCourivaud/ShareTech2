from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Project, Note, Comment, Tag, NoteFavorite


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'color']


class UserBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']


class ProjectSerializer(serializers.ModelSerializer):
    created_by = UserBasicSerializer(read_only=True)
    members = UserBasicSerializer(many=True, read_only=True)
    
    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'created_by', 'members', 'created_at', 'updated_at']


class CommentSerializer(serializers.ModelSerializer):
    author = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'content', 'author', 'parent_comment', 'created_at', 'updated_at']


class NoteSerializer(serializers.ModelSerializer):
    author = UserBasicSerializer(read_only=True)
    project = ProjectSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    
    class Meta:
        model = Note
        fields = ['id', 'title', 'content', 'project', 'author', 'tags', 'comments', 'is_favorited', 'created_at', 'updated_at']
    
    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return NoteFavorite.objects.filter(user=request.user, note=obj).exists()
        return False