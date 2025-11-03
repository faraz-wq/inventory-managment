"""
Location Views
"""
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import District, Mandal, Village
from .serializers import (
    DistrictSerializer,
    MandalSerializer,
    VillageSerializer,
    VillageDetailSerializer,
)


class DistrictViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Districts
    """
    queryset = District.objects.all()
    serializer_class = DistrictSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'district_code_ap']
    search_fields = ['district_name', 'district_code_ap', 'district_code_ind']
    ordering_fields = ['id', 'district_name']
    ordering = ['district_name']

    @swagger_auto_schema(
        operation_summary='List districts',
        tags=['Locations – Districts'],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Create a district',
        request_body=DistrictSerializer,
        responses={201: DistrictSerializer},
        tags=['Locations – Districts'],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Retrieve a district',
        responses={200: DistrictSerializer},
        tags=['Locations – Districts'],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Update a district',
        request_body=DistrictSerializer,
        responses={200: DistrictSerializer},
        tags=['Locations – Districts'],
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Partial update of a district',
        request_body=DistrictSerializer,
        responses={200: DistrictSerializer},
        tags=['Locations – Districts'],
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Delete a district',
        tags=['Locations – Districts'],
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class MandalViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Mandals
    """
    queryset = Mandal.objects.select_related('district').all()
    serializer_class = MandalSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'district', 'mandal_code_ap']
    search_fields = ['mandal_name', 'mandal_code_ap', 'mandal_code_ind']
    ordering_fields = ['id', 'mandal_name']
    ordering = ['district', 'mandal_name']

    @swagger_auto_schema(
        operation_summary='List mandals',
        tags=['Locations – Mandals'],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Create a mandal',
        request_body=MandalSerializer,
        responses={201: MandalSerializer},
        tags=['Locations – Mandals'],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Retrieve a mandal',
        responses={200: MandalSerializer},
        tags=['Locations – Mandals'],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Update a mandal',
        request_body=MandalSerializer,
        responses={200: MandalSerializer},
        tags=['Locations – Mandals'],
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Partial update of a mandal',
        request_body=MandalSerializer,
        responses={200: MandalSerializer},
        tags=['Locations – Mandals'],
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Delete a mandal',
        tags=['Locations – Mandals'],
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class VillageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Villages
    """
    queryset = Village.objects.select_related('district', 'mandal').all()
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'district', 'mandal', 'village_code_ap']
    search_fields = ['village_name', 'village_code_ap', 'village_code_ind']
    ordering_fields = ['id', 'village_name']
    ordering = ['district', 'mandal', 'village_name']

    def get_serializer_class(self):
        return VillageDetailSerializer if self.action == 'retrieve' else VillageSerializer

    @swagger_auto_schema(
        operation_summary='List villages',
        tags=['Locations – Villages'],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Create a village',
        request_body=VillageSerializer,
        responses={201: VillageSerializer},
        tags=['Locations – Villages'],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Retrieve a village (includes nested mandal/district)',
        responses={200: VillageDetailSerializer},
        tags=['Locations – Villages'],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Update a village',
        request_body=VillageSerializer,
        responses={200: VillageSerializer},
        tags=['Locations – Villages'],
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Partial update of a village',
        request_body=VillageSerializer,
        responses={200: VillageSerializer},
        tags=['Locations – Villages'],
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='Delete a village',
        tags=['Locations – Villages'],
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)