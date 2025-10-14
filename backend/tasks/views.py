from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.contrib.auth.models import User

from .models import Task, TaskTag
from .serializers import (
    TaskListSerializer,
    TaskDetailSerializer,
    TaskCreateUpdateSerializer,
    AssignTaskSerializer
)
from accounts.permissions import IsLeadOrAdmin

class TaskViewSet(viewsets.ModelViewSet):
    """ViewSet pour gérer les tâches"""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Retourne les tâches accessibles selon le rôle :
        - Junior/Senior : Ses tâches assignées + tâches ouvertes (non assignées)
        - Lead+ : Toutes les tâches
        """
        user = self.request.user
        
        # Lead+ : accès à toutes les tâches
        if user.profile.role in ['lead', 'admin']:
            return Task.objects.all()
        
        # Junior/Senior : ses tâches + tâches ouvertes
        return Task.objects.filter(
            Q(assigned_to=user) |  # Ses tâches assignées
            Q(assigned_to__isnull=True)  # Tâches non assignées
        ).distinct()
    
    def get_serializer_class(self):
        """Choisir le serializer selon l'action"""
        if self.action == 'list':
            return TaskListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return TaskCreateUpdateSerializer
        else:
            return TaskDetailSerializer
    
    def perform_create(self, serializer):
        """Créer la tâche avec created_by = utilisateur connecté"""
        serializer.save(created_by=self.request.user)
    
    def update(self, request, *args, **kwargs):
        """
        Modifier une tâche
        Permissions : Lead+ peut tout modifier, autres ne peuvent modifier que leurs tâches
        """
        task = self.get_object()
        
        # Vérifier les permissions
        if request.user.profile.role not in ['lead', 'admin']:
            # Junior/Senior ne peuvent modifier que leurs tâches assignées
            if task.assigned_to != request.user:
                return Response(
                    {'error': 'Vous ne pouvez modifier que vos propres tâches.'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """
        Supprimer une tâche
        Permissions : Seulement Lead+
        """
        if request.user.profile.role not in ['lead', 'admin']:
            return Response(
                {'error': 'Seuls les Lead+ peuvent supprimer des tâches.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return super().destroy(request, *args, **kwargs)
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """
        Assigner une tâche à un utilisateur
        Permissions : Lead+ uniquement
        """
        if request.user.profile.role not in ['lead', 'admin']:
            return Response(
                {'error': 'Seuls les Lead+ peuvent assigner des tâches.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        task = self.get_object()
        serializer = AssignTaskSerializer(data=request.data)
        
        if serializer.is_valid():
            user_id = serializer.validated_data['user_id']
            user = User.objects.get(id=user_id)
            
            task.assigned_to = user
            task.status = 'assignee'  # Changer le statut automatiquement
            task.save()
            
            return Response({
                'message': f'Tâche assignée à {user.username}',
                'task': TaskDetailSerializer(task).data
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def unassign(self, request, pk=None):
        """
        Retirer l'assignation d'une tâche
        Permissions : Lead+ uniquement
        """
        if request.user.profile.role not in ['lead', 'admin']:
            return Response(
                {'error': 'Seuls les Lead+ peuvent désassigner des tâches.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        task = self.get_object()
        
        if task.assigned_to is None:
            return Response(
                {'error': 'Cette tâche n\'est pas assignée.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        task.assigned_to = None
        task.status = 'ouverte'  # Retour au statut "ouverte"
        task.save()
        
        return Response({
            'message': 'Assignation retirée',
            'task': TaskDetailSerializer(task).data
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def change_status(self, request, pk=None):
        """
        Changer le statut d'une tâche
        Permissions : Assigné peut changer son statut, Lead+ peut tout changer
        """
        task = self.get_object()
        new_status = request.data.get('status')
        
        # Vérifier que le statut est valide
        valid_statuses = ['ouverte', 'assignee', 'terminee']
        if new_status not in valid_statuses:
            return Response(
                {'error': f'Statut invalide. Valeurs possibles : {valid_statuses}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Vérifier les permissions
        if request.user.profile.role not in ['lead', 'admin']:
            # L'utilisateur doit être assigné à la tâche
            if task.assigned_to != request.user:
                return Response(
                    {'error': 'Seul l\'assigné ou Lead+ peut changer le statut.'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Logique métier : si on passe à "terminee", ajouter la date de complétion
        if new_status == 'terminee' and task.status != 'terminee':
            from django.utils import timezone
            task.completed_date = timezone.now().date()
        
        task.status = new_status
        task.save()
        
        return Response({
            'message': f'Statut changé en "{new_status}"',
            'task': TaskDetailSerializer(task).data
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def my_tasks(self, request):
        """
        Récupérer uniquement les tâches assignées à l'utilisateur connecté
        """
        tasks = Task.objects.filter(assigned_to=request.user)
        serializer = TaskListSerializer(tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_project(self, request):
        """
        Filtrer les tâches par projet
        Query param : ?project_id=1
        """
        project_id = request.query_params.get('project_id')
        
        if not project_id:
            return Response(
                {'error': 'Le paramètre project_id est requis.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Récupérer les tâches selon les permissions
        user = request.user
        if user.profile.role in ['lead', 'admin']:
            tasks = Task.objects.filter(project_id=project_id)
        else:
            tasks = Task.objects.filter(
                project_id=project_id
            ).filter(
                Q(assigned_to=user) | Q(assigned_to__isnull=True)
            )
        
        serializer = TaskListSerializer(tasks, many=True)
        return Response(serializer.data)