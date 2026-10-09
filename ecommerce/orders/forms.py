from django import forms
from .models import Order


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['full_name' , 'phone' , 'address']
        widgets = {
            'full_name':forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class':'form-control'}),
            'address': forms.Textarea(attrs={'class':'form-control' , 'row':3})
        }
