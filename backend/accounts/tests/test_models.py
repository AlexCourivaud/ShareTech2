# backend/accounts/tests/test_models.py
"""
Tests unitaires pour les modèles de l'app Accounts
Teste : UserProfile et les signals Django (création automatique de profil)
"""

import pytest
from django.contrib.auth.models import User
from django.db import IntegrityError
from accounts.models import UserProfile


# ===== TESTS DU MODÈLE USERPROFILE =====

@pytest.mark.django_db
def test_user_profile_creation_manual():
    """
    Test : Un UserProfile peut être créé manuellement

    Vérifie la création directe (sans signal)
    """
    # ARRANGE
    user = User.objects.create_user(username='testuser', password='testpass')

    # ACT
    # Le signal a déjà créé un profil, on le récupère
    profile = user.profile

    # ASSERT
    assert profile is not None
    assert profile.user == user
    assert profile.role == 'junior'  # Rôle par défaut


@pytest.mark.django_db
def test_user_profile_str_method_returns_username_and_role():
    """
    Test : La méthode __str__() retourne "username - Role Display"
    """
    # ARRANGE
    user = User.objects.create_user(username='testuser', password='testpass')
    profile = user.profile
    profile.role = 'senior'
    profile.save()

    # ACT
    result = str(profile)

    # ASSERT
    assert result == "testuser - Senior Developer"


@pytest.mark.django_db
def test_user_profile_get_role_display_returns_full_name():
    """
    Test : get_role_display() retourne le nom complet du rôle

    Django génère automatiquement cette méthode pour les CHOICES
    """
    # ARRANGE
    user = User.objects.create_user(username='testuser', password='testpass')
    profile = user.profile

    # ACT & ASSERT
    profile.role = 'junior'
    assert profile.get_role_display() == 'Junior Developer'

    profile.role = 'senior'
    assert profile.get_role_display() == 'Senior Developer'

    profile.role = 'lead'
    assert profile.get_role_display() == 'Lead Developer'

    profile.role = 'admin'
    assert profile.get_role_display() == 'Admin'


@pytest.mark.django_db
def test_user_profile_default_role_is_junior():
    """
    Test : Le rôle par défaut d'un UserProfile est 'junior'

    Vérifie le default='junior' du modèle
    """
    # ARRANGE
    user = User.objects.create_user(username='testuser', password='testpass')

    # ACT
    profile = user.profile

    # ASSERT
    assert profile.role == 'junior'


@pytest.mark.django_db
def test_user_profile_avatar_url_can_be_null():
    """
    Test : Le champ avatar_url peut être null/vide

    Vérifie blank=True, null=True
    """
    # ARRANGE
    user = User.objects.create_user(username='testuser', password='testpass')
    profile = user.profile

    # ACT & ASSERT
    assert profile.avatar_url is None or profile.avatar_url == ''


@pytest.mark.django_db
def test_user_profile_avatar_url_can_be_set():
    """
    Test : On peut définir une URL d'avatar
    """
    # ARRANGE
    user = User.objects.create_user(username='testuser', password='testpass')
    profile = user.profile

    # ACT
    profile.avatar_url = 'https://example.com/avatar.png'
    profile.save()

    # ASSERT
    profile.refresh_from_db()
    assert profile.avatar_url == 'https://example.com/avatar.png'


@pytest.mark.django_db
def test_user_profile_is_deleted_when_user_is_deleted():
    """
    Test : Le profil est supprimé quand le user est supprimé (CASCADE)

    Vérifie on_delete=models.CASCADE
    """
    # ARRANGE
    user = User.objects.create_user(username='testuser', password='testpass')
    profile_id = user.profile.id

    # ACT
    user.delete()

    # ASSERT
    assert not UserProfile.objects.filter(id=profile_id).exists()


@pytest.mark.django_db
def test_user_can_have_only_one_profile():
    """
    Test : Un user ne peut avoir qu'un seul profil (OneToOne)

    Tenter de créer un 2ème profil doit échouer
    """
    # ARRANGE
    user = User.objects.create_user(username='testuser', password='testpass')
    # Le signal a déjà créé un profil

    # ACT & ASSERT
    # Tenter de créer un 2ème profil doit lever une IntegrityError
    with pytest.raises(IntegrityError):
        UserProfile.objects.create(user=user, role='senior')


# ===== TESTS DES SIGNALS =====

@pytest.mark.django_db
def test_signal_creates_profile_automatically_for_normal_user():
    """
    Test : Le signal crée automatiquement un UserProfile quand un User est créé

    C'est LE test le plus important pour le système de profils !
    """
    # ARRANGE & ACT
    user = User.objects.create_user(
        username='newuser',
        email='new@test.com',
        password='testpass'
    )

    # ASSERT
    # Vérifier que le profil a été créé automatiquement
    assert hasattr(user, 'profile')
    assert user.profile is not None
    assert isinstance(user.profile, UserProfile)
    assert user.profile.user == user


@pytest.mark.django_db
def test_signal_creates_profile_with_junior_role_for_normal_user():
    """
    Test : Un user normal reçoit automatiquement le rôle 'junior'

    Vérifie la logique : if instance.is_superuser else 'junior'
    """
    # ARRANGE & ACT
    user = User.objects.create_user(
        username='normaluser',
        password='testpass',
        is_superuser=False  # Explicitement NON superuser
    )

    # ASSERT
    assert user.profile.role == 'junior'


@pytest.mark.django_db
def test_signal_creates_profile_with_admin_role_for_superuser():
    """
    Test : Un superuser reçoit automatiquement le rôle 'admin'

    Vérifie la logique : if instance.is_superuser -> 'admin'
    C'est critique pour la sécurité !
    """
    # ARRANGE & ACT
    user = User.objects.create_superuser(
        username='superuser',
        email='super@test.com',
        password='testpass'
    )

    # ASSERT
    assert user.is_superuser == True  # Vérification précondition
    assert user.profile.role == 'admin'  # Le signal a mis 'admin'


@pytest.mark.django_db
def test_signal_works_for_multiple_users():
    """
    Test : Le signal fonctionne pour plusieurs créations de users

    Vérifie qu'il n'y a pas d'effets de bord
    """
    # ARRANGE & ACT
    users = []
    for i in range(5):
        user = User.objects.create_user(
            username=f'user{i}',
            password='testpass'
        )
        users.append(user)

    # ASSERT
    for user in users:
        assert hasattr(user, 'profile')
        assert user.profile.role == 'junior'


@pytest.mark.django_db
def test_user_profile_role_can_be_changed_after_creation():
    """
    Test : Le rôle peut être modifié après la création

    Un Junior peut être promu Senior, Lead, etc.
    """
    # ARRANGE
    user = User.objects.create_user(username='testuser', password='testpass')
    assert user.profile.role == 'junior'  # Précondition

    # ACT
    user.profile.role = 'senior'
    user.profile.save()

    # ASSERT
    user.refresh_from_db()
    assert user.profile.role == 'senior'
