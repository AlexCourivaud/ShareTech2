from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer pour le profil utilisateur"""
    
    class Meta:
        model = UserProfile
        fields = ['role', 'avatar_url']


class UserSerializer(serializers.ModelSerializer):
    """Serializer pour l'utilisateur avec son profil"""
    profile = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                  'is_active', 'date_joined', 'profile']
        read_only_fields = ['id', 'date_joined']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer pour l'inscription d'un nouvel utilisateur"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(
        choices=UserProfile.ROLE_CHOICES, 
        default='junior'
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm',
                  'first_name', 'last_name', 'role']
    
    def validate(self, data):
        """Vérifier que les mots de passe correspondent"""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'Les mots de passe ne correspondent pas.'
            })
        return data
    
    def create(self, validated_data):
        """Créer l'utilisateur et son profil"""
        validated_data.pop('password_confirm')
        role = validated_data.pop('role', 'junior')
        
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        
        # Le profil est créé automatiquement par le signal
        # On met juste à jour le rôle
        user.profile.role = role
        user.profile.save()
        
        return user