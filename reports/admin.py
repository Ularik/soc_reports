from django.contrib import admin
from .models import Pattern, Report, Organization
from django import forms



class PatternForm(forms.ModelForm):
    class Meta:
        model = Pattern
        fields = '__all__'

    def clean_name(self):
        name = self.cleaned_data['name'].strip()
        qs = Pattern.objects.filter(name__iexact=name)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(
                "Шаблон с таким названием уже существует."
            )
        return name


@admin.register(Pattern)
class PatternAdmin(admin.ModelAdmin):
    form = PatternForm
    list_display = ('id', 'name',)
    search_fields = ('id', 'name',)


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = (
        'detection_date',
        'pattern',
        'attack_type',
        'organization__name_en',
        'source_ip',
        'destination_ip',
        'detection_tool',
    )
    list_filter = (
        'pattern',
        'attack_type',
        'detection_tool',
        'detection_date',
    )
    search_fields = (
        'source_ip',
        'destination_ip',
        'pattern__name',
        'cve',
    )



@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name_en', 'name_ru')
    search_fields = ('id', 'name_en', 'name_ru')
