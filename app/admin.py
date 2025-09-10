# admin.py
from django.contrib import admin
from .models import PollingUnit, VoteAllocation, AllocatedResult

@admin.register(PollingUnit)
class PollingUnitAdmin(admin.ModelAdmin):
    list_display = ['sno', 'state', 'lga', 'delim', 'pvc_45_percent']
    list_filter = ['state', 'lga']
    search_fields = ['state', 'lga', 'delim']
    ordering = ['sno']

@admin.register(VoteAllocation)
class VoteAllocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'total_percentage', 'is_valid_allocation', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']

@admin.register(AllocatedResult)
class AllocatedResultAdmin(admin.ModelAdmin):
    list_display = ['polling_unit', 'vote_allocation', 'total_votes']
    list_filter = ['vote_allocation', 'polling_unit__state']
    search_fields = ['polling_unit__delim', 'vote_allocation__name']