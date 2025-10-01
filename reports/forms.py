from django import forms
from .models import Report, Pattern
from datetime import datetime

class ReportsForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = [
            'detection_date', 'country', 'organization', 'pattern',  'attack_type', 'source_ip',
            'destination_ip', 'cve', 'host', 'detection_tool',
            'short_description', 'methods', 'protocols_ports',
            'potential_impact', 'risk_assessment', 'data_or_payload', 'response_actions',
        ]

    pattern = forms.CharField(
        required=False,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_pattern'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Уменьшенный виджет для даты и времени
        self.fields['detection_date'].widget = forms.DateTimeInput(
            attrs={
                # 'type': 'datetime-local',
                'class': 'form-control form-control-sm',
            }
        )
        self.fields['detection_date'].input_formats = ['%Y/%m/%d']
        # Заполнение выпадающего списка
        self.fields['pattern'].widget.choices = [
            (str(p.pk), p.name) for p in Pattern.objects.all()
        ]

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

    def clean(self):
        cleaned_data = super().clean()
        raw_value = self.data.get('pattern')
        pattern_obj = None
        print(raw_value)

        try:
            pattern_obj = Pattern.objects.filter(pk=raw_value).first()
        except:
            print('pattern_obj: ', pattern_obj)
            # Если это ID существующего Pattern
            pattern_obj = Pattern.objects.create(
                name=raw_value,
                attack_type=cleaned_data.get('attack_type', ''),
                methods=cleaned_data.get('methods', ''),
                detection_tool=cleaned_data.get('detection_tool', ''),
                protocols_ports=cleaned_data.get('protocols_ports', ''),
                risk_assessment=cleaned_data.get('risk_assessment', 'Низкая'),
                potential_impact=cleaned_data.get('potential_impact', ''),
                data_or_payload=cleaned_data.get('data_or_payload', ''),
                response_actions=cleaned_data.get('response_actions', ''),
            )


        cleaned_data['pattern'] = pattern_obj
        return cleaned_data

