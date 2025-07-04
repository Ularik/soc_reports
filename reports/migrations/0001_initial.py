# Generated by Django 5.2.1 on 2025-06-16 12:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_en', models.CharField(max_length=100, unique=True, verbose_name='Наименование организации анг')),
                ('name_ru', models.CharField(max_length=100, unique=True, verbose_name='Наименование организации')),
            ],
            options={
                'verbose_name': 'Организация',
                'verbose_name_plural': 'Организации',
            },
        ),
        migrations.CreateModel(
            name='Pattern',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Название шаблона')),
                ('attack_type', models.CharField(max_length=100, verbose_name='Название атаки')),
                ('description', models.TextField(blank=True, verbose_name='Описание атаки')),
                ('methods', models.CharField(max_length=200, verbose_name='Методы атаки')),
                ('detection_tool', models.CharField(choices=[('WAF', 'WAF'), ('IPS', 'IPS'), ('EDR', 'EDR'), ('SIEM', 'SIEM'), ('Other', 'Другое')], max_length=10, verbose_name='Средство обнаружения')),
                ('protocols_ports', models.CharField(blank=True, max_length=100, verbose_name='Протоколы и порты')),
                ('risk_assessment', models.CharField(choices=[('Критическая', 'Критическая'), ('Высокая', 'Высокая'), ('Средняя', 'Средняя'), ('Низкая', 'Низкая')], default='Низкая', max_length=12, verbose_name='Критичность')),
                ('potential_impact', models.TextField(blank=True, verbose_name='Потенциальные последствия')),
                ('data_or_payload', models.TextField(blank=True, null=True)),
                ('response_actions', models.TextField(blank=True, verbose_name='Реагирование на инцидент')),
            ],
            options={
                'verbose_name': 'Шаблон',
                'verbose_name_plural': 'Шаблоны',
            },
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('detection_date', models.DateTimeField(verbose_name='Дата и время выявления угрозы')),
                ('attack_type', models.CharField(blank=True, max_length=100, null=True, verbose_name='Название атаки')),
                ('source_ip', models.GenericIPAddressField(verbose_name='Источник угрозы')),
                ('destination_ip', models.GenericIPAddressField(verbose_name='Адрес назначения')),
                ('detection_tool', models.CharField(choices=[('WAF', 'WAF'), ('IPS', 'IPS'), ('EDR', 'EDR'), ('SIEM', 'SIEM'), ('Other', 'Другое')], max_length=10, verbose_name='Средство обнаружения')),
                ('cve', models.CharField(blank=True, max_length=50, null=True)),
                ('host', models.CharField(blank=True, max_length=50, null=True)),
                ('short_description', models.TextField(verbose_name='Краткое описание')),
                ('methods', models.CharField(blank=True, max_length=200, verbose_name='Методы атаки')),
                ('protocols_ports', models.CharField(blank=True, max_length=200, verbose_name='Протоколы и порты')),
                ('potential_impact', models.TextField(blank=True, verbose_name='Потенциальные последствия')),
                ('risk_assessment', models.CharField(max_length=120, verbose_name='Критичность')),
                ('data_or_payload', models.TextField(blank=True, verbose_name='Дата или payload')),
                ('response_actions', models.TextField(blank=True, verbose_name='Реагирование на инцидент')),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='reports.organization', verbose_name='Организация')),
                ('pattern', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='reports.pattern', verbose_name='Шаблон')),
            ],
        ),
    ]
