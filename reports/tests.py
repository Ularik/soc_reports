from datetime import datetime
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase, override_settings

from .models import Report
from .views import _build_report_pdf, _ensure_report_pdf


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

        pdf = _build_report_pdf(report)

        self.assertTrue(pdf.getvalue().startswith(b'%PDF-'))

    def test_report_pdf_is_persisted_and_reused(self):
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

        with TemporaryDirectory() as media_root:
            with override_settings(MEDIA_ROOT=media_root):
                with patch.object(report, 'save') as save_report:
                    first_pdf = _ensure_report_pdf(report)
                    file_name = report.pdf_file.name
                    self.assertTrue(report.pdf_file.storage.exists(file_name))

                    second_pdf = _ensure_report_pdf(report)

        self.assertEqual(first_pdf.getvalue(), second_pdf.getvalue())
        save_report.assert_called_once()
