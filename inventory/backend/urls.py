"""
URL configuration for Asset Verification & Management System.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Swagger/OpenAPI Schema
schema_view = get_schema_view(
    openapi.Info(
        title="Asset Verification & Management API",
        default_version='v1',
        description="RESTful API for managing departments, users, roles, permissions, and physical assets with geographic tracking",
        terms_of_service="https://www.yourapp.com/terms/",
        contact=openapi.Contact(email="contact@assetmanagement.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # API Documentation
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # App URLs
    path('api/auth/', include('apps.users.urls')),
    path('api/users/', include('apps.users.urls')),
    path('api/departments/', include('apps.departments.urls')),
    path('api/rbac/', include('apps.rbac.urls')),
    path('api/items/', include('apps.items.urls')),
    path('api/catalogue/', include('apps.catalogue.urls')),
    path('api/locations/', include('apps.locations.urls')),
    path('api/logs/', include('apps.logs.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
