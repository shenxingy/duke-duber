from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Driver
from .forms import VehicleRegistrationForm, VehicleUpdateForm
from django.contrib import messages
from rider.models import Ride
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import get_connection
import socket
from utils.gmail_service import send_email
from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
import logging
import requests
import os
from dotenv import load_dotenv
from rider.models import Ride, RideShare

# Load environment variables
load_dotenv()
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

logger = logging.getLogger(__name__)
def fetch_distance_from_google_maps(pickup, dropoff):
    """Fetch distance (in miles) using Google Maps Distance Matrix API."""
    GOOGLE_MAPS_API_KEY = settings.GOOGLE_MAPS_API_KEY
    url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={pickup}&destinations={dropoff}&key={GOOGLE_MAPS_API_KEY}"
    
    response = requests.get(url)
    data = response.json()
    
    if data.get("status") == "OK":
        distance_meters = data["rows"][0]["elements"][0]["distance"]["value"]  # Distance in meters
        distance_miles = distance_meters / 1609.34  # Convert meters to miles
        return round(distance_miles, 2)
    
    return 0.0  # Default if API call fails

@login_required
def driver_dashboard(request):
    try:
        vehicle = Driver.objects.get(driver=request.user)
        # Apply filters for max_passengers and special_info
        pending_rides = Ride.objects.filter(
            status='PENDING',
            passenger_count__lte=vehicle.max_passengers,
            special_request=vehicle.special_info
        ).order_by('-created_at')
        #COMPLETED is history
        ride_history = Ride.objects.filter(driver=vehicle).exclude(status__in=['PENDING', 'CONFIRMED', 'CANCELED']).order_by('-created_at')
        # Open rides are PENDING
        my_rides = Ride.objects.filter(driver=vehicle, status='CONFIRMED')
        return render(request, 'driver/dashboard.html', {
            'vehicle': vehicle,
            'pending_rides': pending_rides,
            'my_rides': my_rides,
            'ride_history': ride_history
        })
    except Driver.DoesNotExist:
        return redirect('vehicle_registration')

@login_required
def vehicle_registration(request):
    if request.method == 'POST':
        form = VehicleRegistrationForm(request.POST)
        if form.is_valid():
            vehicle = form.save(commit=False)
            vehicle.driver = request.user
            vehicle.save()
            #messages.success(request, 'Vehicle registered successfully!')
            return redirect('driver_dashboard')
    else:
        form = VehicleRegistrationForm()
    return render(request, 'driver/vehicle_registration.html', {'form': form})

@login_required
def accept_ride(request, ride_id):
    try:
        # 获取当前登录用户的 Driver 信息
        driver_profile = Driver.objects.get(driver=request.user)

        # 获取订单并检查状态
        ride = Ride.objects.get(id=ride_id)
        if ride.status != 'PENDING':
            #messages.error(request, 'This ride is no longer available.')
            return redirect('driver_dashboard')

        # 计算总乘客数
        total_passengers = ride.total_passengers

        # 判断载客量是否足够
        if total_passengers <= driver_profile.max_passengers:
            ride.distance = fetch_distance_from_google_maps(ride.pickup_location, ride.dropoff_location)
            # **这里改为给 ride.driver 赋值，而非 ride.vehicle**
            ride.driver = driver_profile  
            ride.status = 'CONFIRMED'
            ride.shared_rides.update(status='CONFIRMED')
            ride.save()
            
            # 发送邮件通知
            if ride.rider and ride.rider.email:
                try:
                    logger.info("Attempting to send email...")
                    subject = "Your Ride Has Been Accepted"
                    message = f"""Dear User,

                    Your ride has been accepted by driver.
                    The driver will provide service shortly.

                    Ride Details:
                    - Pickup Location: {ride.pickup_location}
                    - Destination: {ride.dropoff_location}
                    - Number of Passengers: {total_passengers}

                    If you have any questions, please contact our customer service.

                    Have a great ride!"""

                    if send_email(ride.rider.email, subject, message):
                        messages.success(request, 'Ride accepted and notification sent!')
                    else:
                        messages.success(request, 'Ride accepted but email notification failed.')
                except Exception as e:
                    logger.error(f"Email error: {str(e)}")
                    messages.success(request, 'Ride accepted but email notification failed.')
            else:
                messages.success(request, 'Ride accepted!')
                
            return redirect('driver_dashboard')
        # else:
            # messages.error(request, 'Your vehicle cannot accommodate this many passengers.')
    except Exception as e:
        print(f"Unexpected error in accept_ride: {str(e)}")
        # messages.error(request, 'An error occurred while processing your request.')
    
    return redirect('driver_dashboard')

from points.models import UserPoints, PointsTransaction

TOKEN_RATE = 1000  # ✅ 10 points per mile

@login_required
def finish_ride(request, ride_id):
    try:
        vehicle = Driver.objects.get(driver=request.user)
        ride = get_object_or_404(Ride, id=ride_id, status='CONFIRMED', driver=vehicle)
        
        # ✅ Update ride status
        ride.status = 'COMPLETED'
        ride.shared_rides.update(status='COMPLETED')
        ride.save()

        # ✅ Award tokens to the rider
        base_points = int(ride.distance * TOKEN_RATE)
        if ride.rider:
            rider_points, _ = UserPoints.objects.get_or_create(user=ride.rider)
            rider_points.points += base_points
            rider_points.save()

            PointsTransaction.objects.create(user=ride.rider, ride=ride, points=base_points, transaction_type='earn')

        # ✅ Award tokens to the driver
        if ride.driver and ride.driver.driver:
            driver_points, _ = UserPoints.objects.get_or_create(user=ride.driver.driver)
            driver_points.points += base_points
            driver_points.save()

            PointsTransaction.objects.create(user=ride.driver.driver, ride=ride, points=base_points, transaction_type='earn')

        # ✅ Award tokens to ride sharers (based on their individual distance)
        sharers = RideShare.objects.filter(ride=ride)
        for share in sharers:
            sharer_distance = fetch_distance_from_google_maps(share.pickup_location, share.dropoff_location)
            sharer_points = int(sharer_distance * TOKEN_RATE)

            sharer_user_points, _ = UserPoints.objects.get_or_create(user=share.rider)
            sharer_user_points.points += sharer_points
            sharer_user_points.save()

            PointsTransaction.objects.create(user=share.rider, ride=ride, points=sharer_points, transaction_type='earn')

        messages.success(request, f'Ride completed! Tokens awarded based on {ride.distance} miles.')

    except Driver.DoesNotExist:
        print("vehicle not found")
    
    return redirect('driver_dashboard')

@login_required
def update_vehicle(request):
    try:
        vehicle = Driver.objects.get(driver=request.user)
        if request.method == 'POST':
            form = VehicleUpdateForm(request.POST, instance=vehicle)
            if form.is_valid():
                form.save()
                # messages.success(request, 'Vehicle information updated successfully!')
                return redirect('driver_dashboard')
        else:
            form = VehicleUpdateForm(instance=vehicle)
        return render(request, 'driver/update_vehicle.html', {'form': form})
    except Driver.DoesNotExist:
        return redirect('vehicle_registration')


class DriverRideDetailView(LoginRequiredMixin, DetailView):
    model = Ride
    template_name = 'driver/driver_ride_detail.html'  # 司机专用的模板
    context_object_name = 'ride'

    def get_queryset(self):
        # 如果司机真的要看到所有订单，不加限制就行
        return Ride.objects.all()