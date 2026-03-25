from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register('trees', TreeViewSet)
router.register('persons', PersonViewSet)
router.register('unions', FamilyUnionViewSet)
router.register('parent-child', ParentChildViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('relationship/', RelationshipView.as_view(), name='relationship'),
]