from datetime import datetime
from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase
from django.urls import reverse

from .models import Report
from .forms import ReportsForm
from .services import analytics
from .services.pdf import build_report_pdf


class ReportPdfGenerationTests(SimpleTestCase):
    def test_report_pdf_handles_markup_characters_and_empty_optional_fields(self):
        report = SimpleNamespace(
            detection_date=datetime(2026, 10, 22),
            attack_type='Attack & <details>',
            source_ip='192.0.2.1',
            destination_ip='192.0.2.2',
            detection_tool='WAF',
            short_description='Description with <tags> & symbols',
            methods='',
            protocols_ports='',
            risk_assessment='Низкая',
            potential_impact='',
            host='example.test',
            data_or_payload='',
            response_actions='First line\nSecond line',
            cve='',
        )

        pdf = build_report_pdf(report)

        self.assertTrue(pdf.getvalue().startswith(b'%PDF-'))

    def test_report_pdf_is_generated_without_persisting_a_file(self):
        report = Report(
            pk=123,
            detection_date=datetime(2026, 10, 22),
            attack_type='Test attack',
            source_ip='192.0.2.1',
            destination_ip='192.0.2.2',
            detection_tool='WAF',
            short_description='Test description',
            organization=None,
        )

        pdf = build_report_pdf(report)

        self.assertTrue(pdf.getvalue().startswith(b'%PDF-'))
        self.assertFalse(report.pdf_file.name)

    def test_missing_required_fields_are_reported_by_the_bound_form(self):
        with patch('reports.forms.Pattern.objects.all', return_value=[]):
            form = ReportsForm(data={})

        self.assertFalse(form.is_valid())
        self.assertIn('detection_date', form.errors)
        self.assertIn('source_ip', form.errors)
        self.assertIn('destination_ip', form.errors)
        self.assertIn('detection_tool', form.errors)
        self.assertIn('short_description', form.errors)


class AnalyticsPeriodTests(SimpleTestCase):
    def test_date_only_end_covers_the_whole_day(self):
        start, end = analytics.parse_period('2026-10-01', '2026-10-02')

        self.assertEqual((start.hour, start.minute), (0, 0))
        self.assertEqual((end.day, end.hour, end.minute), (2, 23, 59))

    def test_invalid_date_raises_value_error(self):
        with self.assertRaises(ValueError):
            analytics.parse_period('not-a-date', None)

    def test_split_top_sums_the_rest(self):
        rows = [(f'a{i}', 1) for i in range(12)]

        top, others = analytics.split_top(rows)

        self.assertEqual(len(top), 10)
        self.assertEqual(others, 2)


class LoginRequiredTests(SimpleTestCase):
    def test_anonymous_user_is_redirected_to_login(self):
        for name in ('reports:report_list', 'reports:report_analytics', 'reports:attack_risc',
                     'reports:report_monthly', 'reports:report_monthly_export'):
            response = self.client.get(reverse(name))

            self.assertEqual(response.status_code, 302, name)
            self.assertTrue(response['Location'].startswith('/user/login/'), name)
