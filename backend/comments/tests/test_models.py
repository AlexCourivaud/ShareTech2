# backend/comments/tests/test_models.py
"""
Tests unitaires pour les modèles de l'app Comments
Teste : Comment (avec relation auto-référençante pour les réponses)
"""

import pytest
from django.utils import timezone
from comments.models import Comment


# ===== TESTS DU MODÈLE COMMENT =====

@pytest.mark.django_db
def test_comment_creation_with_valid_data(sample_note, senior_user):
    """
    Test : Un commentaire se crée correctement avec des données valides

    Vérifie tous les champs et les relations
    """
    # ACT
    comment = Comment.objects.create(
        content='Ceci est un commentaire de test',
        note=sample_note,
        author=senior_user
    )

    # ASSERT
    assert comment.id is not None
    assert comment.content == 'Ceci est un commentaire de test'
    assert comment.note == sample_note
    assert comment.author == senior_user
    assert comment.parent_comment is None  # Pas de parent (commentaire racine)
    assert comment.is_edited is False  # Pas encore édité
    assert comment.created_at is not None
    assert comment.updated_at is not None


@pytest.mark.django_db
def test_comment_str_method_returns_author_and_preview(sample_comment):
    """
    Test : La méthode __str__() retourne "auteur - preview du contenu"

    Preview = 50 premiers caractères du contenu
    """
    # ACT
    result = str(sample_comment)

    # ASSERT
    # Format attendu : "username - contenu[:50]"
    assert result.startswith("seniortest - ")
    assert "Ceci est un commentaire de test" in result


@pytest.mark.django_db
def test_comment_str_method_with_deleted_author(sample_note, senior_user):
    """
    Test : La méthode __str__() gère le cas où l'auteur est supprimé

    Vérifie le cas author=None → affiche '[Compte supprimé]'
    """
    # ARRANGE
    comment = Comment.objects.create(
        content='Commentaire orphelin',
        note=sample_note,
        author=senior_user
    )
    comment_id = comment.id

    # Supprimer l'auteur (author devient NULL grâce à SET_NULL)
    senior_user.delete()

    # ACT
    comment.refresh_from_db()
    result = str(comment)

    # ASSERT
    assert comment.author is None
    assert result.startswith("[Compte supprimé] - ")


@pytest.mark.django_db
def test_comment_str_method_truncates_long_content(sample_note, senior_user):
    """
    Test : La méthode __str__() tronque le contenu à 50 caractères
    """
    # ARRANGE
    long_content = "A" * 100  # 100 caractères
    comment = Comment.objects.create(
        content=long_content,
        note=sample_note,
        author=senior_user
    )

    # ACT
    result = str(comment)

    # ASSERT
    # Devrait contenir seulement 50 'A'
    assert "A" * 50 in result
    assert len(result.split(" - ")[1]) == 50  # Après "username - "


@pytest.mark.django_db
def test_comment_default_is_edited_is_false(sample_note, senior_user):
    """
    Test : Le champ is_edited a False comme valeur par défaut

    Vérifie default=False
    """
    # ACT
    comment = Comment.objects.create(
        content='Commentaire non édité',
        note=sample_note,
        author=senior_user
    )

    # ASSERT
    assert comment.is_edited is False


@pytest.mark.django_db
def test_comment_is_edited_can_be_set_to_true(sample_comment):
    """
    Test : On peut marquer un commentaire comme édité
    """
    # ARRANGE
    assert sample_comment.is_edited is False  # Précondition

    # ACT
    sample_comment.is_edited = True
    sample_comment.save()

    # ASSERT
    sample_comment.refresh_from_db()
    assert sample_comment.is_edited is True


@pytest.mark.django_db
def test_comment_timestamps_are_auto_generated(sample_comment):
    """
    Test : Les timestamps created_at et updated_at sont automatiques
    """
    # ASSERT
    assert sample_comment.created_at is not None
    assert sample_comment.updated_at is not None
    assert sample_comment.created_at <= sample_comment.updated_at


@pytest.mark.django_db
def test_comment_updated_at_changes_on_save(sample_comment):
    """
    Test : Le champ updated_at se met à jour automatiquement

    Vérifie auto_now=True
    """
    # ARRANGE
    original_updated_at = sample_comment.updated_at

    # Attendre un peu pour garantir un timestamp différent
    import time
    time.sleep(0.1)

    # ACT
    sample_comment.content = 'Contenu modifié'
    sample_comment.save()

    # ASSERT
    sample_comment.refresh_from_db()
    assert sample_comment.updated_at > original_updated_at


@pytest.mark.django_db
def test_comment_is_deleted_when_note_is_deleted(sample_note, senior_user):
    """
    Test : Un commentaire est supprimé quand la note est supprimée (CASCADE)

    Vérifie on_delete=models.CASCADE pour note
    """
    # ARRANGE
    comment = Comment.objects.create(
        content='Commentaire à supprimer',
        note=sample_note,
        author=senior_user
    )
    comment_id = comment.id

    # ACT
    sample_note.delete()

    # ASSERT
    assert not Comment.objects.filter(id=comment_id).exists()


@pytest.mark.django_db
def test_comment_author_becomes_null_when_user_deleted(sample_note, senior_user):
    """
    Test : author devient NULL quand l'utilisateur est supprimé (SET_NULL)

    Vérifie on_delete=models.SET_NULL pour author
    Le commentaire reste mais l'auteur est perdu
    """
    # ARRANGE
    comment = Comment.objects.create(
        content='Commentaire orphelin',
        note=sample_note,
        author=senior_user
    )
    comment_id = comment.id

    # ACT
    senior_user.delete()

    # ASSERT
    comment.refresh_from_db()
    assert Comment.objects.filter(id=comment_id).exists()  # Commentaire existe toujours
    assert comment.author is None  # Mais auteur perdu


@pytest.mark.django_db
def test_comments_are_ordered_by_created_at_ascending(sample_note, junior_user, senior_user):
    """
    Test : Les commentaires sont ordonnés par created_at croissant

    Vérifie Meta.ordering = ['created_at'] (plus anciens en premier)
    """
    # ARRANGE
    import time
    comment1 = Comment.objects.create(content='Premier', note=sample_note, author=junior_user)
    time.sleep(0.1)
    comment2 = Comment.objects.create(content='Deuxième', note=sample_note, author=senior_user)
    time.sleep(0.1)
    comment3 = Comment.objects.create(content='Troisième', note=sample_note, author=junior_user)

    # ACT
    comments = Comment.objects.all()
    comment_contents = [c.content for c in comments]

    # ASSERT
    # Plus anciens en premier : Premier, Deuxième, Troisième
    assert comment_contents == ['Premier', 'Deuxième', 'Troisième']


# ===== TESTS DE LA RELATION AUTO-RÉFÉRENÇANTE (RÉPONSES) =====

@pytest.mark.django_db
def test_comment_can_have_parent_comment(sample_comment, junior_user):
    """
    Test : Un commentaire peut répondre à un autre commentaire

    Vérifie la relation auto-référençante (ForeignKey vers 'self')
    """
    # ACT
    reply = Comment.objects.create(
        content='Réponse au commentaire',
        note=sample_comment.note,
        author=junior_user,
        parent_comment=sample_comment  # Référence le commentaire parent
    )

    # ASSERT
    assert reply.parent_comment == sample_comment


@pytest.mark.django_db
def test_comment_can_access_replies(sample_comment, reply_comment):
    """
    Test : Un commentaire peut accéder à ses réponses via related_name='replies'

    Vérifie la navigation dans l'autre sens de la relation
    """
    # ACT
    replies = sample_comment.replies.all()

    # ASSERT
    assert replies.count() == 1
    assert reply_comment in replies


@pytest.mark.django_db
def test_comment_with_multiple_replies(sample_comment, junior_user, senior_user, lead_user):
    """
    Test : Un commentaire peut avoir plusieurs réponses
    """
    # ARRANGE
    reply1 = Comment.objects.create(
        content='Première réponse',
        note=sample_comment.note,
        author=junior_user,
        parent_comment=sample_comment
    )
    reply2 = Comment.objects.create(
        content='Deuxième réponse',
        note=sample_comment.note,
        author=senior_user,
        parent_comment=sample_comment
    )
    reply3 = Comment.objects.create(
        content='Troisième réponse',
        note=sample_comment.note,
        author=lead_user,
        parent_comment=sample_comment
    )

    # ACT
    replies = sample_comment.replies.all()

    # ASSERT
    assert replies.count() == 3
    reply_contents = [r.content for r in replies]
    assert 'Première réponse' in reply_contents
    assert 'Deuxième réponse' in reply_contents
    assert 'Troisième réponse' in reply_contents


@pytest.mark.django_db
def test_reply_is_deleted_when_parent_comment_is_deleted(sample_comment, reply_comment):
    """
    Test : Les réponses sont supprimées quand le commentaire parent est supprimé (CASCADE)

    Vérifie on_delete=models.CASCADE pour parent_comment
    """
    # ARRANGE
    reply_id = reply_comment.id

    # Vérifier que la réponse existe
    assert Comment.objects.filter(id=reply_id).exists()

    # ACT
    sample_comment.delete()

    # ASSERT
    # La réponse doit être supprimée en cascade
    assert not Comment.objects.filter(id=reply_id).exists()


@pytest.mark.django_db
def test_nested_replies_hierarchy(sample_note, junior_user, senior_user, lead_user):
    """
    Test : On peut créer une hiérarchie de commentaires (réponse à une réponse)

    Structure :
    - Commentaire racine
      - Réponse niveau 1
        - Réponse niveau 2
    """
    # ARRANGE
    root = Comment.objects.create(
        content='Commentaire racine',
        note=sample_note,
        author=junior_user
    )

    reply_level1 = Comment.objects.create(
        content='Réponse niveau 1',
        note=sample_note,
        author=senior_user,
        parent_comment=root
    )

    reply_level2 = Comment.objects.create(
        content='Réponse niveau 2',
        note=sample_note,
        author=lead_user,
        parent_comment=reply_level1
    )

    # ACT & ASSERT
    # Vérifier la hiérarchie
    assert root.parent_comment is None
    assert reply_level1.parent_comment == root
    assert reply_level2.parent_comment == reply_level1

    # Vérifier les relations inverses
    assert root.replies.count() == 1
    assert reply_level1.replies.count() == 1
    assert reply_level2.replies.count() == 0


@pytest.mark.django_db
def test_deleting_root_comment_cascades_all_replies(sample_note, junior_user, senior_user, lead_user):
    """
    Test : Supprimer un commentaire racine supprime toute la hiérarchie de réponses

    Vérifie le CASCADE en cascade (tous les niveaux)
    """
    # ARRANGE
    root = Comment.objects.create(
        content='Racine',
        note=sample_note,
        author=junior_user
    )

    reply1 = Comment.objects.create(
        content='Réponse 1',
        note=sample_note,
        author=senior_user,
        parent_comment=root
    )

    reply2 = Comment.objects.create(
        content='Réponse 2',
        note=sample_note,
        author=lead_user,
        parent_comment=reply1
    )

    root_id = root.id
    reply1_id = reply1.id
    reply2_id = reply2.id

    # ACT
    root.delete()

    # ASSERT
    # Tous les commentaires de la hiérarchie doivent être supprimés
    assert not Comment.objects.filter(id=root_id).exists()
    assert not Comment.objects.filter(id=reply1_id).exists()
    assert not Comment.objects.filter(id=reply2_id).exists()


@pytest.mark.django_db
def test_root_comments_have_null_parent(sample_note, junior_user, senior_user):
    """
    Test : Les commentaires racines ont parent_comment = NULL
    """
    # ARRANGE
    root1 = Comment.objects.create(content='Racine 1', note=sample_note, author=junior_user)
    root2 = Comment.objects.create(content='Racine 2', note=sample_note, author=senior_user)

    # ACT
    root_comments = Comment.objects.filter(parent_comment=None)

    # ASSERT
    assert root_comments.count() == 2
    assert root1 in root_comments
    assert root2 in root_comments
