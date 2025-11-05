# backend/tags/tests/test_models.py
"""
Tests unitaires pour le modèle Tag
Le modèle Tag est simple (2 champs) mais important car partagé entre Notes et Tasks
"""

import pytest
from django.db import IntegrityError
from tags.models import Tag


# ===== TESTS DU MODÈLE TAG =====

@pytest.mark.django_db
def test_tag_creation_with_valid_name():
    """
    Test : Un tag se crée correctement avec un nom valide

    Pattern AAA :
    - ARRANGE : Pas besoin de données préalables
    - ACT : Créer un tag
    - ASSERT : Vérifier que le tag existe avec les bonnes valeurs
    """
    # ACT
    tag = Tag.objects.create(name='python')

    # ASSERT
    assert tag.id is not None  # Un ID a été généré
    assert tag.name == 'python'
    assert tag.created_at is not None  # Date auto-générée


@pytest.mark.django_db
def test_tag_str_method_returns_name(sample_tag):
    """
    Test : La méthode __str__() retourne le nom du tag

    C'est important pour l'affichage dans l'admin Django
    """
    # ARRANGE
    # sample_tag vient de la fixture globale (conftest.py)

    # ACT
    result = str(sample_tag)

    # ASSERT
    assert result == 'test-tag'


@pytest.mark.django_db
def test_tag_name_must_be_unique():
    """
    Test : La contrainte unique=True sur name empêche les doublons

    Deux tags ne peuvent pas avoir le même nom
    """
    # ARRANGE
    Tag.objects.create(name='python')

    # ACT & ASSERT
    # Tenter de créer un doublon doit lever une IntegrityError
    with pytest.raises(IntegrityError):
        Tag.objects.create(name='python')


@pytest.mark.django_db
def test_tag_created_at_is_auto_generated():
    """
    Test : Le champ created_at est automatiquement généré

    Django doit créer cette date avec auto_now_add=True
    """
    # ARRANGE & ACT
    tag = Tag.objects.create(name='django')

    # ASSERT
    assert tag.created_at is not None
    # On peut aussi vérifier que c'est une date récente
    from django.utils import timezone
    import datetime
    time_diff = timezone.now() - tag.created_at
    assert time_diff < datetime.timedelta(seconds=5)  # Créé il y a moins de 5 secondes


@pytest.mark.django_db
def test_tags_are_ordered_alphabetically():
    """
    Test : Les tags sont ordonnés par nom (ordre alphabétique)

    Vérifie le Meta.ordering = ['name']
    """
    # ARRANGE
    # Créer des tags dans le désordre
    Tag.objects.create(name='zebra')
    Tag.objects.create(name='apple')
    Tag.objects.create(name='banana')

    # ACT
    tags = Tag.objects.all()
    tag_names = [tag.name for tag in tags]

    # ASSERT
    assert tag_names == ['apple', 'banana', 'zebra']  # Ordre alphabétique


@pytest.mark.django_db
def test_tag_name_max_length_is_50():
    """
    Test : Le nom du tag ne peut pas dépasser 50 caractères

    Vérifie la contrainte max_length=50
    """
    # ARRANGE
    long_name = 'a' * 51  # 51 caractères

    # ACT & ASSERT
    # Django lève une exception si le nom est trop long lors de la validation
    tag = Tag(name=long_name)

    # On teste que la validation échoue
    from django.core.exceptions import ValidationError
    with pytest.raises(ValidationError):
        tag.full_clean()  # Valide tous les champs


@pytest.mark.django_db
def test_tag_name_exactly_50_chars_is_valid():
    """
    Test : Un nom de 50 caractères exactement est valide

    Test de la limite exacte (edge case)
    """
    # ARRANGE
    exact_50_chars = 'a' * 50

    # ACT
    tag = Tag.objects.create(name=exact_50_chars)

    # ASSERT
    assert tag.name == exact_50_chars
    assert len(tag.name) == 50


@pytest.mark.django_db
def test_tag_can_be_deleted():
    """
    Test : Un tag peut être supprimé

    Pas de contrainte CASCADE empêchant la suppression
    Note : En production, attention aux NoteTag et TaskTag !
    """
    # ARRANGE
    tag = Tag.objects.create(name='to-delete')
    tag_id = tag.id

    # ACT
    tag.delete()

    # ASSERT
    assert not Tag.objects.filter(id=tag_id).exists()
    assert Tag.objects.count() == 0


@pytest.mark.django_db
def test_multiple_tags_can_be_created():
    """
    Test : Plusieurs tags peuvent coexister

    Vérifie qu'il n'y a pas de limite artificielle
    """
    # ARRANGE & ACT
    tags = []
    for i in range(10):
        tag = Tag.objects.create(name=f'tag-{i}')
        tags.append(tag)

    # ASSERT
    assert Tag.objects.count() == 10
    assert len(tags) == 10
