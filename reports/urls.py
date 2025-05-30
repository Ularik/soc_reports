from django.urls import path
from django.views.generic import RedirectView

from .views import ReportCreateView, AnalyticsView, ReportListView, ReportDetailView, MonthlyReportView, \
    export_monthly_reports, ReportDownloadView

app_name = 'reports'   # опционально, но удобно для именованных маршрутов

urlpatterns = [
    path(
        '',
        RedirectView.as_view(pattern_name='reports:report_new', permanent=False),
        name='index'
    ),
    path('new/',       ReportCreateView.as_view(), name='report_new'),
    path('list/',      ReportListView.as_view(),   name='report_list'),
    path('<int:pk>/',  ReportDetailView.as_view(), name='report_detail'),
    path('analytics/', AnalyticsView.as_view(),     name='report_analytics'),
    path('monthly/', MonthlyReportView.as_view(), name='report_monthly'),
    path('monthly/export/', export_monthly_reports, name='report_monthly_export'),
    path('new/download/<int:pk>/', ReportDownloadView.as_view(), name='report_pdf'),

]