from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from .models import Note, NoteTag
from .serializers import (
    NoteListSerializer,
    NoteDetailSerializer,
    NoteCreateUpdateSerializer
)


class NoteViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les notes
    - Liste/Détail 
    - Création 
    - Modification 
    - Suppression 
    """
    permission_classes = [IsAuthenticated]
        
    def get_queryset(self):
        user = self.request.user
        
        # Superuser
        if user.is_superuser:
            return Note.objects.all().select_related('author', 'project').prefetch_related('note_tags__tag')
        
        return Note.objects.filter(
            Q(project__members__user=user) | Q(author=user)
        ).distinct().select_related('author', 'project').prefetch_related('note_tags__tag')
    

    def get_serializer_class(self):
        """
        Utilise différents serializers selon l'action
        """
        if self.action == 'list':
            return NoteListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return NoteCreateUpdateSerializer
        else:
            return NoteDetailSerializer
    
    def perform_create(self, serializer):
        """
        Définit automatiquement l'auteur lors de la création
        """
        serializer.save(author=self.request.user)
    
    def update(self, request, *args, **kwargs):
        """
        Mise à jour d'une note (PUT/PATCH)
        Vérifie que l'utilisateur peut modifier
        """
        note = self.get_object()
        
        # Vérifier les permissions : auteur ou Senior et +
        if note.author != request.user:
            # Vérifier si Senior et +
            user_role = request.user.profile.role
            if user_role not in ['senior', 'lead', 'admin']:
                return Response(
                    {'detail': 'Vous ne pouvez modifier que vos propres notes.'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """
        Suppression d'une note
        Vérifie que l'utilisateur peut supprimer
        """
        note = self.get_object()
        
        # Vérifier les permissions : auteur ou Senior et +
        if note.author != request.user:
            user_role = request.user.profile.role
            if user_role not in ['senior', 'lead', 'admin']:
                return Response(
                    {'detail': 'Vous ne pouvez supprimer que vos propres notes.'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        return super().destroy(request, *args, **kwargs)
    
    @action(detail=False, methods=['get'])
    def my_notes(self, request):
        """
        GET /api/notes/my_notes/
        Retourne uniquement les notes créées par l'utilisateur
        """
        notes = Note.objects.filter(author=request.user).select_related('author', 'project')
        serializer = NoteListSerializer(notes, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_project(self, request):
        """
        GET /api/notes/by_project/?project_id=1
        Retourne les notes d'un projet spécifique
        """
        project_id = request.query_params.get('project_id')
        
        if not project_id:
            return Response(
                {'detail': 'project_id requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        notes = self.get_queryset().filter(project_id=project_id)
        serializer = NoteListSerializer(notes, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        GET /api/notes/search/?q=python
        Recherche dans les titres et contenus
        """
        query = request.query_params.get('q', '')
        
        if not query:
            return Response(
                {'detail': 'Paramètre q requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        notes = self.get_queryset().filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )
        serializer = NoteListSerializer(notes, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get', 'post'])
    def comments(self, request, pk=None):
        """
        GET  /api/notes/{id}/comments/  - Liste les commentaires
        POST /api/notes/{id}/comments/  - Créer un commentaire
        """
        note = self.get_object()
        
        if request.method == 'GET':
            from comments.models import Comment
            from comments.serializers import CommentSerializer
            
            comments = Comment.objects.filter(note=note, parent_comment__isnull=True)
            serializer = CommentSerializer(comments, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            from comments.models import Comment
            from comments.serializers import CommentWriteSerializer
            
            serializer = CommentWriteSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(author=request.user, note=note)
                
                from comments.serializers import CommentSerializer
                return Response(
                    CommentSerializer(serializer.instance).data,
                    status=status.HTTP_201_CREATED
                )
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)