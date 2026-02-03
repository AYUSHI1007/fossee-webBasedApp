from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.CSVUploadView.as_view(), name='upload'),
    path('summary/<int:dataset_id>/', views.SummaryView.as_view(), name='summary'),
    path('history/', views.HistoryListView.as_view(), name='history'),
    path('report/<int:dataset_id>/pdf/', views.PDFReportView.as_view(), name='report-pdf'),
]
