from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Project, ProjectMember


class ProjectMemberSerializer(serializers.ModelSerializer):
    """
    Serializer pour les membres d'un projet
    Affiche les infos de l'utilisateur membre
    """
    username = serializers.CharField(source='user.username', read_only=True)
    full_name = serializers.SerializerMethodField()
    role = serializers.CharField(source='user.profile.role', read_only=True)
    
    class Meta:
        model = ProjectMember
        fields = ['id', 'user', 'username', 'full_name', 'role', 'joined_at']
        read_only_fields = ['joined_at']
    
    def get_full_name(self, obj):
        """Retourne le nom complet de l'utilisateur"""
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.username


class ProjectListSerializer(serializers.ModelSerializer):
    """
    Serializer pour la liste des projets (vue simplifiée)
    """
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    member_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'is_active',
            'created_by', 'created_by_username', 'member_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']
    
    def get_member_count(self, obj):
        """Compte le nombre de membres du projet"""
        return obj.members.count()


class ProjectDetailSerializer(serializers.ModelSerializer):
    """
    Serializer pour le détail d'un projet (vue complète)
    Inclut la liste des membres
    """
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    created_by_full_name = serializers.SerializerMethodField()
    members = ProjectMemberSerializer(many=True, read_only=True)
    
    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'is_active',
            'created_by', 'created_by_username', 'created_by_full_name',
            'members', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']
    
    def get_created_by_full_name(self, obj):
        """Retourne le nom complet du créateur"""
        if obj.created_by:
            return f"{obj.created_by.first_name} {obj.created_by.last_name}".strip() or obj.created_by.username
        return "Créateur inconnu"


class ProjectCreateSerializer(serializers.ModelSerializer):
    """
    Serializer pour la création d'un projet
    """
    class Meta:
        model = Project
        fields = ['name', 'description']
    
    def create(self, validated_data):
        """Crée un projet avec le créateur automatique"""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class AddMemberSerializer(serializers.Serializer):
    """
    Serializer pour ajouter un membre à un projet
    """
    user_id = serializers.IntegerField()
    
    def validate_user_id(self, value):
        """Vérifie que l'utilisateur existe"""
        try:
            User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Cet utilisateur n'existe pas")
        return value