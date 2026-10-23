import base64
import json
import logging
from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.forms.models import model_to_dict
from django.http import FileResponse, HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.text import get_valid_filename
from django.views import View
from django.views.generic import DetailView, ListView, TemplateView
from docx import Document

from .forms import ReportsForm
from .models import Organization, Pattern, Report, RISK_LEVELS
from .services import analytics
from .services.cert_gov import send_report_pdf
from .services.monthly import build_monthly_rows
from .services.pdf import build_report_pdf
from .services.stat_report import create_stat_report

logger = logging.getLogger('reports')

XLSX_CONTENT_TYPE = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
DOCX_CONTENT_TYPE = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
BAD_PERIOD_MESSAGE = 'Некорректный формат даты start/end'


@login_required
def report_create_view(request):
    if request.method == 'POST':
        form = ReportsForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.user = request.user
            report.save()

            messages.success(request, 'Отчет отправлен')
            # ?download запускает скачивание PDF на странице формы
            return redirect(f"{reverse_lazy('reports:report_new')}?download={report.pk}")

        invalid_fields = [
            form.fields[name].label or name for name in form.errors if name in form.fields
        ]
        if form.non_field_errors():
            invalid_fields.append('данные формы')
        messages.error(request, 'Не удалось создать отчет. Проверьте поля: ' + ', '.join(invalid_fields))
    else:
        form = ReportsForm()

    # шаблоны отдаём в JSON для автозаполнения формы по выбранному шаблону
    patterns = {pattern.pk: model_to_dict(pattern) for pattern in Pattern.objects.all()}
    return render(request, 'reports/report_waf_form.html', {
        'pattern': json.dumps(patterns, ensure_ascii=False),
        'form': form,
    })


class ReportDownloadView(LoginRequiredMixin, View):
    def get(self, request, pk):
        report = get_object_or_404(Report, pk=pk)
        pdf = build_report_pdf(report)
        organization_name = report.organization.name_en if report.organization else 'report'
        filename = get_valid_filename(f'{report.pk}_{organization_name}_{report.source_ip}.pdf')

        send_report_pdf(report, filename, pdf)

        return FileResponse(pdf, as_attachment=True, filename=filename, content_type='application/pdf')


class ReportListView(LoginRequiredMixin, ListView):
    model = Report
    template_name = 'reports/report_list.html'
    context_object_name = 'reports'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset().order_by('-detection_date')
        start = self.request.GET.get('start')
        end = self.request.GET.get('end')
        if start and end:
            try:
                start_date = datetime.strptime(start, '%Y-%m-%d').date()
                end_date = datetime.strptime(end, '%Y-%m-%d').date()
            except ValueError:
                return qs
            qs = qs.filter(detection_date__date__gte=start_date, detection_date__date__lte=end_date)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['start'] = self.request.GET.get('start', '')
        ctx['end'] = self.request.GET.get('end', '')
        return ctx


class ReportDetailView(LoginRequiredMixin, DetailView):
    model = Report
    template_name = 'reports/report_detail.html'
    context_object_name = 'report'


def _monthly_rows(org_id, start, end):
    if not (org_id and start and end):
        return []
    try:
        return build_monthly_rows(org_id, start, end)
    except ValueError:
        return []


class MonthlyReportView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/monthly_reports.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        org_id = self.request.GET.get('org')
        start = self.request.GET.get('start')
        end = self.request.GET.get('end')

        ctx.update({
            'organizations': Organization.objects.order_by('name_en'),
            'risk_levels': RISK_LEVELS,
            'selected_org': int(org_id) if org_id else None,
            'selected_start': start,
            'selected_end': end,
            'reports': _monthly_rows(org_id, start, end),
        })
        return ctx

    def post(self, request, *args, **kwargs):
        # поля вида manual_priority_<pk> вручную меняют критичность отчёта
        prefix = 'manual_priority_'
        for key, value in request.POST.items():
            if key.startswith(prefix) and value:
                Report.objects.filter(pk=key.removeprefix(prefix)).update(risk_assessment=value)

        org = request.POST.get('org', '')
        start = request.POST.get('start', '')
        end = request.POST.get('end', '')
        return redirect(f'{request.path}?org={org}&start={start}&end={end}')


@login_required
def export_monthly_reports(request):
    org_id = request.GET.get('org')
    start = request.GET.get('start')
    end = request.GET.get('end')
    rows = _monthly_rows(org_id, start, end)

    doc = Document()
    doc.add_heading(f'Ежемесячный отчет {start}–{end}', level=1)
    table = doc.add_table(rows=1, cols=5)
    titles = ('№', 'Destination IP', 'Source IP', 'Предупреждение', 'Критичность')
    for cell, title in zip(table.rows[0].cells, titles):
        cell.text = title

    for number, row in enumerate(rows, start=1):
        cells = table.add_row().cells
        cells[0].text = str(number)
        cells[1].text = ', '.join(row['destination_ips'])
        cells[2].text = row['source_ip']
        cells[3].text = row['warning']
        cells[4].text = row['priority']

    response = HttpResponse(content_type=DOCX_CONTENT_TYPE)
    response['Content-Disposition'] = f'attachment; filename="monthly_report_{org_id}_{start}_{end}.docx"'
    doc.save(response)
    return response


@login_required
def analytics_view(request):
    return render(request, 'reports/analytics.html', {})


@login_required
def get_departments(request):
    return JsonResponse(list(Organization.objects.values_list('name_en', 'name_ru', 'pk')), safe=False)


def _period_reports(request):
    """Отчёты за период из GET-параметров department/start/end; ValueError при неверной дате."""
    return analytics.reports_for_period(
        request.GET.get('start'), request.GET.get('end'), request.GET.get('department'),
    )


def _chart_response(request, field, with_top=False, others_as_percent=False):
    """Данные для графика: количество отчётов по значениям поля `field`.

    with_top — оставить топ-10 значений, остальные свести в «Прочие».
    others_as_percent — «Прочие» отдавать долей от суммы топа в процентах
    (на это рассчитан график типов атак во фронтенде).
    """
    try:
        qs = _period_reports(request)
    except ValueError:
        return HttpResponseBadRequest(BAD_PERIOD_MESSAGE)

    rows = analytics.count_by(qs, field)
    if not rows:
        return JsonResponse({'labels': [], 'data': []})

    others = 0
    if with_top:
        rows, others = analytics.split_top(rows)

    labels = [label for label, _ in rows]
    data = [count for _, count in rows]
    total = sum(data)

    if others:
        labels.append(analytics.OTHERS_LABEL)
        data.append(round(others / total * 100, 2) if others_as_percent else others)

    return JsonResponse({
        'labels': labels,
        'data': data,
        'total': total,
        'start': request.GET.get('start'),
        'end': request.GET.get('end'),
    })


@login_required
def get_attack_types_for_chart(request):
    return _chart_response(request, 'attack_type', with_top=True, others_as_percent=True)


@login_required
def get_risk_assessments_reports(request):
    return _chart_response(request, 'risk_assessment')


@login_required
def get_countries_attacks(request):
    return _chart_response(request, 'country', with_top=True)


@login_required
def get_ip_count(request):
    try:
        qs = _period_reports(request)
    except ValueError:
        return HttpResponseBadRequest(BAD_PERIOD_MESSAGE)

    by_ip_country = qs.values('source_ip', 'country').annotate(count=Count('id')).order_by('-count')
    data = {}
    for row in by_ip_country[:analytics.TOP_LIMIT]:
        data.setdefault(row['source_ip'], []).append([row['country'], row['count']])

    return JsonResponse({
        'data': data,
        'total': qs.values('source_ip').distinct().count(),
        'start': request.GET.get('start'),
        'end': request.GET.get('end'),
    })


@login_required
def get_static_analytic_file(request):
    try:
        start = datetime.fromisoformat(request.GET['start'])
        end = datetime.fromisoformat(request.GET['end'])
    except (KeyError, ValueError):
        return HttpResponseBadRequest('Необходимы параметры start и end в формате ISO')

    reports = analytics.stats_by_user(start, end)
    output = create_stat_report(reports, start=start, end=end)

    return JsonResponse({
        'reports': reports,
        'file': {
            'filename': 'report_kcokb.xlsx',
            'content': base64.b64encode(output.getvalue()).decode('utf-8'),
            'content_type': XLSX_CONTENT_TYPE,
        },
    })
