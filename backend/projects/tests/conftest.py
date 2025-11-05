# backend/projects/tests/conftest.py
"""
Fixtures locales pour les tests de l'app Projects
Ces fixtures sont accessibles uniquement dans projects/tests/

Note : sample_project a été déplacée vers backend/conftest.py (global)
car elle est utilisée par plusieurs apps (notes, tasks, comments)
"""

import pytest
from projects.models import Project, ProjectMember


@pytest.fixture
def active_project(lead_user):
    """
    Crée un projet actif (is_active=True)
    """
    return Project.objects.create(
        name='Active Project',
        description='Projet actif pour les tests',
        created_by=lead_user,
        is_active=True
    )


@pytest.fixture
def terminated_project(lead_user):
    """
    Crée un projet terminé (is_active=False)
    """
    project = Project.objects.create(
        name='Terminated Project',
        description='Projet terminé pour les tests',
        created_by=lead_user
    )
    project.terminate()  # Utilise la méthode pour passer is_active à False
    return project


@pytest.fixture
def project_with_members(sample_project, junior_user, senior_user):
    """
    Crée un projet avec plusieurs membres
    Utilise sample_project (local) + junior_user et senior_user (globales)
    """
    ProjectMember.objects.create(project=sample_project, user=junior_user)
    ProjectMember.objects.create(project=sample_project, user=senior_user)
    return sample_project
