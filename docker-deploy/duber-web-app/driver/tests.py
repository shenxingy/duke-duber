from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Driver
from rider.models import Ride

class DriverTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.driver = User.objects.create_user('driver', 'driver@test.com', 'password123')
        self.rider = User.objects.create_user('rider', 'rider@test.com', 'password123')

    def test_vehicle_registration(self):
        self.client.login(username='driver', password='password123')
        response = self.client.post(reverse('vehicle_registration'), {
            'type': 'Sedan',
            'plate_number': 'ABC123',
            'max_passengers': 4
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Vehicle.objects.filter(driver=self.driver).exists())

    def test_driver_dashboard(self):
        # First register a vehicle
        self.client.login(username='driver', password='password123')
        self.client.post(reverse('vehicle_registration'), {
            'type': 'Sedan',
            'plate_number': 'ABC123',
            'max_passengers': 4
        })
        
        # Then test dashboard
        response = self.client.get(reverse('driver_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'driver/dashboard.html')

    def test_driver_cannot_accept_ride_without_vehicle(self):
        self.client.login(username='driver', password='password123')
        ride = Ride.objects.create(
            rider=self.rider,
            pickup_location='A',
            dropoff_location='B',
            passenger_count=2
        )
        response = self.client.post(reverse('accept_ride', args=[ride.id]))
        self.assertEqual(response.status_code, 302)
        ride.refresh_from_db()
        self.assertEqual(ride.status, 'PENDING')
