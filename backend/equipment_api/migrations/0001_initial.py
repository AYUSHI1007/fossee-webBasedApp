# Generated migration for EquipmentDataset

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='EquipmentDataset',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='Untitled', max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('total_count', models.PositiveIntegerField(default=0)),
                ('avg_flowrate', models.FloatField(blank=True, null=True)),
                ('avg_pressure', models.FloatField(blank=True, null=True)),
                ('avg_temperature', models.FloatField(blank=True, null=True)),
                ('type_distribution', models.JSONField(default=dict)),
                ('raw_rows', models.JSONField(default=list)),
                ('uploaded_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
