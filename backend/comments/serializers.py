from rest_framework import serializers
from .models import Comment
from accounts.serializers import UserSerializer


class CommentSerializer(serializers.ModelSerializer):
    """Serializer récursif pour afficher les commentaires avec leurs réponses"""
    author = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = [
            'id', 'content', 'author', 'parent_comment', 
            'is_edited', 'created_at', 'updated_at', 'replies'
        ]
        read_only_fields = ['id', 'author', 'is_edited', 'created_at', 'updated_at']
    
    def get_replies(self, obj):
        """Récupérer récursivement toutes les réponses"""
        if obj.replies.exists():
            return CommentSerializer(obj.replies.all(), many=True).data
        return []


class CommentWriteSerializer(serializers.ModelSerializer):
    """Serializer pour créer/modifier un commentaire"""
    
    class Meta:
        model = Comment
        fields = [ 'content', 'parent_comment']  
    
    def validate_content(self, value):
        """Validation minimale : juste non vide"""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("Le commentaire ne peut pas être vide.")
        return value
