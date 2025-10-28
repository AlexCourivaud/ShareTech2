from rest_framework import serializers
from .models import Note, NoteTag
from tags.models import Tag


class NoteSerializer(serializers.ModelSerializer):
    """
    Serializer unique pour toutes les opérations sur les notes
    """
    author_username = serializers.CharField(source='author.username', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        required=False
    )
    
    class Meta:
        model = Note
        fields = [
            'id', 'title', 'content', 'status', 'project', 'project_name',
            'author', 'author_username', 'tags', 'created_at', 'updated_at'
        ]
        read_only_fields = ['author', 'project', 'created_at', 'updated_at'] 
           
    def validate_tags(self, value):
        """Validation : maximum 10 tags"""
        if len(value) > 10:
            raise serializers.ValidationError("Maximum 10 tags par note")
        return value
    
    def create(self, validated_data):
        """Création d'une note avec ses tags"""
        tags_data = validated_data.pop('tags', [])
        validated_data['title'] = validated_data['title'].capitalize()

        
        # Créer la note
        note = Note.objects.create(**validated_data)
        
        # Assigner les tags
        for tag in tags_data:
            NoteTag.objects.create(note=note, tag=tag)
        
        return note
    
    def update(self, instance, validated_data):
        """Mise à jour d'une note avec ses tags"""
        tags_data = validated_data.pop('tags', None)
        
        # Mettre à jour les champs de base
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Gérer les tags si fournis
        if tags_data is not None:
            instance.note_tags.all().delete()
            for tag in tags_data:
                NoteTag.objects.create(note=instance, tag=tag)
        
        return instance