from django import forms
from .models import Report


class ReportsForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = [
            'detection_date', 'organization', 'attack_type', 'source_ip',
            'destination_ip', 'cve', 'host', 'detection_tool',
            'short_description', 'methods', 'protocols_ports',
            'potential_impact', 'risk_assessment', 'data_or_payload', 'response_actions',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():
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
