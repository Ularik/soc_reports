# Generated by Django 5.2.1 on 2025-06-23 11:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='report',
            name='pattern',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='reports.pattern', verbose_name='Шаблон'),
        ),
    ]
