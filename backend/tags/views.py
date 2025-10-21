# from django.shortcuts import render

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Tag
from .serializers import TagSerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet pour les Tags (lecture seule)
    
    Endpoints disponibles :
    - GET /api/tags/ : Liste de tous les tags
    - GET /api/tags/{id}/ : Détail d'un tag
    
    Pas de création/modification/suppression via API
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]