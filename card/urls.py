from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CardViewSet, UserViewSet

router = DefaultRouter()
router.register(r"cards", CardViewSet)
router.register(r"users", UserViewSet)

urlpatterns = [
    path("api/", include(router.urls)),
]