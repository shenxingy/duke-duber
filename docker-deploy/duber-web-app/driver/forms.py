from django import forms
from .models import Driver

class VehicleRegistrationForm(forms.ModelForm):
    class Meta:
        model = Driver
        fields = ['type', 'plate_number', 'max_passengers', 'special_info']
        widgets = {
            'special_info': forms.Textarea(attrs={'rows': 3}),
        }

class VehicleUpdateForm(forms.ModelForm):
    class Meta:
        model = Driver
        fields = ['type', 'plate_number', 'max_passengers', 'special_info']
        widgets = {
            'type': forms.TextInput(attrs={'class': 'form-control'}),
            'plate_number': forms.TextInput(attrs={'class': 'form-control'}),
            'max_passengers': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 25}),
            'special_info': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
