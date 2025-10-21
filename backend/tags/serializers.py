from rest_framework import serializers
from .models import Tag


class TagSerializer(serializers.ModelSerializer):
    """
    Serializer pour les Tags
    Lecture seule - pas de création via API
    """
    
    class Meta:
        model = Tag
        fields = ['id', 'name', 'created_at']
        read_only_fields = ['id', 'name', 'created_at']