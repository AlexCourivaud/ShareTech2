from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from .serializers import UserSerializer, UserRegistrationSerializer

@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """
    Inscription d'un nouvel utilisateur
    POST /api/accounts/register/
    """
    serializer = UserRegistrationSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        return Response({
            'message': 'Utilisateur créé avec succès',
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Connexion d'un utilisateur
    POST /api/accounts/login/
    Body: {"username": "...", "password": "..."}
    """
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response({
            'error': 'Username et password requis'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user = authenticate(request, username=username, password=password)
    
    if user is not None:
        auth_login(request, user)
        return Response({
            'message': 'Connexion réussie',
            'user': UserSerializer(user).data
        }, status=status.HTTP_200_OK)
    
    return Response({
        'error': 'Identifiants incorrects'
    }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    Déconnexion de l'utilisateur
    POST /api/accounts/logout/
    """
    auth_logout(request)
    return Response({
        'message': 'Déconnexion réussie'
    }, status=status.HTTP_200_OK)


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    """
    Voir ou modifier son profil
    GET /api/accounts/profile/ - Voir son profil
    PUT /api/accounts/profile/ - Modifier son profil
    """
    if request.method == 'GET':
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = UserSerializer(request.user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()

            # Mettre à jour le profil si des données sont fournies
            profile_data = request.data.get('profile', {})
            if profile_data:
                profile = request.user.profile

                # SÉCURITÉ: Seuls les admins peuvent modifier les rôles
                if 'role' in profile_data:
                    if request.user.profile.role != 'admin':
                        return Response({
                            'error': 'Seuls les administrateurs peuvent modifier les rôles'
                        }, status=status.HTTP_403_FORBIDDEN)
                    profile.role = profile_data.get('role')

                # Avatar peut être modifié par n'importe qui
                if 'avatar_url' in profile_data:
                    profile.avatar_url = profile_data.get('avatar_url')

                profile.save()

            return Response(UserSerializer(request.user).data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)