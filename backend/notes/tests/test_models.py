# backend/notes/tests/test_models.py
"""
Tests unitaires pour les modèles de l'app Notes
Teste : Note et NoteTag (relation Many-to-Many avec Tag)
"""

import pytest
from django.db import IntegrityError
from django.utils import timezone
from notes.models import Note, NoteTag
from tags.models import Tag


# ===== TESTS DU MODÈLE NOTE =====

@pytest.mark.django_db
def test_note_creation_with_valid_data(sample_project, junior_user):
    """
    Test : Une note se crée correctement avec des données valides

    Vérifie tous les champs et les relations
    """
    # ACT
    note = Note.objects.create(
        title='Ma Note de Test',
        content='Contenu détaillé de la note',
        status='brouillon',
        project=sample_project,
        author=junior_user
    )

    # ASSERT
    assert note.id is not None
    assert note.title == 'Ma Note de Test'
    assert note.content == 'Contenu détaillé de la note'
    assert note.status == 'brouillon'
    assert note.project == sample_project
    assert note.author == junior_user
    assert note.created_at is not None
    assert note.updated_at is not None


@pytest.mark.django_db
def test_note_str_method_returns_title_and_status(sample_note):
    """
    Test : La méthode __str__() retourne "titre (Statut)"
    """
    # ARRANGE
    # sample_note a status='brouillon'

    # ACT
    result = str(sample_note)

    # ASSERT
    assert result == "Test Note (Brouillon)"


@pytest.mark.django_db
def test_note_default_status_is_brouillon(sample_project, junior_user):
    """
    Test : Le statut par défaut d'une note est 'brouillon'

    Vérifie default='brouillon'
    """
    # ACT
    note = Note.objects.create(
        title='Note sans statut',
        content='Contenu',
        project=sample_project,
        author=junior_user
        # status non spécifié → doit être 'brouillon'
    )

    # ASSERT
    assert note.status == 'brouillon'


@pytest.mark.django_db
def test_note_all_status_choices_are_valid(sample_project, junior_user):
    """
    Test : Tous les statuts (brouillon/publie/archive) sont valides

    Vérifie les 3 STATUS_CHOICES
    """
    # ACT
    note1 = Note.objects.create(title='N1', content='C', status='brouillon', project=sample_project, author=junior_user)
    note2 = Note.objects.create(title='N2', content='C', status='publie', project=sample_project, author=junior_user)
    note3 = Note.objects.create(title='N3', content='C', status='archive', project=sample_project, author=junior_user)

    # ASSERT
    assert note1.get_status_display() == 'Brouillon'
    assert note2.get_status_display() == 'Publié'
    assert note3.get_status_display() == 'Archivé'


@pytest.mark.django_db
def test_note_timestamps_are_auto_generated(sample_note):
    """
    Test : Les timestamps created_at et updated_at sont automatiques
    """
    # ARRANGE & ACT
    # sample_note existe déjà

    # ASSERT
    assert sample_note.created_at is not None
    assert sample_note.updated_at is not None
    assert sample_note.created_at <= sample_note.updated_at


@pytest.mark.django_db
def test_note_published_at_can_be_null(sample_note):
    """
    Test : Le champ published_at peut être null

    Vérifie blank=True, null=True
    """
    # ARRANGE & ACT
    # sample_note est un brouillon, donc published_at devrait être null

    # ASSERT
    assert sample_note.published_at is None


@pytest.mark.django_db
def test_note_published_at_can_be_set(sample_note):
    """
    Test : On peut définir published_at manuellement
    """
    # ARRANGE
    now = timezone.now()

    # ACT
    sample_note.published_at = now
    sample_note.save()

    # ASSERT
    sample_note.refresh_from_db()
    assert sample_note.published_at == now


@pytest.mark.django_db
def test_note_is_deleted_when_project_is_deleted(sample_project, junior_user):
    """
    Test : Une note est supprimée quand son projet est supprimé (CASCADE)

    Vérifie on_delete=models.CASCADE pour project
    """
    # ARRANGE
    note = Note.objects.create(
        title='Note à supprimer',
        content='Contenu',
        project=sample_project,
        author=junior_user
    )
    note_id = note.id

    # ACT
    sample_project.delete()

    # ASSERT
    assert not Note.objects.filter(id=note_id).exists()


@pytest.mark.django_db
def test_note_is_deleted_when_author_is_deleted(sample_project, junior_user):
    """
    Test : Une note est supprimée quand son auteur est supprimé (CASCADE)

    Vérifie on_delete=models.CASCADE pour author
    """
    # ARRANGE
    note = Note.objects.create(
        title='Note à supprimer',
        content='Contenu',
        project=sample_project,
        author=junior_user
    )
    note_id = note.id

    # ACT
    junior_user.delete()

    # ASSERT
    assert not Note.objects.filter(id=note_id).exists()


@pytest.mark.django_db
def test_notes_are_ordered_by_created_at_descending(sample_project, junior_user):
    """
    Test : Les notes sont ordonnées par created_at décroissant

    Vérifie Meta.ordering = ['-created_at'] (plus récentes en premier)
    """
    # ARRANGE
    import time
    note1 = Note.objects.create(title='Note 1', content='C', project=sample_project, author=junior_user)
    time.sleep(0.1)
    note2 = Note.objects.create(title='Note 2', content='C', project=sample_project, author=junior_user)
    time.sleep(0.1)
    note3 = Note.objects.create(title='Note 3', content='C', project=sample_project, author=junior_user)

    # ACT
    notes = Note.objects.all()
    note_titles = [note.title for note in notes]

    # ASSERT
    # Plus récentes en premier : Note 3, Note 2, Note 1
    assert note_titles == ['Note 3', 'Note 2', 'Note 1']


# ===== TESTS DU MODÈLE NOTETAG =====

@pytest.mark.django_db
def test_note_tag_creation(sample_note, sample_tag):
    """
    Test : On peut créer une association note-tag (NoteTag)

    Vérifie la relation Many-to-Many
    """
    # ACT
    note_tag = NoteTag.objects.create(
        note=sample_note,
        tag=sample_tag
    )

    # ASSERT
    assert note_tag.id is not None
    assert note_tag.note == sample_note
    assert note_tag.tag == sample_tag
    assert note_tag.assigned_at is not None


@pytest.mark.django_db
def test_note_tag_str_method_returns_note_and_tag(sample_note, sample_tag):
    """
    Test : La méthode __str__() de NoteTag affiche "note - tag"
    """
    # ARRANGE
    note_tag = NoteTag.objects.create(note=sample_note, tag=sample_tag)

    # ACT
    result = str(note_tag)

    # ASSERT
    assert result == "Test Note - test-tag"


@pytest.mark.django_db
def test_note_tag_unique_constraint_prevents_duplicate(sample_note, sample_tag):
    """
    Test : On ne peut pas ajouter le même tag deux fois à la même note

    Vérifie la contrainte unique_note_tag
    """
    # ARRANGE
    NoteTag.objects.create(note=sample_note, tag=sample_tag)

    # ACT & ASSERT
    # Tenter de créer un doublon doit lever une IntegrityError
    with pytest.raises(IntegrityError):
        NoteTag.objects.create(note=sample_note, tag=sample_tag)


@pytest.mark.django_db
def test_note_can_have_multiple_different_tags(sample_note):
    """
    Test : Une note peut avoir plusieurs tags différents
    """
    # ARRANGE
    tag1 = Tag.objects.create(name='python')
    tag2 = Tag.objects.create(name='django')
    tag3 = Tag.objects.create(name='testing')

    # ACT
    NoteTag.objects.create(note=sample_note, tag=tag1)
    NoteTag.objects.create(note=sample_note, tag=tag2)
    NoteTag.objects.create(note=sample_note, tag=tag3)

    # ASSERT
    assert sample_note.note_tags.count() == 3
    tag_names = [nt.tag.name for nt in sample_note.note_tags.all()]
    assert 'python' in tag_names
    assert 'django' in tag_names
    assert 'testing' in tag_names


@pytest.mark.django_db
def test_tag_can_be_on_multiple_notes(sample_project, junior_user, sample_tag):
    """
    Test : Un tag peut être associé à plusieurs notes différentes
    """
    # ARRANGE
    note1 = Note.objects.create(title='N1', content='C', project=sample_project, author=junior_user)
    note2 = Note.objects.create(title='N2', content='C', project=sample_project, author=junior_user)
    note3 = Note.objects.create(title='N3', content='C', project=sample_project, author=junior_user)

    # ACT
    NoteTag.objects.create(note=note1, tag=sample_tag)
    NoteTag.objects.create(note=note2, tag=sample_tag)
    NoteTag.objects.create(note=note3, tag=sample_tag)

    # ASSERT
    # Le tag est sur 3 notes différentes
    assert sample_tag.note_tags.count() == 3


@pytest.mark.django_db
def test_note_tag_assigned_at_is_auto_generated(sample_note, sample_tag):
    """
    Test : Le champ assigned_at est automatiquement généré

    Vérifie auto_now_add=True
    """
    # ACT
    note_tag = NoteTag.objects.create(note=sample_note, tag=sample_tag)

    # ASSERT
    assert note_tag.assigned_at is not None
    time_diff = timezone.now() - note_tag.assigned_at
    import datetime
    assert time_diff < datetime.timedelta(seconds=5)


@pytest.mark.django_db
def test_note_tag_is_deleted_when_note_is_deleted(sample_note, sample_tag):
    """
    Test : NoteTag est supprimé quand la note est supprimée (CASCADE)
    """
    # ARRANGE
    note_tag = NoteTag.objects.create(note=sample_note, tag=sample_tag)
    note_tag_id = note_tag.id

    # ACT
    sample_note.delete()

    # ASSERT
    assert not NoteTag.objects.filter(id=note_tag_id).exists()


@pytest.mark.django_db
def test_note_tag_is_deleted_when_tag_is_deleted(sample_note, sample_tag):
    """
    Test : NoteTag est supprimé quand le tag est supprimé (CASCADE)
    """
    # ARRANGE
    note_tag = NoteTag.objects.create(note=sample_note, tag=sample_tag)
    note_tag_id = note_tag.id

    # ACT
    sample_tag.delete()

    # ASSERT
    assert not NoteTag.objects.filter(id=note_tag_id).exists()
