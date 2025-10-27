"""
Items URL Configuration - CORRECTED
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ItemViewSet

router = DefaultRouter()
router.register(r'', ItemViewSet, basename='item')

# Additional URL patterns for attribute actions that can't be handled by the router
# due to conflicting HTTP methods on the same URL path
additional_patterns = [
    path(
        '<int:pk>/attributes/',
        ItemViewSet.as_view({
            'get': 'list_attributes',
            'post': 'add_attribute'
        }),
        name='item-attributes'
    ),
]

urlpatterns = [
    path('', include(router.urls)),
    path('', include(additional_patterns)),
]