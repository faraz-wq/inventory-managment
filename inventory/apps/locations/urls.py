"""
Locations URL Configuration
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DistrictViewSet, MandalViewSet, VillageViewSet

router = DefaultRouter()
router.register(r'districts', DistrictViewSet, basename='district')
router.register(r'mandals', MandalViewSet, basename='mandal')
router.register(r'villages', VillageViewSet, basename='village')

urlpatterns = [
    path('', include(router.urls)),
]
