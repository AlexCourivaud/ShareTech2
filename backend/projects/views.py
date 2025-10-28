from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.db.models import Q 

from .models import Project, ProjectMember
from .serializers import (
    ProjectListSerializer,
    ProjectDetailSerializer,
    ProjectCreateSerializer,
    ProjectMemberSerializer,
    AddMemberSerializer
)
from accounts.permissions import IsLeadOrAdmin


class ProjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les projets
    - Liste/Détail
    - Création
    - Modification
    - Suppression
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        # Superuser voit tout
        if user.is_superuser:
            return Project.objects.all()
        
        return Project.objects.filter(
            Q(members__user=user) | Q(created_by=user)
        ).distinct()
    
    def get_serializer_class(self):
        """
        Utilise différents serializers selon l'action
        """
        if self.action == 'list':
            return ProjectListSerializer
        elif self.action == 'create':
            return ProjectCreateSerializer
        else:
            return ProjectDetailSerializer
    
    def get_permissions(self):
        """
        Permissions spécifiques par action
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsLeadOrAdmin]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """
        Crée un projet et ajoute automatiquement le créateur comme membre
        """
        project = serializer.save(created_by=self.request.user)
        # Ajouter le créateur comme membre du projet
        ProjectMember.objects.create(project=project, user=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsLeadOrAdmin], serializer_class=AddMemberSerializer)
    def add_member(self, request, pk=None):
        """
        Ajoute un membre au projet
        
        POST /api/projects/{id}/add_member/
        Body: {"user_id": 2}
        """
        project = self.get_object()
        serializer = AddMemberSerializer(data=request.data)
        
        if serializer.is_valid():
            user_id = serializer.validated_data['user_id']
            user = User.objects.get(id=user_id)
            
            try:
                # Créer l'affiliation
                member = ProjectMember.objects.create(project=project, user=user)
                member_serializer = ProjectMemberSerializer(member)
                return Response(
                    {
                        'message': f'{user.username} a été ajouté au projet',
                        'member': member_serializer.data
                    },
                    status=status.HTTP_201_CREATED
                )
            except IntegrityError:
                return Response(
                    {'error': 'Cet utilisateur est déjà membre du projet'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsLeadOrAdmin])
    def remove_member(self, request, pk=None):
        """
        Retire un membre du projet
        
        POST /api/projects/{id}/remove_member/
        Body: {"user_id": 2}
        """
        project = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response(
                {'error': 'user_id est requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            member = ProjectMember.objects.get(project=project, user_id=user_id)
            username = member.user.username
            member.delete()
            
            return Response(
                {'message': f'{username} a été retiré du projet'},
                status=status.HTTP_200_OK
            )
        except ProjectMember.DoesNotExist:
            return Response(
                {'error': 'Cet utilisateur n\'est pas membre du projet'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsLeadOrAdmin])
    def terminate(self, request, pk=None):
        """
        Termine un projet (is_active = False)
        
        POST /api/projects/{id}/terminate/
        """
        project = self.get_object()
        
        if not project.is_active:
            return Response(
                {'error': 'Ce projet est déjà terminé'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        project.terminate()
        
        return Response(
            {'message': f'Le projet {project.name} a été marqué comme terminé'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        """
        Liste les membres d'un projet
        
        GET /api/projects/{id}/members/
        """
        project = self.get_object()
        members = project.members.all()
        serializer = ProjectMemberSerializer(members, many=True)
        return Response(serializer.data)