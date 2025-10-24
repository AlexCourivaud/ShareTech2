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
    permission_classes = [IsAuthenticated]
    serializer_class = TaskDetailSerializer
    
    def get_queryset(self):
        user = self.request.user
        queryset = Task.objects.all()
        
        # Filtrage par projet
        project_id = self.request.query_params.get('project', None)
        if project_id is not None:
            queryset = queryset.filter(project_id=project_id)
            # Si filtré par projet, retourner TOUTES les tâches du projet
            # (pour que les membres voient toutes les tâches)
            return queryset
        
        # Sans filtre projet : permissions selon rôle
        if user.is_superuser or user.profile.role in ['lead', 'admin']:
            return queryset
        
        # Junior/Senior sans filtre projet : leurs tâches + ouvertes
        return queryset.filter(
            Q(assigned_to=user) | Q(assigned_to__isnull=True)
        ).distinct()
    
    def perform_create(self, serializer):
        """Créer la tâche avec created_by = utilisateur connecté"""
        serializer.save(created_by=self.request.user)
    
    def update(self, request, *args, **kwargs):
        """Modifier une tâche"""
        task = self.get_object()
        
        # Vérifier les permissions
        if not request.user.is_superuser and request.user.profile.role not in ['lead', 'admin']:
            # Junior/Senior ne peuvent modifier que leurs tâches assignées
            if task.assigned_to != request.user:
                return Response(
                    {'error': 'Vous ne pouvez modifier que vos propres tâches.'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """Supprimer une tâche"""
        if not request.user.is_superuser and request.user.profile.role not in ['lead', 'admin']:
            return Response(
                {'error': 'Vous ne pouvez pas supprimer de tâches.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return super().destroy(request, *args, **kwargs)
    
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """Assigner une tâche à un utilisateur"""
        if not request.user.is_superuser and request.user.profile.role not in ['lead', 'admin']:
            return Response(
                {'error': 'Vous ne pouvez pas assigner de tâches.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        task = self.get_object()
        serializer = AssignTaskSerializer(data=request.data)
        
        if serializer.is_valid():
            user_id = serializer.validated_data['user_id']
            user = User.objects.get(id=user_id)
            
            task.assigned_to = user
            task.status = 'assignee'
            task.save()
            
            return Response({
                'message': f'Tâche assignée à {user.username}',
                'task': TaskDetailSerializer(task).data
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def unassign(self, request, pk=None):
        """Retirer l'assignation d'une tâche"""
        if not request.user.is_superuser and request.user.profile.role not in ['lead', 'admin']:
            return Response(
                {'error': 'Vous ne pouvez désassigner de tâches.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        task = self.get_object()
        
        if task.assigned_to is None:
            return Response(
                {'error': 'Cette tâche n\'est pas assignée.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        task.assigned_to = None
        task.status = 'ouverte'
        task.save()
        
        return Response({
            'message': 'Assignation retirée',
            'task': TaskDetailSerializer(task).data
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def change_status(self, request, pk=None):
        """Changer le statut d'une tâche"""
        task = self.get_object()
        new_status = request.data.get('status')
        
        valid_statuses = ['ouverte', 'assignee', 'terminee']
        if new_status not in valid_statuses:
            return Response(
                {'error': f'Statut invalide. Valeurs possibles : {valid_statuses}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Vérifier les permissions
        if not request.user.is_superuser and request.user.profile.role not in ['lead', 'admin']:
            if task.assigned_to != request.user:
                return Response(
                    {'error': 'Vous ne pouvez changer le statut.'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Si terminée, ajouter date de complétion
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
        Récupérer les tâches accessibles
        - Superuser : TOUTES les tâches
        - Autres : Seulement leurs tâches assignées
        """
        if request.user.is_superuser:
            tasks = Task.objects.all()
        else:
            tasks = Task.objects.filter(assigned_to=request.user)
        
        serializer = TaskListSerializer(tasks, many=True)
        return Response(serializer.data)