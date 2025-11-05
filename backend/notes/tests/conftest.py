# backend/notes/tests/conftest.py
"""
Fixtures locales pour les tests de l'app Notes
Ces fixtures sont accessibles uniquement dans notes/tests/
"""

import pytest
from notes.models import Note


@pytest.fixture
def sample_note(sample_project, junior_user):
    """
    Crée une note de test basique
    Utilise sample_project (de projects/tests/conftest.py)
    et junior_user (de backend/conftest.py)
    """
    return Note.objects.create(
        title='Test Note',
        content='Contenu de test pour la note',
        status='brouillon',
        project=sample_project,
        author=junior_user
    )


@pytest.fixture
def published_note(sample_project, senior_user):
    """
    Crée une note publiée
    """
    return Note.objects.create(
        title='Published Note',
        content='Cette note est publiée',
        status='publie',
        project=sample_project,
        author=senior_user
    )


@pytest.fixture
def archived_note(sample_project, lead_user):
    """
    Crée une note archivée
    """
    return Note.objects.create(
        title='Archived Note',
        content='Cette note est archivée',
        status='archive',
        project=sample_project,
        author=lead_user
    )
