from rest_framework import serializers
from .models import Note, NoteTag
from tags.models import Tag


class NoteSerializer(serializers.ModelSerializer):
    """Serializer pour lecture (liste/détail)"""
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
        if len(value) > 10:
            raise serializers.ValidationError("Maximum 10 tags par note")
        return value


class NoteCreateSerializer(serializers.ModelSerializer):
    """Serializer pour création (project en écriture)"""
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        required=False
    )
    
    class Meta:
        model = Note
        fields = ['title', 'content', 'status', 'project', 'tags']
   
    def create(self, validated_data):
        print("🔍 DEBUG - validated_data:", validated_data)  
        tags_data = validated_data.pop('tags', [])
        validated_data['title'] = validated_data['title']
        note = Note.objects.create(**validated_data)
        for tag in tags_data:
            NoteTag.objects.create(note=note, tag=tag)
        return note


class NoteUpdateSerializer(serializers.ModelSerializer):
    """Serializer pour modification (project en read_only)"""
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        required=False
    )
    
    class Meta:
        model = Note
        fields = ['title', 'content', 'status', 'tags']
        # project n'est pas dans fields → on ne peut pas le modifier
    
    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if tags_data is not None:
            instance.note_tags.all().delete()
            for tag in tags_data:
                NoteTag.objects.create(note=instance, tag=tag)
        return instance