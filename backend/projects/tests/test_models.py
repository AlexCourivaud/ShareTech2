# backend/projects/tests/test_models.py
"""
Tests unitaires pour les modèles de l'app Projects
Teste : Project et ProjectMember
"""

import pytest
from django.contrib.auth.models import User
from django.db import IntegrityError
from projects.models import Project, ProjectMember


# ===== TESTS DU MODÈLE PROJECT =====

@pytest.mark.django_db
def test_project_creation_with_valid_data(lead_user):
    """
    Test : Un projet se crée correctement avec des données valides

    Ce test vérifie :
    - Le projet est bien créé en base de données
    - Les champs ont les bonnes valeurs
    - Les valeurs par défaut sont correctes (is_active=True)
    """
    # ARRANGE (Préparer les données)
    # lead_user vient de la fixture globale

    # ACT (Exécuter l'action)
    project = Project.objects.create(
        name='Mon Projet Test',
        description='Une description de test',
        created_by=lead_user
    )

    # ASSERT (Vérifier les résultats)
    assert project.id is not None  # Un ID a été généré
    assert project.name == 'Mon Projet Test'
    assert project.description == 'Une description de test'
    assert project.created_by == lead_user
    assert project.is_active == True  # Valeur par défaut
    assert project.created_at is not None  # Date auto-générée
    assert project.updated_at is not None  # Date auto-générée


@pytest.mark.django_db
def test_project_str_method_returns_name_and_status_active(sample_project):
    """
    Test : La méthode __str__() retourne "Nom (Actif)" pour un projet actif

    Pattern testé : Représentation textuelle d'un objet
    """
    # ARRANGE
    # sample_project vient de la fixture locale (conftest.py)
    # sample_project est actif par défaut

    # ACT
    result = str(sample_project)

    # ASSERT
    assert result == "Test Project (Actif)"


@pytest.mark.django_db
def test_project_str_method_returns_name_and_status_termine(terminated_project):
    """
    Test : La méthode __str__() retourne "Nom (Terminé)" pour un projet terminé

    Pattern testé : Représentation textuelle d'un objet
    """
    # ARRANGE
    # terminated_project vient de la fixture locale
    # terminated_project est déjà terminé (is_active=False)

    # ACT
    result = str(terminated_project)

    # ASSERT
    assert result == "Terminated Project (Terminé)"


@pytest.mark.django_db
def test_project_terminate_method_sets_is_active_to_false(sample_project):
    """
    Test : La méthode terminate() met is_active à False

    Ce test vérifie la logique métier :
    - Un projet actif peut être terminé
    - terminate() change bien le statut
    """
    # ARRANGE
    assert sample_project.is_active == True  # Précondition

    # ACT
    sample_project.terminate()

    # ASSERT
    assert sample_project.is_active == False


@pytest.mark.django_db
def test_project_terminate_method_persists_to_database(sample_project):
    """
    Test : La méthode terminate() sauvegarde bien en base de données

    Ce test vérifie que le changement est persisté (pas juste en mémoire)
    """
    # ARRANGE
    project_id = sample_project.id

    # ACT
    sample_project.terminate()

    # ASSERT
    # On recharge le projet depuis la DB pour vérifier la persistance
    project_from_db = Project.objects.get(id=project_id)
    assert project_from_db.is_active == False


@pytest.mark.django_db
def test_project_has_created_at_and_updated_at_timestamps(sample_project):
    """
    Test : Les timestamps created_at et updated_at sont automatiquement générés

    Django doit créer ces dates automatiquement avec auto_now_add et auto_now
    """
    # ARRANGE & ACT
    # sample_project existe déjà

    # ASSERT
    assert sample_project.created_at is not None
    assert sample_project.updated_at is not None
    assert sample_project.created_at <= sample_project.updated_at


# ===== TESTS DU MODÈLE PROJECTMEMBER =====

@pytest.mark.django_db
def test_project_member_creation(sample_project, junior_user):
    """
    Test : On peut créer un membre de projet (ProjectMember)

    Vérifie la relation Many-to-Many entre Project et User
    """
    # ARRANGE
    # sample_project et junior_user existent déjà

    # ACT
    member = ProjectMember.objects.create(
        project=sample_project,
        user=junior_user
    )

    # ASSERT
    assert member.id is not None
    assert member.project == sample_project
    assert member.user == junior_user
    assert member.joined_at is not None  # Date auto-générée


@pytest.mark.django_db
def test_project_member_str_method_shows_username_project_and_role(sample_project, junior_user):
    """
    Test : La méthode __str__() de ProjectMember affiche "username - projet (rôle)"

    C'est le bug qu'on a corrigé ! Ce test garantit qu'il ne reviendra pas.
    """
    # ARRANGE
    member = ProjectMember.objects.create(
        project=sample_project,
        user=junior_user
    )

    # ACT
    result = str(member)

    # ASSERT
    # Format attendu : "juniortest - Test Project (Junior Developer)"
    assert 'juniortest' in result
    assert 'Test Project' in result
    assert 'Junior Developer' in result


@pytest.mark.django_db
def test_project_member_unique_constraint_prevents_duplicate(sample_project, junior_user):
    """
    Test : On ne peut pas ajouter le même user deux fois au même projet

    Vérifie la contrainte d'unicité unique_project_user
    """
    # ARRANGE
    ProjectMember.objects.create(project=sample_project, user=junior_user)

    # ACT & ASSERT
    # Tenter de créer un doublon doit lever une exception
    with pytest.raises(IntegrityError):
        ProjectMember.objects.create(project=sample_project, user=junior_user)


@pytest.mark.django_db
def test_project_can_have_multiple_different_members(sample_project, junior_user, senior_user, lead_user):
    """
    Test : Un projet peut avoir plusieurs membres différents
    """
    # ARRANGE & ACT
    ProjectMember.objects.create(project=sample_project, user=junior_user)
    ProjectMember.objects.create(project=sample_project, user=senior_user)
    ProjectMember.objects.create(project=sample_project, user=lead_user)

    # ASSERT
    members_count = sample_project.members.count()
    assert members_count == 3


@pytest.mark.django_db
def test_project_members_relation_returns_all_members(project_with_members):
    """
    Test : La relation 'members' retourne tous les membres du projet

    Vérifie que le related_name='members' fonctionne correctement
    """
    # ARRANGE
    # project_with_members a 2 membres (junior + senior) via la fixture

    # ACT
    members = project_with_members.members.all()

    # ASSERT
    assert members.count() == 2
    usernames = [m.user.username for m in members]
    assert 'juniortest' in usernames
    assert 'seniortest' in usernames
