from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet

# Router DRF pour générer automatiquement les URLs CRUD
router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='project')

urlpatterns = [
    path('', include(router.urls)),
]