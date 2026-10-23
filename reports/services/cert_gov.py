import json
import logging

import requests
from django.conf import settings

logger = logging.getLogger('reports')


def send_report_pdf(report, filename, pdf):
    """Отправляет PDF-отчёт во внешний сервис cert.gov.kg.

    Ошибки не пробрасываются: пользователь должен получить файл, даже если сервис недоступен.
    Возвращает True при успешной отправке.
    """
    if not settings.CERT_GOV_API_URL:
        logger.info('CERT_GOV_API_URL не задан, отчёт %s не отправлен', report.pk)
        return False

    pdf.seek(0)
    body = {
        'username': report.user.username if report.user else '',
        'organization': report.organization.name_ru if report.organization else '',
        'name': report.attack_type,
    }

    try:
        login_response = requests.post(
            f'{settings.CERT_GOV_API_URL}/api/token/pair',
            json={
                'email': settings.CERT_GOV_USERNAME,
                'password': settings.CERT_GOV_PASSWORD,
            },
            timeout=30,
        )
        login_response.raise_for_status()
        # ответ: {email, refresh, access}
        access_token = login_response.json()['access']

        response = requests.post(
            f'{settings.CERT_GOV_API_URL}/api/router/report-create',
            data={'body': json.dumps(body, ensure_ascii=False)},
            files={'file': (filename, pdf, 'application/pdf')},
            headers={
                'Authorization': f'Bearer {access_token}',
                'Idempotency-Key': filename,
            },
            timeout=60,
        )
        response.raise_for_status()
    except (requests.RequestException, KeyError, ValueError) as err:
        logger.error(
            'Не удалось отправить отчёт %s в cert.gov.kg: %r (ответ: %s)',
            report.pk, err, getattr(getattr(err, 'response', None), 'text', '-'),
        )
        return False
    finally:
        pdf.seek(0)

    logger.info('Отчёт %s отправлен в cert.gov.kg', report.pk)
    return True
