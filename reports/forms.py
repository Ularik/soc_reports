from django import forms
from .models import Report

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = [
            'organization', 'detection_date', 'attack_type', 'detection_tool',
            'source_ip', 'destination_ip',
            'short_description', 'methods', 'protocols_ports',
            'risk_assessment', 'potential_impact', 'payload', 'response_actions',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Уменьшенный виджет для даты и времени
        self.fields['detection_date'].widget = forms.DateTimeInput(
            attrs={
                'type': 'datetime-local',
                'class': 'form-control form-control-sm',
            }
        )
        for name, field in self.fields.items():
            if name == 'detection_date':
                continue
            widget = field.widget
            # Компактные текстовые области
            if isinstance(widget, forms.Textarea):
                widget.attrs.update({
                    'class': 'form-control form-control-sm',
                    'rows': 2,
                })
            # Компактные выпадающие списки
            elif hasattr(widget, 'input_type') and widget.input_type == 'select':
                widget.attrs.update({'class': 'form-select form-select-sm'})
            # Компактные поля ввода
            else:
                widget.attrs.update({'class': 'form-control form-control-sm'})
