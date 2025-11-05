# backend/tasks/tests/conftest.py
"""
Fixtures locales pour les tests de l'app Tasks
Ces fixtures sont accessibles uniquement dans tasks/tests/
"""

import pytest
from tasks.models import Task


@pytest.fixture
def sample_task(sample_project, junior_user):
    """
    Crée une tâche de test basique (statut: ouverte, priorité: normale)
    Utilise sample_project (globale) et junior_user (globale)
    """
    return Task.objects.create(
        title='Test Task',
        description='Description de la tâche de test',
        status='ouverte',
        priority='normale',
        project=sample_project,
        created_by=junior_user
    )


@pytest.fixture
def assigned_task(sample_project, junior_user, senior_user):
    """
    Crée une tâche assignée à un utilisateur
    """
    return Task.objects.create(
        title='Assigned Task',
        description='Tâche assignée à senior_user',
        status='assignee',
        priority='haute',
        project=sample_project,
        created_by=junior_user,
        assigned_to=senior_user
    )


@pytest.fixture
def completed_task(sample_project, lead_user):
    """
    Crée une tâche terminée
    """
    from django.utils import timezone
    return Task.objects.create(
        title='Completed Task',
        description='Tâche terminée',
        status='terminee',
        priority='normale',
        project=sample_project,
        created_by=lead_user,
        assigned_to=lead_user,
        completed_date=timezone.now().date()
    )
