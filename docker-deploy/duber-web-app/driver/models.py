from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class Driver(models.Model):
    driver = models.OneToOneField(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=50)
    plate_number = models.CharField(max_length=20)
    max_passengers = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(25)] 
    )
    special_info = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.driver.username}'s vehicle - {self.plate_number}"
