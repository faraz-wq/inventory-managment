"""
Location Views
"""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from .models import District, Mandal, Village
from .serializers import (
    DistrictSerializer,
    MandalSerializer,
    VillageSerializer,
    VillageDetailSerializer
)


class DistrictViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Districts
    """
    queryset = District.objects.all()
    serializer_class = DistrictSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'district_code_ap']
    search_fields = ['district_name', 'district_code_ap', 'district_code_ind']
    ordering_fields = ['id', 'district_name']
    ordering = ['district_name']


class MandalViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Mandals
    """
    queryset = Mandal.objects.select_related('district').all()
    serializer_class = MandalSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'district', 'mandal_code_ap']
    search_fields = ['mandal_name', 'mandal_code_ap', 'mandal_code_ind']
    ordering_fields = ['id', 'mandal_name']
    ordering = ['district', 'mandal_name']


class VillageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Villages
    """
    queryset = Village.objects.select_related('district', 'mandal').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'district', 'mandal', 'village_code_ap']
    search_fields = ['village_name', 'village_code_ap', 'village_code_ind']
    ordering_fields = ['id', 'village_name']
    ordering = ['district', 'mandal', 'village_name']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return VillageDetailSerializer
        return VillageSerializer
