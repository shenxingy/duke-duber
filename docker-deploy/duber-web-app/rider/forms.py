import os
import requests
from django import forms
from django.core.exceptions import ValidationError
from dotenv import load_dotenv
from django.utils.timezone import now
from .models import Ride, RideShare

# Load environment variables
load_dotenv()
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

def validate_address(address):
    print(GOOGLE_MAPS_API_KEY)
    """Check if an address is valid using Google Maps Geocoding API."""
    if not address:
        raise ValidationError("Address cannot be empty.")

    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={GOOGLE_MAPS_API_KEY}"
    response = requests.get(url)
    
    # Ensure response is valid
    if response.status_code != 200:
        raise ValidationError("Failed to validate address. Please try again.")

    result = response.json()
    
    if result.get("status") != "OK":
        raise ValidationError("Invalid address. Please enter a real location.")

class RideRequestForm(forms.ModelForm):
    pickup_location = forms.CharField(
        max_length=255,
        validators=[validate_address],
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    dropoff_location = forms.CharField(
        max_length=255,
        validators=[validate_address],
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    required_arrival_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}),
        required=False
    )
    

    class Meta:
        model = Ride
        fields = ['pickup_location', 'dropoff_location', 'passenger_count', 
                  'required_arrival_time','special_request', 'allow_sharing']
        widgets = {
            'special_request': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'passenger_count': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'allow_sharing': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class JoinRideForm(forms.ModelForm):
    class Meta:
        model = RideShare
        fields = ['passenger_count']
        widgets = {
            'passenger_count': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }