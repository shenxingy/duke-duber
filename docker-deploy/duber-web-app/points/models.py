from django.db import models
from django.contrib.auth.models import User
from rider.models import Ride  # Assuming your ride model is in ride/models.py

class UserPoints(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.points} Points"

class PointsTransaction(models.Model):
    TRANSACTION_TYPE = (
        ('earn', 'Earned'),
        ('redeem', 'Redeemed'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ride = models.ForeignKey(Ride, on_delete=models.SET_NULL, null=True, blank=True)
    points = models.IntegerField()
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.transaction_type} {self.points} points"