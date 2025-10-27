from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Comment
from .serializers import CommentSerializer, CommentWriteSerializer


class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les commentaires individuels
    Route principale : /api/comments/{id}/
    Pour les commentaires d'une note : /api/notes/{note_id}/comments/
    """
    permission_classes = [IsAuthenticated]
    queryset = Comment.objects.all()
    
    def get_serializer_class(self):
        """Choisir le serializer selon l'action"""
        if self.action in ['update', 'partial_update']:
            return CommentWriteSerializer
        return CommentSerializer
    
    def list(self, request, *args, **kwargs):
        """Liste désactivée - Utiliser /api/notes/{note_id}/comments/"""
        return Response({
            'message': 'Utilisez /api/notes/{note_id}/comments/ pour lister les commentaires d\'une note.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def create(self, request, *args, **kwargs):
        """Création désactivée - Utiliser /api/notes/{note_id}/comments/"""
        return Response({
            'message': 'Utilisez /api/notes/{note_id}/comments/ pour créer un commentaire.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        """Modifier un commentaire (auteur ou admin uniquement)"""
        comment = self.get_object()
        
        # Vérifier les permissions
        if request.user.profile.role != 'admin':
            if comment.author != request.user:
                return Response(
                    {'error': 'Vous ne pouvez modifier que vos propres commentaires.'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Marquer comme édité
        comment.is_edited = True
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """Supprimer un commentaire (auteur ou admin uniquement)"""
        comment = self.get_object()
        
        # Vérifier les permissions
        if request.user.profile.role != 'admin':
            if comment.author != request.user:
                return Response(
                    {'error': 'Vous ne pouvez supprimer que vos propres commentaires.'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        return super().destroy(request, *args, **kwargs)
    
    @action(detail=True, methods=['get'])
    def replies(self, request, pk=None):
        """Récupérer toutes les réponses d'un commentaire"""
        comment = self.get_object()
        replies = comment.replies.all()
        serializer = self.get_serializer(replies, many=True)
        return Response(serializer.data)