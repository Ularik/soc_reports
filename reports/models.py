from django.db import models
from datetime import datetime, timedelta


class Organization(models.Model):
    name = models.CharField("Наименование организации", max_length=100, unique=True)

    class Meta:
        verbose_name = "Организация"
        verbose_name_plural = "Организации"

    def __str__(self):
        return self.name


class AttackType(models.Model):
    name = models.CharField("Название атаки", max_length=100, unique=True)
    cve = models.CharField("CVE", max_length=50, blank=True, null=True)
    description = models.TextField("Описание атаки", blank=True)
    #recommended_measures = models.TextField("Рекомендованные меры", blank=True)

    class Meta:
        verbose_name = "Тип атаки"
        verbose_name_plural = "Типы атак"

    def __str__(self):
        return self.name


class Report(models.Model):
    RISK_LEVELS = [
        ('Критическая', 'Критическая'),
        ('Высокая',      'Высокая'),
        ('Средняя',      'Средняя'),
        ('Низкая',       'Низкая'),
    ]

    DETECTION_TOOLS = [
        ('WAF', 'WAF'),
        ('IPS', 'IPS'),
        ('EDR', 'EDR'),
        ('SIEM', 'SIEM'),
        ('Other', 'Другое'),
    ]

    organization = models.ForeignKey(
        Organization,
        verbose_name="Организация",
        on_delete=models.PROTECT,
        related_name="reports"
    )
    # detection_date = models.DateField("Дата выявления угрозы")
    detection_date = models.DateTimeField("Дата и время выявления угрозы")
    attack_type = models.ForeignKey(
        AttackType,
        verbose_name="Тип угрозы",
        on_delete=models.PROTECT,
        related_name="reports"
    )
    source_ip = models.GenericIPAddressField("Источник угрозы")
    destination_ip = models.GenericIPAddressField("Адрес назначения")
    detection_tool = models.CharField(
        "Средство обнаружения",
        max_length=10,
        choices=DETECTION_TOOLS
    )
    risk_assessment = models.CharField(
        "Критичность",
        max_length=12,
        choices=RISK_LEVELS,
        default='Низкая'
    )
    short_description = models.TextField("Краткое описание")
    methods = models.CharField("Методы атаки", max_length=200, blank=True)
    protocols_ports = models.CharField("Протоколы и порты", max_length=200, blank=True)
    potential_impact = models.TextField("Потенциальные последствия", blank=True)
    payload = models.TextField("Payload", blank=True)
    response_actions = models.TextField("Реагирование на инцидент", blank=True)

    class Meta:
        verbose_name = "Отчет"
        verbose_name_plural = "Отчеты"

    def __str__(self):
        return f"{self.attack_type.name} – {self.detection_date.strftime('%Y-%m-%d')} ({self.organization})"
