from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from driver.models import Vehicle
from .models import Ride, RideShare

class RideSharingTests(TestCase):
    def setUp(self):
        # Create test users
        self.client = Client()
        self.rider1 = User.objects.create_user('rider1', 'rider1@test.com', 'password123')
        self.rider2 = User.objects.create_user('rider2', 'rider2@test.com', 'password123')
        self.driver = User.objects.create_user('driver', 'driver@test.com', 'password123')
        
        # Create a vehicle for the driver
        self.vehicle = Vehicle.objects.create(
            driver=self.driver,
            type='Sedan',
            plate_number='ABC123',
            max_passengers=4
        )

    def test_create_sharable_ride(self):
        self.client.login(username='rider1', password='password123')
        
        # Create a sharable ride request
        response = self.client.post(reverse('request_ride'), {
            'pickup_location': 'Location A',
            'dropoff_location': 'Location B',
            'passenger_count': 2,
            'allow_sharing': True
        })
        
        self.assertEqual(response.status_code, 302)  # Redirect after success
        ride = Ride.objects.first()
        self.assertTrue(ride.allow_sharing)
        self.assertEqual(ride.passenger_count, 2)
        self.assertEqual(ride.total_passengers, 0)  # Should be updated when others join
    def test_join_ride(self):
        # Create initial ride
        ride = Ride.objects.create(
            rider=self.rider1,
            pickup_location='Location A',
            dropoff_location='Location B',
            passenger_count=2,
            allow_sharing=True
        )
        
        self.client.login(username='rider2', password='password123')
        
        # Join the ride
        response = self.client.post(reverse('join_ride', args=[ride.id]), {
            'passenger_count': 1
        })
        
        self.assertEqual(response.status_code, 302)  # Redirect after success
        
        # Refresh ride from database
        ride.refresh_from_db()
        self.assertEqual(ride.total_passengers, 3)  # 2 + 1
        self.assertEqual(ride.shared_rides.count(), 1)

    def test_driver_accept_shared_ride(self):
        # Create ride with multiple passengers
        ride = Ride.objects.create(
            rider=self.rider1,
            pickup_location='Location A',
            dropoff_location='Location B',
            passenger_count=2,
            allow_sharing=True
        )
        
        # Add another rider
        RideShare.objects.create(
            ride=ride,
            rider=self.rider2,
            passenger_count=2
        )
        
        ride.total_passengers = 4  # Update total passengers
        ride.save()
        
        self.client.login(username='driver', password='password123')
        
        # Try to accept the ride
        response = self.client.post(reverse('accept_ride', args=[ride.id]))
        
        ride.refresh_from_db()
        self.assertEqual(ride.status, 'CONFIRMED')
        self.assertEqual(ride.vehicle, self.vehicle)
    def test_exceed_vehicle_capacity(self):
        # Create ride with too many passengers
        ride = Ride.objects.create(
            rider=self.rider1,
            pickup_location='Location A',
            dropoff_location='Location B',
            passenger_count=3,
            allow_sharing=True
        )
        
        # Add another rider
        RideShare.objects.create(
            ride=ride,
            rider=self.rider2,
            passenger_count=3
        )
        
        ride.total_passengers = 6  # More than vehicle capacity
        ride.save()
        
        self.client.login(username='driver', password='password123')
        
        # Try to accept the ride
        response = self.client.post(reverse('accept_ride', args=[ride.id]))
        
        ride.refresh_from_db()
        self.assertEqual(ride.status, 'PENDING')  # Should still be pending
        self.assertIsNone(ride.vehicle)  # Should not be assigned to vehicle 
