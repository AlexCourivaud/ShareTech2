from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Comment
from .serializers import CommentSerializer, CommentWriteSerializer


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet pour gérer les commentaires individuels"""
    permission_classes = [IsAuthenticated]
    queryset = Comment.objects.all()
    
    def get_serializer_class(self):
        """Choisir le serializer selon l'action"""
        if self.action in ['update', 'partial_update', 'reply']:
            return CommentWriteSerializer
        return CommentSerializer
    
    def list(self, request, *args, **kwargs):
        """
        Liste des commentaires
        """
        return Response({
            'message': 'Utilisez /api/notes/{note_id}/comments/ pour lister les commentaires d\'une note.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def create(self, request, *args, **kwargs):
        """
        Création de commentaire désactivée
        """
        return Response({
            'message': 'Utilisez /api/notes/{note_id}/comments/ pour créer un commentaire.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        """
        Modifier un commentaire
        """
        comment = self.get_object()
        
        if request.user.profile.role != 'admin':
            if comment.author != request.user:
                return Response(
                    {'error': 'Vous ne pouvez modifier que vos propres commentaires.'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        serializer = self.get_serializer(comment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(is_edited=True)
            return Response(CommentSerializer(comment).data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        """
        Supprimer un commentaire
        """
        comment = self.get_object()
        
        if request.user.profile.role != 'admin':
            if comment.author != request.user:
                return Response(
                    {'error': 'Vous ne pouvez supprimer que vos propres commentaires.'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        return super().destroy(request, *args, **kwargs)
    
    @action(detail=True, methods=['post'])
    def reply(self, request, pk=None):
        """
        Répondre à un commentaire
        """
        parent_comment = self.get_object()
        
        serializer = CommentWriteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(
                author=request.user,
                note=parent_comment.note,
                parent_comment=parent_comment
            )
            
            return Response(
                CommentSerializer(serializer.instance).data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)