from django.contrib import admin
from .models import EquipmentDataset


@admin.register(EquipmentDataset)
class EquipmentDatasetAdmin(admin.ModelAdmin):
    list_display = ('name', 'total_count', 'created_at', 'uploaded_by')
    list_filter = ('created_at',)
    search_fields = ('name',)
