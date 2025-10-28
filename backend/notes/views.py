from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from .models import Note
from .serializers import NoteSerializer


class NoteViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les notes
    
    Permissions :
    - Liste/Détail : Tous les utilisateurs authentifiés
    - Création : Tous les utilisateurs authentifiés
    - Modification : Auteur ou Senior+
    - Suppression : Auteur ou Admin
    """
    permission_classes = [IsAuthenticated]
    serializer_class = NoteSerializer
    
    def get_queryset(self):
        """
        Retourne les notes accessibles par l'utilisateur
        """
        user = self.request.user
        return Note.objects.filter(
            Q(project__members__user=user) | Q(author=user)
        ).distinct().select_related('author', 'project').prefetch_related('note_tags__tag')
    
    def perform_create(self, serializer):
        """Définit automatiquement l'auteur lors de la création"""
        serializer.save(author=self.request.user)
    
    def update(self, request, *args, **kwargs):
        """Mise à jour d'une note - Vérifie les permissions"""
        note = self.get_object()
        
        # Vérifier : auteur ou Senior+
        if note.author != request.user:
            user_role = request.user.profile.role
            if user_role not in ['senior', 'lead', 'admin']:
                return Response(
                    {'detail': 'Vous ne pouvez modifier que vos propres notes.'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """Suppression d'une note - Vérifie les permissions"""
        note = self.get_object()
        
        # Vérifier : auteur ou Admin
        if note.author != request.user:
            if request.user.profile.role != 'admin':
                return Response(
                    {'detail': 'Seul l\'auteur ou un admin peut supprimer cette note.'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        return super().destroy(request, *args, **kwargs)
    
    @action(detail=False, methods=['get'])
    def my_notes(self, request):
        """Retourne uniquement les notes de l'utilisateur connecté"""
        notes = self.get_queryset().filter(author=request.user)
        serializer = self.get_serializer(notes, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_project(self, request):
        """Filtre les notes par projet"""
        project_id = request.query_params.get('project')
        if not project_id:
            return Response(
                {'error': 'Paramètre project requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        notes = self.get_queryset().filter(project_id=project_id)
        serializer = self.get_serializer(notes, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Recherche full-text dans les notes"""
        query = request.query_params.get('q', '')
        if len(query) < 2:
            return Response(
                {'error': 'Requête trop courte (min 2 caractères)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        notes = self.get_queryset().filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )
        serializer = self.get_serializer(notes, many=True)
        return Response(serializer.data)
    

    @action(detail=True, methods=['get', 'post'])
    def comments(self, request, pk=None):
        """
        GET  /api/notes/{id}/comments/  - Liste les commentaires racines
        POST /api/notes/{id}/comments/  - Créer un commentaire
        """
        note = self.get_object()
        
        if request.method == 'GET':
            from comments.models import Comment
            from comments.serializers import CommentSerializer
            
            # Récupérer uniquement les commentaires racines (sans parent)
            comments = Comment.objects.filter(note=note, parent_comment__isnull=True)
            serializer = CommentSerializer(comments, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            from comments.models import Comment
            from comments.serializers import CommentWriteSerializer, CommentSerializer
            
            serializer = CommentWriteSerializer(data=request.data)
            if serializer.is_valid():
                comment = serializer.save(author=request.user, note=note)
                return Response(
                    CommentSerializer(comment).data,
                    status=status.HTTP_201_CREATED
                )
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)