from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

class NavigationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='password123'
        )

    def test_home_page_anonymous(self):
        """Test home page for anonymous users"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        self.assertContains(response, 'Login')
        self.assertContains(response, 'Register')
        self.assertNotContains(response, 'Driver Mode')
        self.assertNotContains(response, 'Rider Mode')

    def test_home_page_authenticated(self):
        """Test home page for logged in users"""
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        self.assertContains(response, 'Driver Mode')
        self.assertContains(response, 'Rider Mode')
        self.assertContains(response, 'Logout')

    def test_navigation_authentication_required(self):
        """Test pages that require authentication"""
        protected_urls = [
            'rider_dashboard',
            'driver_dashboard',
            'request_ride',
            'vehicle_registration'
        ]
        
        # Test without login
        for url_name in protected_urls:
            response = self.client.get(reverse(url_name))
            self.assertEqual(response.status_code, 302)
            self.assertIn('/accounts/login/', response.url)
        
        # Test with login
        self.client.login(username='testuser', password='password123')
        for url_name in protected_urls:
            response = self.client.get(reverse(url_name))
            self.assertIn(response.status_code, [200, 302])  # Some views might redirect

    def test_navigation_flow(self):
        """Test the navigation flow between pages"""
        self.client.login(username='testuser', password='password123')
        
        # Test navigation from home to rider dashboard
        response = self.client.get(reverse('rider_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'rider/dashboard.html')
        
        # Test navigation from home to driver dashboard
        response = self.client.get(reverse('driver_dashboard'))
        self.assertEqual(response.status_code, 302)  # Should redirect to vehicle registration
        self.assertIn('register-vehicle', response.url)
