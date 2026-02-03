"""
Store last 5 uploaded datasets with summary (FIFO).
"""
from django.db import models
from django.conf import settings


class EquipmentDataset(models.Model):
    """One uploaded CSV dataset with stored summary."""
    name = models.CharField(max_length=255, default='Untitled')
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    # Summary (JSON-friendly)
    total_count = models.PositiveIntegerField(default=0)
    avg_flowrate = models.FloatField(null=True, blank=True)
    avg_pressure = models.FloatField(null=True, blank=True)
    avg_temperature = models.FloatField(null=True, blank=True)
    type_distribution = models.JSONField(default=dict)  # {"Reactor": 3, "Pump": 2, ...}
    raw_rows = models.JSONField(default=list)  # list of dicts for table display

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.created_at})"
