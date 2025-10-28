"""
Catalogue URL Configuration
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ItemInfoViewSet, ItemAttributeViewSet

router = DefaultRouter()
router.register(r'', ItemInfoViewSet, basename='iteminfo')

urlpatterns = [
    path('', include(router.urls)),
]