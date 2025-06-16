from django.urls import path
from django.views.generic import RedirectView

from .views import report_create_view, AnalyticsView, ReportListView, ReportDetailView, MonthlyReportView, \
    export_monthly_reports, ReportDownloadView, get_reports

app_name = 'reports'   # опционально, но удобно для именованных маршрутов

urlpatterns = [
    path('',       report_create_view, name='report_new'),
    path('list/',      ReportListView.as_view(),   name='report_list'),
    path('<int:pk>/',  ReportDetailView.as_view(), name='report_detail'),
    path('analytics/', AnalyticsView.as_view(),     name='report_analytics'),
    path('monthly/', MonthlyReportView.as_view(), name='report_monthly'),
    path('monthly/export/', export_monthly_reports, name='report_monthly_export'),
    path('download/<int:pk>/', ReportDownloadView.as_view(), name='report_pdf'),
    path('get_static_report/', get_reports, name='static_report')
]