"""
Users URL Configuration
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import UserViewSet
from .views import RegisterView

router = DefaultRouter()
router.register(r'', UserViewSet, basename='user')

urlpatterns = [
    # JWT Authentication
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # Public registration
    path('register/', RegisterView.as_view(), name='user_register'),

    # User endpoints
    path('', include(router.urls)),
]
