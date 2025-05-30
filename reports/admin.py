from django.contrib import admin
from .models import AttackType, Report, Organization
from django import forms



class AttackTypeForm(forms.ModelForm):
    class Meta:
        model = AttackType
        fields = '__all__'

    def clean_name(self):
        name = self.cleaned_data['name'].strip()
        qs = AttackType.objects.filter(name__iexact=name)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(
                "Тип атаки с таким названием уже существует."
            )
        return name


@admin.register(AttackType)
class AttackTypeAdmin(admin.ModelAdmin):
    form = AttackTypeForm
    list_display = ('name', 'cve')
    search_fields = ('name',)


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = (
        'detection_date',
        'attack_type',
        'source_ip',
        'destination_ip',
        'detection_tool',
    )
    list_filter = (
        'attack_type',
        'detection_tool',
        'detection_date',
    )
    search_fields = (
        'source_ip',
        'destination_ip',
        'attack_type__name',
    )



@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
