from rest_framework import permissions


class IsProjectMember(permissions.BasePermission):
    """
    Permission : L'utilisateur doit être membre du projet
    """
    def has_object_permission(self, request, view, obj):
        # obj est un Project
        return obj.members.filter(user=request.user).exists() or obj.created_by == request.user


class CanManageProject(permissions.BasePermission):
    """
    Permission : Lead ou Admin peuvent gérer les projets
    OU le créateur du projet peut le gérer
    """
    def has_object_permission(self, request, view, obj):
        # Vérifier le rôle global
        user_role = request.user.profile.role
        
        # Admin et Lead peuvent tout gérer
        if user_role in ['admin', 'lead']:
            return True
        
        # Le créateur peut gérer son propre projet
        if obj.created_by == request.user:
            return True
        
        return False