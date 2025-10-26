"""
Locations Admin Configuration
"""
from django.contrib import admin
from .models import District, Mandal, Village


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ['id', 'district_name', 'district_code_ap', 'district_code_ind', 'is_active']
    list_filter = ['is_active']
    search_fields = ['district_name', 'district_code_ap', 'district_code_ind']
    ordering = ['district_name']


@admin.register(Mandal)
class MandalAdmin(admin.ModelAdmin):
    list_display = ['id', 'mandal_name', 'mandal_code_ap', 'district', 'is_active']
    list_filter = ['is_active', 'district']
    search_fields = ['mandal_name', 'mandal_code_ap', 'mandal_code_ind']
    ordering = ['district', 'mandal_name']


@admin.register(Village)
class VillageAdmin(admin.ModelAdmin):
    list_display = ['id', 'village_name', 'village_code_ap', 'mandal', 'district', 'is_active']
    list_filter = ['is_active', 'district', 'mandal']
    search_fields = ['village_name', 'village_code_ap', 'village_code_ind']
    ordering = ['district', 'mandal', 'village_name']
