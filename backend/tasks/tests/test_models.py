# backend/tasks/tests/test_models.py
"""
Tests unitaires pour les modèles de l'app Tasks
Teste : Task et TaskTag (relation Many-to-Many avec Tag)
"""

import pytest
from decimal import Decimal
from django.db import IntegrityError
from django.utils import timezone
from tasks.models import Task, TaskTag
from tags.models import Tag


# ===== TESTS DU MODÈLE TASK =====

@pytest.mark.django_db
def test_task_creation_with_valid_data(sample_project, junior_user):
    """
    Test : Une tâche se crée correctement avec des données valides

    Vérifie tous les champs et les relations
    """
    # ACT
    task = Task.objects.create(
        title='Ma Tâche de Test',
        description='Description détaillée de la tâche',
        status='ouverte',
        priority='haute',
        project=sample_project,
        created_by=junior_user
    )

    # ASSERT
    assert task.id is not None
    assert task.title == 'Ma Tâche de Test'
    assert task.description == 'Description détaillée de la tâche'
    assert task.status == 'ouverte'
    assert task.priority == 'haute'
    assert task.project == sample_project
    assert task.created_by == junior_user
    assert task.assigned_to is None  # Pas encore assignée
    assert task.created_at is not None
    assert task.updated_at is not None


@pytest.mark.django_db
def test_task_str_method_returns_title(sample_task):
    """
    Test : La méthode __str__() retourne le titre de la tâche
    """
    # ACT
    result = str(sample_task)

    # ASSERT
    assert result == "Test Task"


@pytest.mark.django_db
def test_task_default_status_is_ouverte(sample_project, junior_user):
    """
    Test : Le statut par défaut d'une tâche est 'ouverte'

    Vérifie default='ouverte'
    """
    # ACT
    task = Task.objects.create(
        title='Tâche sans statut',
        project=sample_project,
        created_by=junior_user
        # status non spécifié → doit être 'ouverte'
    )

    # ASSERT
    assert task.status == 'ouverte'


@pytest.mark.django_db
def test_task_default_priority_is_normale(sample_project, junior_user):
    """
    Test : La priorité par défaut d'une tâche est 'normale'

    Vérifie default='normale'
    """
    # ACT
    task = Task.objects.create(
        title='Tâche sans priorité',
        project=sample_project,
        created_by=junior_user
        # priority non spécifiée → doit être 'normale'
    )

    # ASSERT
    assert task.priority == 'normale'


@pytest.mark.django_db
def test_task_all_status_choices_are_valid(sample_project, junior_user):
    """
    Test : Tous les statuts (ouverte/assignee/terminee) sont valides

    Vérifie les 3 STATUS_CHOICES
    """
    # ACT
    task1 = Task.objects.create(title='T1', status='ouverte', project=sample_project, created_by=junior_user)
    task2 = Task.objects.create(title='T2', status='assignee', project=sample_project, created_by=junior_user)
    task3 = Task.objects.create(title='T3', status='terminee', project=sample_project, created_by=junior_user)

    # ASSERT
    assert task1.get_status_display() == 'Ouverte'
    assert task2.get_status_display() == 'Assignée'
    assert task3.get_status_display() == 'Terminée'


@pytest.mark.django_db
def test_task_all_priority_choices_are_valid(sample_project, junior_user):
    """
    Test : Toutes les priorités (basse/normale/haute/urgente) sont valides

    Vérifie les 4 PRIORITY_CHOICES
    """
    # ACT
    task1 = Task.objects.create(title='T1', priority='basse', project=sample_project, created_by=junior_user)
    task2 = Task.objects.create(title='T2', priority='normale', project=sample_project, created_by=junior_user)
    task3 = Task.objects.create(title='T3', priority='haute', project=sample_project, created_by=junior_user)
    task4 = Task.objects.create(title='T4', priority='urgente', project=sample_project, created_by=junior_user)

    # ASSERT
    assert task1.get_priority_display() == 'Basse'
    assert task2.get_priority_display() == 'Normale'
    assert task3.get_priority_display() == 'Haute'
    assert task4.get_priority_display() == 'Urgente'


@pytest.mark.django_db
def test_task_can_be_assigned_to_user(sample_project, junior_user, senior_user):
    """
    Test : Une tâche peut être assignée à un utilisateur

    Vérifie le champ assigned_to (ForeignKey optionnelle)
    """
    # ACT
    task = Task.objects.create(
        title='Tâche à assigner',
        project=sample_project,
        created_by=junior_user,
        assigned_to=senior_user
    )

    # ASSERT
    assert task.assigned_to == senior_user


@pytest.mark.django_db
def test_task_estimated_hours_can_be_set(sample_project, junior_user):
    """
    Test : On peut définir les heures estimées (DecimalField)
    """
    # ACT
    task = Task.objects.create(
        title='Tâche avec heures estimées',
        project=sample_project,
        created_by=junior_user,
        estimated_hours=Decimal('5.50')
    )

    # ASSERT
    assert task.estimated_hours == Decimal('5.50')


@pytest.mark.django_db
def test_task_actual_hours_can_be_set(sample_project, junior_user):
    """
    Test : On peut définir les heures réelles (DecimalField)
    """
    # ACT
    task = Task.objects.create(
        title='Tâche avec heures réelles',
        project=sample_project,
        created_by=junior_user,
        actual_hours=Decimal('7.25')
    )

    # ASSERT
    assert task.actual_hours == Decimal('7.25')


@pytest.mark.django_db
def test_task_due_date_can_be_set(sample_project, junior_user):
    """
    Test : On peut définir une date d'échéance
    """
    # ARRANGE
    from datetime import date
    due = date(2025, 12, 31)

    # ACT
    task = Task.objects.create(
        title='Tâche avec échéance',
        project=sample_project,
        created_by=junior_user,
        due_date=due
    )

    # ASSERT
    assert task.due_date == due


@pytest.mark.django_db
def test_task_completed_date_can_be_set(sample_project, junior_user):
    """
    Test : On peut définir une date de complétion
    """
    # ARRANGE
    from datetime import date
    completed = date(2025, 11, 5)

    # ACT
    task = Task.objects.create(
        title='Tâche complétée',
        status='terminee',
        project=sample_project,
        created_by=junior_user,
        completed_date=completed
    )

    # ASSERT
    assert task.completed_date == completed


@pytest.mark.django_db
def test_task_timestamps_are_auto_generated(sample_task):
    """
    Test : Les timestamps created_at et updated_at sont automatiques
    """
    # ASSERT
    assert sample_task.created_at is not None
    assert sample_task.updated_at is not None
    assert sample_task.created_at <= sample_task.updated_at


@pytest.mark.django_db
def test_task_is_deleted_when_project_is_deleted(sample_project, junior_user):
    """
    Test : Une tâche est supprimée quand son projet est supprimé (CASCADE)

    Vérifie on_delete=models.CASCADE pour project
    """
    # ARRANGE
    task = Task.objects.create(
        title='Tâche à supprimer',
        project=sample_project,
        created_by=junior_user
    )
    task_id = task.id

    # ACT
    sample_project.delete()

    # ASSERT
    assert not Task.objects.filter(id=task_id).exists()


@pytest.mark.django_db
def test_task_is_deleted_when_creator_is_deleted(sample_project, junior_user):
    """
    Test : Une tâche est supprimée quand son créateur est supprimé (CASCADE)

    Vérifie on_delete=models.CASCADE pour created_by
    """
    # ARRANGE
    task = Task.objects.create(
        title='Tâche à supprimer',
        project=sample_project,
        created_by=junior_user
    )
    task_id = task.id

    # ACT
    junior_user.delete()

    # ASSERT
    assert not Task.objects.filter(id=task_id).exists()


@pytest.mark.django_db
def test_task_assigned_to_becomes_null_when_user_deleted(sample_project, junior_user, senior_user):
    """
    Test : assigned_to devient NULL quand l'utilisateur assigné est supprimé (SET_NULL)

    Vérifie on_delete=models.SET_NULL pour assigned_to
    La tâche reste mais l'assignation est perdue
    """
    # ARRANGE
    task = Task.objects.create(
        title='Tâche assignée',
        project=sample_project,
        created_by=junior_user,
        assigned_to=senior_user
    )
    task_id = task.id

    # ACT
    senior_user.delete()

    # ASSERT
    task.refresh_from_db()
    assert Task.objects.filter(id=task_id).exists()  # Tâche existe toujours
    assert task.assigned_to is None  # Mais assignation perdue


@pytest.mark.django_db
def test_tasks_are_ordered_by_created_at_descending(sample_project, junior_user):
    """
    Test : Les tâches sont ordonnées par created_at décroissant

    Vérifie Meta.ordering = ['-created_at'] (plus récentes en premier)
    """
    # ARRANGE
    import time
    task1 = Task.objects.create(title='Task 1', project=sample_project, created_by=junior_user)
    time.sleep(0.1)
    task2 = Task.objects.create(title='Task 2', project=sample_project, created_by=junior_user)
    time.sleep(0.1)
    task3 = Task.objects.create(title='Task 3', project=sample_project, created_by=junior_user)

    # ACT
    tasks = Task.objects.all()
    task_titles = [task.title for task in tasks]

    # ASSERT
    # Plus récentes en premier : Task 3, Task 2, Task 1
    assert task_titles == ['Task 3', 'Task 2', 'Task 1']


# ===== TESTS DU MODÈLE TASKTAG =====

@pytest.mark.django_db
def test_task_tag_creation(sample_task, sample_tag):
    """
    Test : On peut créer une association task-tag (TaskTag)

    Vérifie la relation Many-to-Many
    """
    # ACT
    task_tag = TaskTag.objects.create(
        task=sample_task,
        tag=sample_tag
    )

    # ASSERT
    assert task_tag.id is not None
    assert task_tag.task == sample_task
    assert task_tag.tag == sample_tag
    assert task_tag.assigned_at is not None


@pytest.mark.django_db
def test_task_tag_str_method_returns_task_and_tag(sample_task, sample_tag):
    """
    Test : La méthode __str__() de TaskTag affiche "task - tag"
    """
    # ARRANGE
    task_tag = TaskTag.objects.create(task=sample_task, tag=sample_tag)

    # ACT
    result = str(task_tag)

    # ASSERT
    assert result == "Test Task - test-tag"


@pytest.mark.django_db
def test_task_can_have_multiple_different_tags(sample_task):
    """
    Test : Une tâche peut avoir plusieurs tags différents
    """
    # ARRANGE
    tag1 = Tag.objects.create(name='backend')
    tag2 = Tag.objects.create(name='frontend')
    tag3 = Tag.objects.create(name='urgent')

    # ACT
    TaskTag.objects.create(task=sample_task, tag=tag1)
    TaskTag.objects.create(task=sample_task, tag=tag2)
    TaskTag.objects.create(task=sample_task, tag=tag3)

    # ASSERT
    assert sample_task.task_tags.count() == 3
    tag_names = [tt.tag.name for tt in sample_task.task_tags.all()]
    assert 'backend' in tag_names
    assert 'frontend' in tag_names
    assert 'urgent' in tag_names


@pytest.mark.django_db
def test_tag_can_be_on_multiple_tasks(sample_project, junior_user, sample_tag):
    """
    Test : Un tag peut être associé à plusieurs tâches différentes
    """
    # ARRANGE
    task1 = Task.objects.create(title='T1', project=sample_project, created_by=junior_user)
    task2 = Task.objects.create(title='T2', project=sample_project, created_by=junior_user)
    task3 = Task.objects.create(title='T3', project=sample_project, created_by=junior_user)

    # ACT
    TaskTag.objects.create(task=task1, tag=sample_tag)
    TaskTag.objects.create(task=task2, tag=sample_tag)
    TaskTag.objects.create(task=task3, tag=sample_tag)

    # ASSERT
    # Le tag est sur 3 tâches différentes
    assert sample_tag.task_tags.count() == 3


@pytest.mark.django_db
def test_task_tag_assigned_at_is_auto_generated(sample_task, sample_tag):
    """
    Test : Le champ assigned_at est automatiquement généré

    Vérifie auto_now_add=True
    """
    # ACT
    task_tag = TaskTag.objects.create(task=sample_task, tag=sample_tag)

    # ASSERT
    assert task_tag.assigned_at is not None
    time_diff = timezone.now() - task_tag.assigned_at
    import datetime
    assert time_diff < datetime.timedelta(seconds=5)


@pytest.mark.django_db
def test_task_tag_is_deleted_when_task_is_deleted(sample_task, sample_tag):
    """
    Test : TaskTag est supprimé quand la tâche est supprimée (CASCADE)
    """
    # ARRANGE
    task_tag = TaskTag.objects.create(task=sample_task, tag=sample_tag)
    task_tag_id = task_tag.id

    # ACT
    sample_task.delete()

    # ASSERT
    assert not TaskTag.objects.filter(id=task_tag_id).exists()


@pytest.mark.django_db
def test_task_tag_is_deleted_when_tag_is_deleted(sample_task, sample_tag):
    """
    Test : TaskTag est supprimé quand le tag est supprimé (CASCADE)
    """
    # ARRANGE
    task_tag = TaskTag.objects.create(task=sample_task, tag=sample_tag)
    task_tag_id = task_tag.id

    # ACT
    sample_tag.delete()

    # ASSERT
    assert not TaskTag.objects.filter(id=task_tag_id).exists()
