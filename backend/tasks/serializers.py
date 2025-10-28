from rest_framework import serializers
from django.utils import timezone
from .models import Task, TaskTag
from accounts.serializers import UserSerializer
from projects.serializers import ProjectListSerializer
from tags.serializers import TagSerializer
from tags.models import Tag
from django.contrib.auth.models import User


class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer unique pour toutes les opérations sur les tâches
    """
    # Champs en lecture seule pour affichage
    author_username = serializers.CharField(source='created_by.username', read_only=True)
    assigned_to_username = serializers.CharField(source='assigned_to.username', read_only=True, allow_null=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    
    # Tags (lecture et écriture)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        required=False
    )
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 'priority',
            'estimated_hours', 'actual_hours', 'due_date', 'completed_date',
            'project', 'project_name',
            'assigned_to', 'assigned_to_username',
            'created_by', 'author_username',
            'tags',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'completed_date', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """Création d'une tâche avec ses tags"""
        tags_data = validated_data.pop('tags', [])
        
        # Créer la tâche
        task = Task.objects.create(**validated_data)
        
        # Ajouter les tags
        for tag in tags_data:
            TaskTag.objects.create(task=task, tag=tag)
        
        return task
    
    def update(self, instance, validated_data):
        """Mise à jour d'une tâche avec ses tags"""
        tags_data = validated_data.pop('tags', None)
        
        # Mettre à jour les champs de la tâche
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Mettre à jour les tags si fournis
        if tags_data is not None:
            # Supprimer les anciens tags
            instance.task_tags.all().delete()
            
            # Ajouter les nouveaux tags
            for tag in tags_data:
                TaskTag.objects.create(task=instance, tag=tag)
        
        return instance


class AssignTaskSerializer(serializers.Serializer):
    """
    Serializer pour valider l'assignation d'une tâche
    Utilisé uniquement pour l'action 'assign'
    """
    user_id = serializers.IntegerField()
    
    def validate_user_id(self, value):
        """Vérifier que l'utilisateur existe"""
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("Utilisateur introuvable.")
        return value