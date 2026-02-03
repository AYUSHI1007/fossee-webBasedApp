"""
API views: CSV upload, summary, history (last 5), PDF report.
"""
from django.http import HttpResponse
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import EquipmentDataset
from .serializers import EquipmentDatasetSerializer
from .services import parse_and_analyze
from .pdf_report import build_pdf_report

MAX_STORED_DATASETS = 5


def trim_to_last_n(user=None):
    """Keep only last MAX_STORED_DATASETS for this user (or global if no user)."""
    qs = EquipmentDataset.objects.all()
    if user and user.is_authenticated:
        qs = qs.filter(uploaded_by=user)
    qs = qs.order_by('-created_at')
    to_delete = list(qs[MAX_STORED_DATASETS:].values_list('id', flat=True))
    if to_delete:
        EquipmentDataset.objects.filter(id__in=to_delete).delete()


class CSVUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        file_obj = request.FILES.get('file') or request.data.get('file')
        if not file_obj:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
        name = request.data.get('name', file_obj.name or 'Untitled')

        try:
            summary = parse_and_analyze(file_obj)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        dataset = EquipmentDataset(
            name=name,
            uploaded_by=request.user if request.user.is_authenticated else None,
            total_count=summary['total_count'],
            avg_flowrate=summary.get('avg_flowrate'),
            avg_pressure=summary.get('avg_pressure'),
            avg_temperature=summary.get('avg_temperature'),
            type_distribution=summary.get('type_distribution', {}),
            raw_rows=summary.get('raw_rows', []),
        )
        dataset.save()
        trim_to_last_n(request.user)

        serializer = EquipmentDatasetSerializer(dataset)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SummaryView(APIView):
    """Get summary for a dataset by id."""

    def get(self, request, dataset_id):
        try:
            dataset = EquipmentDataset.objects.get(pk=dataset_id)
        except EquipmentDataset.DoesNotExist:
            return Response({'error': 'Dataset not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = EquipmentDatasetSerializer(dataset)
        return Response(serializer.data)


class HistoryListView(APIView):
    """List last 5 uploaded datasets."""

    def get(self, request):
        qs = EquipmentDataset.objects.all().order_by('-created_at')[:MAX_STORED_DATASETS]
        serializer = EquipmentDatasetSerializer(qs, many=True)
        return Response(serializer.data)


class PDFReportView(APIView):
    """Download PDF report for a dataset."""

    def get(self, request, dataset_id):
        try:
            dataset = EquipmentDataset.objects.get(pk=dataset_id)
        except EquipmentDataset.DoesNotExist:
            return Response({'error': 'Dataset not found'}, status=status.HTTP_404_NOT_FOUND)
        pdf_bytes = build_pdf_report(dataset)
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="equipment_report_{dataset_id}.pdf"'
        return response
