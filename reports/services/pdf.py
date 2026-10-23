import os
from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFError, TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

FONT_NAME = 'TimesNewRoman'
FONT_PATHS = (
    r'/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf',
    r'/usr/share/fonts/truetype/liberation2/LiberationSerif-Regular.ttf',
    r'C:\Windows\Fonts\times.ttf',
    r'C:\Windows\Fonts\arial.ttf',
)


def _register_font():
    """Регистрирует шрифт с кириллицей; без него остаётся Times-Roman (кириллица не отобразится)."""
    try:
        pdfmetrics.getFont(FONT_NAME)
        return FONT_NAME
    except KeyError:
        pass

    for font_path in FONT_PATHS:
        if os.path.isfile(font_path):
            try:
                pdfmetrics.registerFont(TTFont(FONT_NAME, font_path))
                return FONT_NAME
            except (OSError, TTFError):
                continue

    return 'Times-Roman'


def _paragraph(value, style, multiline=False):
    text = escape(str(value or ''))
    if multiline:
        text = text.replace('\r\n', '\n').replace('\r', '\n').replace('\n', '<br/>')
    return Paragraph(text, style)


def build_report_pdf(report):
    """Возвращает BytesIO с PDF-отчётом по инциденту."""
    font_name = _register_font()
    styles = getSampleStyleSheet()
    styles['Title'].fontName = font_name
    styles['Normal'].fontName = font_name
    cell = ParagraphStyle('CellStyle', fontName=font_name, fontSize=10, leading=12, wordWrap='LTR')

    def row(label, value, multiline=False):
        return [_paragraph(label, cell), _paragraph(value, cell, multiline)]

    data = [
        row("Поле", "Значение"),
        row("Дата и время", report.detection_date.strftime('%Y-%m-%d')),
        row("Тип угрозы", report.attack_type),
        row("Источник угрозы", report.source_ip),
        row("Адрес назначения", report.destination_ip),
        row("Средство обнаружения", report.detection_tool),
        row("Краткое описание", report.short_description, multiline=True),
        row("Методы атаки", report.methods),
        row("Протоколы и порты", report.protocols_ports),
        row("Критичность", report.risk_assessment),
        row("Потенциальные последствия", report.potential_impact, multiline=True),
        row("Payload" if report.host else "Data", report.data_or_payload, multiline=True),
        row("Реагирование на инцидент", report.response_actions, multiline=True),
    ]
    if report.detection_tool == 'WAF' and report.host:
        data.insert(4, row("Host", report.host))
    elif report.detection_tool == 'IPS' and report.cve:
        data.insert(4, row("CVE", report.cve))

    table = Table(data, colWidths=[150, 330])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f0f0')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=40, leftMargin=40,
        topMargin=60, bottomMargin=40,
    )
    doc.build([
        _paragraph("Отчет по выявлению аномалий средствами SOC", styles['Title']),
        Spacer(1, 12),
        table,
    ])
    buffer.seek(0)
    return buffer
