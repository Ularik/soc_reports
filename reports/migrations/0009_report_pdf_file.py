from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0008_report_country'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='pdf_file',
            field=models.FileField(blank=True, upload_to='reports/pdfs/', verbose_name='PDF отчет'),
        ),
    ]
