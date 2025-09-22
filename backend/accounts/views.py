from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import UserProfile
from .serializers import UserSerializer, UserProfileSerializer


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour consulter les utilisateurs"""
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour consulter les profils utilisateurs"""
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Endpoint pour récupérer le profil de l'utilisateur connecté"""
        if request.user.is_authenticated:
            try:
                profile = UserProfile.objects.get(user=request.user)
                serializer = self.get_serializer(profile)
                return Response(serializer.data)
            except UserProfile.DoesNotExist:
                return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'error': 'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)