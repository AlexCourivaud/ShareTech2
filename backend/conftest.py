# backend/conftest.py
"""
Fixtures globales pour les tests ShareTech
Ces fixtures sont accessibles dans TOUS les tests du projet
"""

import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from tags.models import Tag


# ===== FIXTURES USERS (utilisées dans toutes les apps) =====

@pytest.fixture
def junior_user():
    """
    Crée un utilisateur avec le rôle Junior
    Utilisé pour tester les permissions limitées
    """
    user = User.objects.create_user(
        username='juniortest',
        email='junior@test.com',
        password='testpass123'
    )
    user.profile.role = 'junior'
    user.profile.save()
    return user


@pytest.fixture
def senior_user():
    """
    Crée un utilisateur avec le rôle Senior
    Utilisé pour tester les permissions intermédiaires
    """
    user = User.objects.create_user(
        username='seniortest',
        email='senior@test.com',
        password='testpass123'
    )
    user.profile.role = 'senior'
    user.profile.save()
    return user


@pytest.fixture
def lead_user():
    """
    Crée un utilisateur avec le rôle Lead
    Utilisé pour tester les permissions élevées (création de projets, etc.)
    """
    user = User.objects.create_user(
        username='leadtest',
        email='lead@test.com',
        password='testpass123'
    )
    user.profile.role = 'lead'
    user.profile.save()
    return user


@pytest.fixture
def admin_user():
    """
    Crée un utilisateur avec le rôle Admin
    Utilisé pour tester les permissions maximales
    """
    user = User.objects.create_user(
        username='admintest',
        email='admin@test.com',
        password='testpass123'
    )
    user.profile.role = 'admin'
    user.profile.save()
    return user


# ===== FIXTURES API CLIENT (utilisées pour tester les endpoints) =====

@pytest.fixture
def api_client():
    """
    Crée un client API pour tester les endpoints
    Non authentifié par défaut
    """
    return APIClient()


@pytest.fixture
def authenticated_junior_client(api_client, junior_user):
    """
    Client API authentifié en tant que Junior
    """
    api_client.force_authenticate(user=junior_user)
    return api_client


@pytest.fixture
def authenticated_lead_client(api_client, lead_user):
    """
    Client API authentifié en tant que Lead
    """
    api_client.force_authenticate(user=lead_user)
    return api_client


@pytest.fixture
def authenticated_admin_client(api_client, admin_user):
    """
    Client API authentifié en tant qu'Admin
    """
    api_client.force_authenticate(user=admin_user)
    return api_client


# ===== FIXTURES TAGS (utilisées dans notes/ et tasks/) =====

@pytest.fixture
def sample_tag():
    """
    Crée un tag de test générique
    """
    return Tag.objects.create(name='test-tag')


@pytest.fixture
def python_tag():
    """
    Crée un tag 'python'
    """
    return Tag.objects.create(name='python')


@pytest.fixture
def django_tag():
    """
    Crée un tag 'django'
    """
    return Tag.objects.create(name='django')


# ===== FIXTURES PROJECTS (utilisées dans notes/, tasks/, comments/) =====

@pytest.fixture
def sample_project(lead_user):
    """
    Crée un projet de test basique
    Le créateur est un Lead (fixture globale)
    Fixture GLOBALE car utilisée par plusieurs apps (notes, tasks, comments)
    """
    from projects.models import Project
    return Project.objects.create(
        name='Test Project',
        description='Description de test',
        created_by=lead_user
    )
