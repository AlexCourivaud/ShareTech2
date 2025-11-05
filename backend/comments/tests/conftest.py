# backend/comments/tests/conftest.py
"""
Fixtures locales pour les tests de l'app Comments
Ces fixtures sont accessibles uniquement dans comments/tests/
"""

import pytest
from comments.models import Comment
from notes.models import Note


@pytest.fixture
def sample_note(sample_project, junior_user):
    """
    Crée une note de test pour les commentaires
    Réutilise sample_project (globale) et junior_user (globale)
    """
    return Note.objects.create(
        title='Note pour commentaires',
        content='Contenu de la note',
        status='publie',
        project=sample_project,
        author=junior_user
    )


@pytest.fixture
def sample_comment(sample_note, senior_user):
    """
    Crée un commentaire de test basique (commentaire racine, pas de parent)
    """
    return Comment.objects.create(
        content='Ceci est un commentaire de test',
        note=sample_note,
        author=senior_user
    )


@pytest.fixture
def reply_comment(sample_comment, junior_user):
    """
    Crée une réponse à un commentaire existant (commentaire enfant)
    """
    return Comment.objects.create(
        content='Ceci est une réponse au commentaire',
        note=sample_comment.note,
        author=junior_user,
        parent_comment=sample_comment
    )
