from django.db import models
from datetime import datetime, timedelta

RISK_LEVELS = [
    ('Критическая', 'Критическая'),
    ('Высокая', 'Высокая'),
    ('Средняя', 'Средняя'),
    ('Низкая', 'Низкая'),
]

DETECTION_TOOLS = [
    ('WAF', 'WAF'),
    ('IPS', 'IPS'),
    ('EDR', 'EDR'),
    ('SIEM', 'SIEM'),
    ('Other', 'Другое'),
]

class Organization(models.Model):
    name = models.CharField("Наименование организации", max_length=100, unique=True)

    class Meta:
        verbose_name = "Организация"
        verbose_name_plural = "Организации"

    def __str__(self):
        return self.name


class AttackType(models.Model):
    name = models.CharField("Название атаки", max_length=100, unique=True)
    description = models.TextField("Описание атаки", blank=True)
    methods = models.CharField(max_length=200, verbose_name='Методы атаки')
    detection_tool = models.CharField(
        "Средство обнаружения",
        max_length=10,
        choices=DETECTION_TOOLS
    )
    protocols_ports = models.CharField("Протоколы и порты", max_length=100, blank=True)
    risk_assessment = models.CharField(
        "Критичность",
        max_length=12,
        choices=RISK_LEVELS,
        default='Низкая'
    )
    potential_impact = models.TextField("Потенциальные последствия", blank=True)
    data = models.TextField(blank=True, null=True)
    response_actions = models.TextField("Реагирование на инцидент", blank=True)

    class Meta:
        verbose_name = "Тип атаки"
        verbose_name_plural = "Типы атак"

    def __str__(self):
        return self.name


class Report(models.Model):
    detection_date = models.DateTimeField("Дата и время выявления угрозы")
    organization = models.ForeignKey(
        Organization,
        verbose_name="Организация",
        on_delete=models.PROTECT,
    )
    attack_type = models.ForeignKey(
        AttackType,
        verbose_name="Тип угрозы",
        on_delete=models.PROTECT,
    )
    source_ip = models.GenericIPAddressField("Источник угрозы")
    destination_ip = models.GenericIPAddressField("Адрес назначения")
    detection_tool = models.CharField("Средство обнаружения", max_length=10, choices=DETECTION_TOOLS)
    cve = models.CharField(max_length=50, null=True, blank=True)
    host = models.CharField(max_length=50, null=True, blank=True)
    short_description = models.TextField("Краткое описание")
    methods = models.CharField("Методы атаки", max_length=200, blank=True)
    protocols_ports = models.CharField("Протоколы и порты", max_length=200, blank=True)
    potential_impact = models.TextField("Потенциальные последствия", blank=True)
    risk_assessment = models.CharField('Критичность', max_length=120)
    data_or_payload = models.TextField("Дата или payload", blank=True)
    response_actions = models.TextField("Реагирование на инцидент", blank=True)


# class ReportIPS(models.Model):
#     detection_date = models.CharField("Дата и время выявления угрозы")
#     organization = models.ForeignKey(
#         Organization,
#         verbose_name="Организация",
#         on_delete=models.PROTECT,
#     )
#     attack_type = models.ForeignKey(
#         AttackType,
#         verbose_name="Тип угрозы",
#         on_delete=models.PROTECT,
#     )
#     source_ip = models.GenericIPAddressField("Источник угрозы")
#     destination_ip = models.GenericIPAddressField("Адрес назначения")
#     short_description = models.TextField("Краткое описание")
#     methods = models.CharField("Методы атаки", max_length=200, blank=True)
#     protocols_ports = models.CharField("Протоколы и порты", max_length=200, blank=True)
#     potential_impact = models.TextField("Потенциальные последствия", blank=True)
#     risk_assessment = models.CharField('Критичность', max_length=120)
#     payload = models.TextField()
#     response_actions = models.TextField("Реагирование на инцидент", blank=True)