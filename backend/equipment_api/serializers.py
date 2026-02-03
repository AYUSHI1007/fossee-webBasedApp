from rest_framework import serializers
from .models import EquipmentDataset


class EquipmentDatasetSerializer(serializers.ModelSerializer):
    class Meta:
        model = EquipmentDataset
        fields = [
            'id', 'name', 'created_at',
            'total_count', 'avg_flowrate', 'avg_pressure', 'avg_temperature',
            'type_distribution', 'raw_rows',
        ]
        read_only_fields = fields
