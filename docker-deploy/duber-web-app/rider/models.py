from django.db import models
from django.contrib.auth.models import User
from driver.models import Driver
from django.core.validators import MinValueValidator, MaxValueValidator

class Ride(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    rider = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rides_requested')
    pickup_location = models.CharField(max_length=255)
    dropoff_location = models.CharField(max_length=255)
    passenger_count = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(25)] 
    )
    special_request = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    allow_sharing = models.BooleanField(default=False)
    total_passengers = models.IntegerField(default=0)
    required_arrival_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, blank=True, related_name="rides_driven")

    def __str__(self):
        return f"Ride from {self.pickup_location} to {self.dropoff_location}"

class RideShare(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    ride = models.ForeignKey(Ride, on_delete=models.CASCADE, related_name='shared_rides')
    rider = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    pickup_location = models.CharField(max_length=255, default='Unknown')
    dropoff_location = models.CharField(max_length=255, default='Unknown')
    passenger_count = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
