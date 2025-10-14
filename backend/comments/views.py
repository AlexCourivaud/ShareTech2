from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import Comment
from .serializers import CommentSerializer, CommentWriteSerializer
from notes.models import Note


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet pour gérer les commentaires"""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Retourne les commentaires accessibles
        Filtrés par note si ?note_id fourni
        """
        queryset = Comment.objects.all()
        
        # Filtrer par note
        note_id = self.request.query_params.get('note_id')
        if note_id:
            queryset = queryset.filter(note_id=note_id, parent_comment__isnull=True)
        
        return queryset
    
    def get_serializer_class(self):
        """Choisir le serializer selon l'action"""
        if self.action in ['create', 'update', 'partial_update']:
            return CommentWriteSerializer
        return CommentSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Créer un commentaire sur une note
        Body : {
            "note_id": 1,
            "content": "Mon commentaire",
            "parent_comment": null (ou ID du parent)
        }
        """
        note_id = request.data.get('note_id')
        
        if not note_id:
            return Response(
                {'error': 'Le champ note_id est requis.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Vérifier que la note existe
        note = get_object_or_404(Note, id=note_id)
        
        # Vérifier que l'utilisateur a accès à cette note (membre du projet ou Senior+)
        user = request.user
        if user.profile.role not in ['senior', 'lead', 'admin']:
            if not note.project.members.filter(user=user).exists():
                return Response(
                    {'error': 'Vous n\'avez pas accès à cette note.'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Sauvegarder avec l'auteur et la note
            serializer.save(author=request.user, note=note)
            return Response(
                CommentSerializer(serializer.instance).data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        """
        Modifier un commentaire
        Permissions : Auteur uniquement ou Senior+
        """
        comment = self.get_object()
        
        # Vérifier les permissions
        if request.user.profile.role not in ['senior', 'lead', 'admin']:
            if comment.author != request.user:
                return Response(
                    {'error': 'Vous ne pouvez modifier que vos propres commentaires.'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Forcer partial=True pour éviter de perdre des données
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """
        Supprimer un commentaire
        Permissions : Auteur uniquement ou Senior+
        """
        comment = self.get_object()
        
        # Vérifier les permissions
        if request.user.profile.role not in ['senior', 'lead', 'admin']:
            if comment.author != request.user:
                return Response(
                    {'error': 'Vous ne pouvez supprimer que vos propres commentaires.'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        return super().destroy(request, *args, **kwargs)
    
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """Liker un commentaire"""
        comment = self.get_object()
        comment.like_count += 1
        comment.save()
        
        return Response({
            'message': 'Commentaire liké',
            'like_count': comment.like_count
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def by_note(self, request):
        """
        Récupérer tous les commentaires d'une note (avec hiérarchie)
        Query param : ?note_id=1
        """
        note_id = request.query_params.get('note_id')
        
        if not note_id:
            return Response(
                {'error': 'Le paramètre note_id est requis.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Vérifier que la note existe
        note = get_object_or_404(Note, id=note_id)
        
        # Vérifier les permissions d'accès à la note
        user = request.user
        if user.profile.role not in ['senior', 'lead', 'admin']:
            if not note.project.members.filter(user=user).exists():
                return Response(
                    {'error': 'Vous n\'avez pas accès à cette note.'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Récupérer seulement les commentaires de niveau 1 (sans parent)
        comments = Comment.objects.filter(note=note, parent_comment__isnull=True)
        serializer = CommentSerializer(comments, many=True)
        
        return Response(serializer.data)