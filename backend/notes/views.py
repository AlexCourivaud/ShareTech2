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
    
    Permissions :
    - Liste/Détail : Tous les utilisateurs authentifiés (membres du projet)
    - Création : Tous les utilisateurs authentifiés
    - Modification : Auteur ou Senior+
    - Suppression : Auteur ou Senior+
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Retourne les notes accessibles par l'utilisateur
        - Notes des projets dont il est membre
        - Notes qu'il a créées
        """
        user = self.request.user
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
        
        # Vérifier les permissions : auteur ou Senior+
        if note.author != request.user:
            # Vérifier si Senior+
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
        
        # Vérifier les permissions : auteur ou Senior+
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