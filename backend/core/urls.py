from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet, NoteViewSet, CommentViewSet, TagViewSet

router = DefaultRouter()
router.register(r'projects', ProjectViewSet)
router.register(r'notes', NoteViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'tags', TagViewSet)

urlpatterns = [
    path('', include(router.urls)),  # PAS de 'api/' ici
]