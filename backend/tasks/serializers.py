from rest_framework import serializers
from django.utils import timezone
from .models import Task, TaskTag
from accounts.serializers import UserSerializer
from projects.serializers import ProjectListSerializer
from tags.serializers import TagSerializer
from tags.models import Tag  # ✅ AJOUTÉ


class TaskTagSerializer(serializers.ModelSerializer):
    """Serializer pour afficher les tags d'une tâche"""
    tag = TagSerializer(read_only=True)
    
    class Meta:
        model = TaskTag
        fields = ['id', 'tag', 'assigned_at']


class TaskListSerializer(serializers.ModelSerializer):
    """Serializer pour la liste des tâches (vue simplifiée)"""
    project = ProjectListSerializer(read_only=True)
    assigned_to = UserSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    
    # Afficher les labels lisibles au lieu des valeurs brutes
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    
    # Compteur de tags
    tags_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'status', 'status_display', 'priority', 'priority_display',
            'due_date', 'project', 'assigned_to', 'created_by', 'created_at', 'tags_count'
        ]
    
    def get_tags_count(self, obj):
        return obj.task_tags.count()


class TaskDetailSerializer(serializers.ModelSerializer):
    """Serializer pour le détail d'une tâche (vue complète)"""
    project = ProjectListSerializer(read_only=True)
    assigned_to = UserSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    task_tags = TaskTagSerializer(many=True, read_only=True)
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status', 'status_display', 
            'priority', 'priority_display', 'estimated_hours', 'actual_hours',
            'due_date', 'completed_date', 'project', 'assigned_to', 'created_by',
            'created_at', 'updated_at', 'task_tags'
        ]


class TaskCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer pour créer/modifier une tâche"""
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        required=False,
        write_only=True
    )
    
    class Meta:
        model = Task
        fields = [
            'title', 'description', 'priority', 'estimated_hours',
            'due_date', 'project', 'tags'
        ]
    
    def validate_title(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Le titre doit contenir au moins 3 caractères.")
        return value
    
    def create(self, validated_data):
        tags_data = validated_data.pop('tags', [])
        
        # Créer la tâche avec statut 'ouverte' par défaut
        task = Task.objects.create(**validated_data)
        
        # Ajouter les tags
        for tag in tags_data:
            TaskTag.objects.create(task=task, tag=tag)
        
        return task
    
    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags', None)
        
        # Mettre à jour les champs de la tâche
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Mettre à jour les tags si fournis
        if tags_data is not None:
            # Supprimer les anciens tags
            instance.task_tags.all().delete()
            # Ajouter les nouveaux
            for tag in tags_data:
                TaskTag.objects.create(task=instance, tag=tag)
        
        return instance


class AssignTaskSerializer(serializers.Serializer):
    """Serializer pour assigner une tâche à un utilisateur"""
    user_id = serializers.IntegerField()
    
    def validate_user_id(self, value):
        from django.contrib.auth.models import User
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("Utilisateur introuvable.")
        return value