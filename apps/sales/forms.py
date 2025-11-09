from django import forms
from .models import Sale

class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['seller', 'date', 'total_amount']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'seller': forms.Select(attrs={'class': 'form-select'}),
            'total_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '0.00'
            }),
        }
    def clean_total_amount(self):
        total_amount = self.cleaned_data.get('total_amount')
        if total_amount is not None and total_amount < 0:
            raise forms.ValidationError("O valor total da venda não pode ser negativo.")
        return total_amount
    
    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date is None:
            raise forms.ValidationError("A data da venda é obrigatória.")
        return date
