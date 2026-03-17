from rest_framework.routers import DefaultRouter
from .views import PersonViewSet, FamilyUnionViewSet, ParentChildViewSet

router = DefaultRouter()
router.register(r'persons', PersonViewSet)
router.register(r'unions', FamilyUnionViewSet)
router.register(r'parent-child', ParentChildViewSet)

urlpatterns = router.urls