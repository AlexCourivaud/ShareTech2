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
    
    # mise à jour du commentaire
    def update(self, request, *args, **kwargs):
        """Modifier un commentaire"""
        comment = self.get_object()
        
        # Vérifier les permissions : auteur ou Senior
        if comment.author != request.user:
            user_role = request.user.profile.role
            if user_role not in ['senior', 'lead', 'admin']:
                return Response(
                    {'error': 'Seul l\'auteur ou un Senior+ peut modifier ce commentaire.'},
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
    @action(detail=True, methods=['get', 'post'])
    def replies(self, request, pk=None):
        """
        GET  /api/comments/{id}/replies/  - Récupérer toutes les réponses
        POST /api/comments/{id}/replies/  - Créer une nouvelle réponse
        """
        parent_comment = self.get_object()
        
        if request.method == 'GET':
            replies = parent_comment.replies.all()
            serializer = self.get_serializer(replies, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            serializer = CommentWriteSerializer(data=request.data)
            if serializer.is_valid():
                reply = serializer.save(
                    author=request.user,
                    note=parent_comment.note,
                    parent_comment=parent_comment
                )
                return Response(
                    CommentSerializer(reply).data,
                    status=status.HTTP_201_CREATED
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)