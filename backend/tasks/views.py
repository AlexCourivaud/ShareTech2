from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.contrib.auth.models import User

from .models import Task, TaskTag
from .serializers import TaskSerializer, AssignTaskSerializer


class TaskViewSet(viewsets.ModelViewSet):
    """ViewSet pour gérer les tâches"""
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer  # ✅ Un seul serializer pour tout le CRUD
    
    def get_queryset(self):
        """
        Retourne les tâches accessibles selon le rôle :
        - Junior/Senior : Ses tâches assignées + tâches ouvertes (non assignées)
        - Lead+ : Toutes les tâches
        """
        user = self.request.user
        queryset = Task.objects.all()
        
        # Filtrage par projet si paramètre fourni
        project_id = self.request.query_params.get('project', None)
        if project_id is not None:
            queryset = queryset.filter(project_id=project_id)
            # Si filtré par projet, retourner toutes les tâches du projet
            return queryset
        
        # Sans filtre projet : permissions selon rôle
        if user.is_superuser or user.profile.role in ['lead', 'admin']:
            return queryset
        
        # Junior/Senior : leurs tâches + ouvertes
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
        """Supprimer une tâche (Lead+ uniquement)"""
        if not request.user.is_superuser and request.user.profile.role not in ['lead', 'admin']:
            return Response(
                {'error': 'Seuls les Lead+ peuvent supprimer des tâches.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return super().destroy(request, *args, **kwargs)
    
    # ===== ACTIONS MÉTIER =====
    
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """Assigner une tâche à un utilisateur (Lead+ uniquement)"""
        if not request.user.is_superuser and request.user.profile.role not in ['lead', 'admin']:
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
            task.status = 'assignee'
            task.save()
            
            return Response({
                'message': f'Tâche assignée à {user.username}',
                'task': TaskSerializer(task).data
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def unassign(self, request, pk=None):
        """Retirer l'assignation d'une tâche (Lead+ uniquement)"""
        if not request.user.is_superuser and request.user.profile.role not in ['lead', 'admin']:
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
        task.status = 'ouverte'
        task.save()
        
        return Response({
            'message': 'Assignation retirée',
            'task': TaskSerializer(task).data
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
                    {'error': 'Seul l\'assigné ou Lead+ peut changer le statut.'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Si on passe à "terminee", ajouter la date de complétion
        if new_status == 'terminee' and task.status != 'terminee':
            from django.utils import timezone
            task.completed_date = timezone.now().date()
        
        task.status = new_status
        task.save()
        
        return Response({
            'message': f'Statut changé en "{new_status}"',
            'task': TaskSerializer(task).data
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def my_tasks(self, request):
        """Récupérer uniquement les tâches assignées à l'utilisateur connecté"""
        tasks = Task.objects.filter(assigned_to=request.user)
        serializer = self.get_serializer(tasks, many=True)
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
        
        tasks = self.get_queryset().filter(project_id=project_id)
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)