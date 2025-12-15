from django.urls import path
from django.views.generic import RedirectView

from .views import report_create_view, get_attack_types_for_chart, ReportListView, ReportDetailView, MonthlyReportView, \
    export_monthly_reports, ReportDownloadView, get_reports, analytics_view, get_risk_assessments_reports, get_countries_attacks, \
    get_static_reports_data

app_name = 'reports'   # опционально, но удобно для именованных маршрутов

urlpatterns = [
    path('',       report_create_view, name='report_new'),
    path('list/',      ReportListView.as_view(),   name='report_list'),
    path('<int:pk>/',  ReportDetailView.as_view(), name='report_detail'),
    path('analytics/', analytics_view,     name='report_analytics'),
    path('analytics-attack-types/', get_attack_types_for_chart, name='report_analytics_attacks'),
    path('analytics-risc-assessments/', get_risk_assessments_reports, name='attack_risc'),
    path('analytics-country-attacks/', get_countries_attacks, name='countries_attacks'),
    path('analytics-static-reports/', get_reports, name='static_reports'),
    path('monthly/', MonthlyReportView.as_view(), name='report_monthly'),
    path('monthly/export/', export_monthly_reports, name='report_monthly_export'),
    path('download/<int:pk>/', ReportDownloadView.as_view(), name='report_pdf'),
    # path('get_static_report/', get_reports, name='static_report'),
]