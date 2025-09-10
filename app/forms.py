# forms.py
from django import forms
from .models import VoteAllocation

class VoteAllocationForm(forms.ModelForm):
    class Meta:
        model = VoteAllocation
        fields = [
            'name', 'description', 'aa_percentage', 'ad_percentage', 
            'adc_percentage', 'apc_percentage', 'lp_percentage', 'pdp_percentage'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'aa_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '100'}),
            'ad_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '100'}),
            'adc_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '100'}),
            'apc_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '100'}),
            'lp_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '100'}),
            'pdp_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '100'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        total = (
            cleaned_data.get('aa_percentage', 0) +
            cleaned_data.get('ad_percentage', 0) +
            cleaned_data.get('adc_percentage', 0) +
            cleaned_data.get('apc_percentage', 0) +
            cleaned_data.get('lp_percentage', 0) +
            cleaned_data.get('pdp_percentage', 0)
        )

        if abs(total - 100.0) > 0.01:
            raise forms.ValidationError(f'Total percentage must equal 100%. Current total: {total:.2f}%')

        return cleaned_data
