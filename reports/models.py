from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


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
    name_en = models.CharField("Наименование организации анг", max_length=100, unique=True)
    name_ru = models.CharField("Наименование организации", max_length=100, unique=True)

    class Meta:
        verbose_name = "Организация"
        verbose_name_plural = "Организации"

    def __str__(self):
        return self.name_ru


class Pattern(models.Model):
    name = models.CharField("Название шаблона", max_length=100)
    attack_type = models.CharField("Название атаки", max_length=100, null=True, blank=True)
    description = models.TextField("Описание атаки",  null=True, blank=True)
    methods = models.CharField(max_length=200, verbose_name='Методы атаки',  null=True, blank=True)
    detection_tool = models.CharField(
        "Средство обнаружения",
        max_length=10,
        choices=DETECTION_TOOLS,
        null=True, blank=True
    )
    protocols_ports = models.CharField("Протоколы и порты", max_length=100, blank=True)
    risk_assessment = models.CharField(
        "Критичность",
        max_length=12,
        choices=RISK_LEVELS,
        default='Низкая',
    )
    potential_impact = models.TextField("Потенциальные последствия", null=True, blank=True)
    data_or_payload = models.TextField(blank=True, null=True)
    response_actions = models.TextField("Реагирование на инцидент", null=True, blank=True)

    class Meta:
        verbose_name = "Шаблон"
        verbose_name_plural = "Шаблоны"

    def __str__(self):
        return self.name


class Report(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='Пользователь', null=True, blank=True)
    detection_date = models.DateTimeField("Дата и время выявления угрозы")
    organization = models.ForeignKey(
        Organization,
        verbose_name="Организация",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    pattern = models.ForeignKey(
        Pattern,
        verbose_name="Шаблон",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    attack_type = models.CharField("Название атаки", max_length=100, null=True, blank=True)
    source_ip = models.GenericIPAddressField("Источник угрозы")
    destination_ip = models.GenericIPAddressField("Адрес назначения")
    detection_tool = models.CharField("Средство обнаружения", max_length=10, choices=DETECTION_TOOLS)
    cve = models.CharField(max_length=50, null=True, blank=True)
    host = models.CharField(max_length=50, null=True, blank=True)
    short_description = models.TextField("Краткое описание")
    methods = models.CharField("Методы атаки", max_length=200, blank=True)
    protocols_ports = models.CharField("Протоколы и порты", max_length=200, blank=True)
    potential_impact = models.TextField("Потенциальные последствия", blank=True)
    risk_assessment = models.CharField("Критичность", max_length=12, choices=RISK_LEVELS, default='Низкая')
    data_or_payload = models.TextField("Дата или payload", blank=True)
    response_actions = models.TextField("Реагирование на инцидент", blank=True)
