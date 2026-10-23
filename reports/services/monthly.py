from datetime import datetime, time

from ..models import RISK_LEVELS, Report


def build_monthly_rows(org_id, start, end):
    """Сводка по source_ip за период для организации.

    Для каждого IP берётся запись с наивысшей критичностью (порядок RISK_LEVELS),
    при равенстве — самая ранняя. Некорректные даты -> ValueError.
    """
    start_dt = datetime.combine(datetime.strptime(start, '%Y-%m-%d').date(), time.min)
    end_dt = datetime.combine(datetime.strptime(end, '%Y-%m-%d').date(), time.max)

    qs = Report.objects.filter(
        organization_id=org_id,
        detection_date__gte=start_dt,
        detection_date__lte=end_dt,
    )

    rows = []
    for source_ip in qs.values_list('source_ip', flat=True).distinct():
        group = qs.filter(source_ip=source_ip)
        rec = next(
            (r for level, _ in RISK_LEVELS
             if (r := group.filter(risk_assessment=level).order_by('detection_date').first())),
            None,
        ) or group.order_by('detection_date').first()
        rows.append({
            'rec': rec,
            'destination_ips': list(group.values_list('destination_ip', flat=True).distinct()),
            'source_ip': source_ip,
            'warning': rec.attack_type,
            'priority': rec.risk_assessment,
            'requests': group.count(),
        })
    return rows
