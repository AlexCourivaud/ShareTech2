from rest_framework import permissions


class IsJunior(permissions.BasePermission):
    """
    Permission pour Junior Developer
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.profile.role == 'junior'


class IsSenior(permissions.BasePermission):
    """
    Permission pour Senior Developer et supérieur
    """
    ALLOWED_ROLES = ['senior', 'lead', 'admin']
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.profile.role in self.ALLOWED_ROLES


class IsLead(permissions.BasePermission):
    """
    Permission pour Lead Developer et Admin
    """
    ALLOWED_ROLES = ['lead', 'admin']
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.profile.role in self.ALLOWED_ROLES


class IsLeadOrAdmin(permissions.BasePermission):
    """
    Permission pour Lead et Admin
    """
    ALLOWED_ROLES = ['lead', 'admin']
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.profile.role in self.ALLOWED_ROLES


class IsAdmin(permissions.BasePermission):
    """
    Permission pour Admin uniquement
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.profile.role == 'admin'


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Lecture autorisée pour tous.
    Modification uniquement par le propriétaire.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        if hasattr(obj, 'author'):
            return obj.author == request.user
        elif hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        elif hasattr(obj, 'user'):
            return obj.user == request.user
        
        return False


class IsSeniorOrOwner(permissions.BasePermission):
    """
    Senior+ ont accès total.
    Junior uniquement à leurs propres objets.
    """
    ALLOWED_ROLES = ['senior', 'lead', 'admin']
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        if request.user.profile.role in self.ALLOWED_ROLES:
            return True
        
        if hasattr(obj, 'author'):
            return obj.author == request.user
        elif hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        elif hasattr(obj, 'user'):
            return obj.user == request.user
        
        return False