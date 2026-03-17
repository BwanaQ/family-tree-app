from rest_framework.routers import DefaultRouter
from .views import PersonViewSet, RelationshipViewSet

router = DefaultRouter()
router.register(r'persons', PersonViewSet)
router.register(r'relationships', RelationshipViewSet)

urlpatterns = router.urls