"""
Catalogue Views
"""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from .models import ItemInfo
from .serializers import ItemInfoSerializer


class ItemInfoViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Item Catalogue (ItemInfo)
    """
    queryset = ItemInfo.objects.all()
    serializer_class = ItemInfoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['active', 'category', 'resource_type', 'perishability', 'item_code']
    search_fields = ['item_name', 'item_code', 'category', 'tags', 'activity_name']
    ordering_fields = ['id', 'item_name', 'item_code']
    ordering = ['item_name']
