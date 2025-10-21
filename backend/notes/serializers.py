from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Note, NoteTag
from tags.models import Tag
from tags.serializers import TagSerializer


class NoteTagSerializer(serializers.ModelSerializer):
    """
    Serializer pour la relation Note-Tag
    """
    tag_name = serializers.CharField(source='tag.name', read_only=True)
    
    class Meta:
        model = NoteTag
        fields = ['id', 'tag', 'tag_name', 'assigned_at']
        read_only_fields = ['assigned_at']


class NoteListSerializer(serializers.ModelSerializer):
    """
    Serializer pour la liste des notes (vue simplifiée)
    """
    author_username = serializers.CharField(source='author.username', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    tags = TagSerializer(source='note_tags.tag', many=True, read_only=True)
    
    class Meta:
        model = Note
        fields = [
            'id', 'title', 'status', 'project', 'project_name',
            'author', 'author_username', 'tags', 'created_at', 'updated_at'
        ]
        read_only_fields = ['author', 'created_at', 'updated_at']


class NoteDetailSerializer(serializers.ModelSerializer):
    """
    Serializer pour le détail complet d'une note
    """
    author_username = serializers.CharField(source='author.username', read_only=True)
    author_full_name = serializers.SerializerMethodField()
    project_name = serializers.CharField(source='project.name', read_only=True)
    tags = serializers.SerializerMethodField()
    
    class Meta:
        model = Note
        fields = [
            'id', 'title', 'content', 'status', 
            'project', 'project_name',
            'author', 'author_username', 'author_full_name',
            'tags', 'created_at', 'updated_at', 'published_at'
        ]
        read_only_fields = ['author', 'created_at', 'updated_at']
    
    def get_author_full_name(self, obj):
        """Retourne le nom complet de l'auteur"""
        return f"{obj.author.first_name} {obj.author.last_name}".strip() or obj.author.username
    
    def get_tags(self, obj):
        """Retourne la liste des tags"""
        note_tags = obj.note_tags.all()
        return [{'id': nt.tag.id, 'name': nt.tag.name} for nt in note_tags]


class NoteCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer pour la création et modification de notes
    """
    tags = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text="Liste des IDs de tags (max 10)"
    )
    
    class Meta:
        model = Note
        fields = ['id', 'title', 'content', 'status', 'project', 'tags', 'published_at']
        read_only_fields = ['id']
    
    def validate_tags(self, value):
        """Validation : maximum 10 tags"""
        if len(value) > 10:
            raise serializers.ValidationError("Maximum 10 tags par note")
        return value
    
    def validate_status(self, value):
        """Validation du statut lors de la publication"""
        if value == 'publie' and not self.instance:
            # Nouvelle note publiée directement
            return value
        return value
    
    def create(self, validated_data):
        """Création d'une note avec ses tags"""
        tags_data = validated_data.pop('tags', [])
        
        # Créer la note
        note = Note.objects.create(**validated_data)
        
        # Ajouter les tags
        for tag_id in tags_data:
            try:
                tag = Tag.objects.get(id=tag_id)
                NoteTag.objects.create(note=note, tag=tag)
            except Tag.DoesNotExist:
                pass  # Ignore les tags inexistants
        
        return note
    
    def update(self, instance, validated_data):
        """Mise à jour d'une note avec ses tags"""
        tags_data = validated_data.pop('tags', None)
        
        # Mettre à jour les champs de la note
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Mettre à jour les tags si fournis
        if tags_data is not None:
            # Supprimer les anciens tags
            instance.note_tags.all().delete()
            
            # Ajouter les nouveaux tags
            for tag_id in tags_data:
                try:
                    tag = Tag.objects.get(id=tag_id)
                    NoteTag.objects.create(note=instance, tag=tag)
                except Tag.DoesNotExist:
                    pass
        
        return instance