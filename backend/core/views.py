from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Project, Note, Comment, Tag, NoteFavorite
from .serializers import ProjectSerializer, NoteSerializer, CommentSerializer, TagSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    """ViewSet pour gérer les projets"""
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    
    def perform_create(self, serializer):
        """Définir l'utilisateur connecté comme créateur du projet"""
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['get'])
    def notes(self, request, pk=None):
        """Récupérer les notes d'un projet"""
        project = self.get_object()
        notes = Note.objects.filter(project=project)
        serializer = NoteSerializer(notes, many=True, context={'request': request})
        return Response(serializer.data)


class NoteViewSet(viewsets.ModelViewSet):
    """ViewSet pour gérer les notes"""
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    
    def perform_create(self, serializer):
        """Définir l'utilisateur connecté comme auteur de la note"""
        serializer.save(author=self.request.user)
    
    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk=None):
        """Ajouter/retirer une note des favoris"""
        note = self.get_object()
        favorite, created = NoteFavorite.objects.get_or_create(
            user=request.user, 
            note=note
        )
        
        if request.method == 'POST':
            if created:
                return Response({'status': 'added to favorites'})
            return Response({'status': 'already in favorites'})
        
        elif request.method == 'DELETE':
            favorite.delete()
            return Response({'status': 'removed from favorites'})


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet pour gérer les commentaires"""
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    
    def perform_create(self, serializer):
        """Définir l'utilisateur connecté comme auteur du commentaire"""
        serializer.save(author=self.request.user)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour consulter les tags"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer