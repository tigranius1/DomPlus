from django import forms
from .models import ViewingRequest, Apartment


class ViewingRequestForm(forms.ModelForm):
    class Meta:
        model = ViewingRequest
        fields = ['name', 'phone', 'preferred_date', 'comment']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Ваше имя'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': '+7 (___) ___-__-__'
            }),
            'preferred_date': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M',
            ),
            'comment': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3,
                'placeholder': 'Комментарий (необязательно)'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['preferred_date'].input_formats = ['%Y-%m-%dT%H:%M']
        self.fields['preferred_date'].required = False


class ApartmentFilterForm(forms.Form):
    """Форма фильтров для каталога (используется в GET-запросе)."""
    price_min = forms.DecimalField(
        required=False, min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control', 'placeholder': 'от 5 000 000'
        }),
    )
    price_max = forms.DecimalField(
        required=False, min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control', 'placeholder': 'до 15 000 000'
        }),
    )
    district = forms.ChoiceField(
        required=False,
        choices=[('', 'Любой')] + list(Apartment.District.choices),
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    area_min = forms.DecimalField(
        required=False, min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control', 'placeholder': 'от 30'
        }),
    )
    floor_min = forms.IntegerField(
        required=False, min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control', 'placeholder': 'от 1'
        }),
    )
    floor_max = forms.IntegerField(
        required=False, min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control', 'placeholder': 'до 25'
        }),
    )