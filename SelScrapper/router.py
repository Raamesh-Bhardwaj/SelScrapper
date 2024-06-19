from rest_framework.routers import DefaultRouter

from api.views.Entities import EntitiesViewSet

router = DefaultRouter()
router.register("", EntitiesViewSet, "entities")
