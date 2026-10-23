from collections import defaultdict
from datetime import date, datetime, time

from django.db.models import Count
from django.utils import timezone

from ..models import Report

TOP_LIMIT = 10
OTHERS_LABEL = 'Прочие'


def parse_period(start, end):
    """Превращает строки start/end (ISO) в границы периода; без дат — текущий день.

    Дата без времени в end означает конец этого дня. Некорректная строка -> ValueError.
    """
    today = timezone.localdate()
    start_dt = _parse_boundary(start, today, time.min)
    end_dt = _parse_boundary(end, today, time.max)
    return start_dt, end_dt


def _parse_boundary(value, default_day, default_time):
    if not value:
        parsed = datetime.combine(default_day, default_time)
    else:
        parsed = datetime.fromisoformat(value)
        if len(value) <= 10:  # только дата
            parsed = datetime.combine(parsed.date(), default_time)
    return timezone.make_aware(parsed) if timezone.is_naive(parsed) else parsed


def reports_for_period(start=None, end=None, department=None):
    start_dt, end_dt = parse_period(start, end)
    qs = Report.objects.filter(detection_date__range=(start_dt, end_dt))
    if department:
        qs = qs.filter(organization=department)
    return qs


def count_by(qs, field):
    """[(значение поля, количество)], по убыванию количества."""
    rows = qs.values(field).annotate(count=Count('id')).order_by('-count')
    return [(row[field], row['count']) for row in rows]


def split_top(rows, limit=TOP_LIMIT):
    """Возвращает (топ-N строк, сумма остальных)."""
    return rows[:limit], sum(count for _, count in rows[limit:])


def stats_by_user(start, end):
    """{username: {organization.name_en: {risk_assessment: count}}} за период."""
    rows = (
        Report.objects
        .filter(detection_date__range=(start, end))
        .values('user__username', 'organization__name_en', 'risk_assessment')
        .annotate(count=Count('id'))
    )
    result = defaultdict(lambda: defaultdict(dict))
    for row in rows:
        result[row['user__username']][row['organization__name_en']][row['risk_assessment']] = row['count']
    return result
