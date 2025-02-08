import os
import json
import pytz
import requests
from datetime import datetime
from django.db.models import Q
from django.conf import settings
from django.utils.timezone import now
from datetime import timedelta
from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin  # Add this import


from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
from .forms import RideRequestForm, JoinRideForm
from .models import Ride, RideShare

# Load environment variables
load_dotenv()
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

def get_estimated_time(pickup, dropoff):
    """Fetch estimated time using Google Maps Distance Matrix API."""
    url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={pickup}&destinations={dropoff}&key={GOOGLE_MAPS_API_KEY}"
    response = requests.get(url)
    result = response.json()
    if result.get("status") == "OK":
        return result["rows"][0]["elements"][0]["duration"]["text"]
    return "Unknown ETA"

def get_estimated_info(pickup, dropoff):
    """Fetch estimated time and distance using Google Maps Distance Matrix API."""
    url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={pickup}&destinations={dropoff}&key={GOOGLE_MAPS_API_KEY}"
    response = requests.get(url)
    result = response.json()
    if result.get("status") == "OK":
        element = result["rows"][0]["elements"][0]
        return {
            "duration_text": element["duration"]["text"],
            "distance_text": element["distance"]["text"]
        }
    return {
        "duration_text": "Unknown ETA",
        "distance_text": "Unknown Distance"
    }

def get_lat_lng(address):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={GOOGLE_MAPS_API_KEY}"
    response = requests.get(url)
    data = response.json()
    
    if data["status"] == "OK":
        return data["results"][0]["geometry"]["location"]  # 返回 {'lat': ..., 'lng': ...}
    return None  # 地址无效

def get_optimized_route(requester_pickup, requester_dropoff, sharer_pickup, sharer_dropoff):
    """
    Uses Google Maps Directions API to determine whether a ride is along the way:
    - requester_pickup -> sharer_pickup (fixed order)
    - sharer_dropoff & requester_dropoff (Google will optimize order)
    - Validates if both requester & sharer can arrive on time.
    """
    url = "https://maps.googleapis.com/maps/api/directions/json"
    
    requester_pickup_coords = get_lat_lng(requester_pickup)
    requester_dropoff_coords = get_lat_lng(requester_dropoff)
    sharer_pickup_coords = get_lat_lng(sharer_pickup)
    sharer_dropoff_coords = get_lat_lng(sharer_dropoff)
    
    params = {
        "origin": f"{requester_pickup_coords['lat']},{requester_pickup_coords['lng']}",
        "destination": f"{requester_dropoff_coords['lat']},{requester_dropoff_coords['lng']}",
        "waypoints": f"{sharer_pickup_coords['lat']},{sharer_pickup_coords['lng']}|{sharer_dropoff_coords['lat']},{sharer_dropoff_coords['lng']}",
        "key": GOOGLE_MAPS_API_KEY
    }
    
    response = requests.get(url, params=params)
    data = response.json()

    if data.get("status") == "OK":
        legs = data["routes"][0]["legs"]
        optimized_order = data["routes"][0].get("waypoint_order", [])

        # Determine the order of drop-offs
        dropoff_points = [sharer_dropoff, requester_dropoff]
        sorted_dropoff_points = [dropoff_points[i] for i in optimized_order]

        # Extract segment travel times (convert seconds to minutes)
        requester_to_sharer_time = legs[0]["duration"]["value"] // 60  # requester -> sharer
        sharer_to_first_dropoff_time = legs[1]["duration"]["value"] // 60  # first drop-off
        first_to_second_dropoff_time = legs[2]["duration"]["value"] // 60  # second drop-off

        # Track total travel times
        travel_times = {
            "requester": requester_to_sharer_time,
            "sharer": 0
        }

        # Assign travel time based on who is dropped off first
        if sorted_dropoff_points[0] == sharer_dropoff:
            travel_times["sharer"] += sharer_to_first_dropoff_time
            travel_times["requester"] += sharer_to_first_dropoff_time + first_to_second_dropoff_time
        else:
            travel_times["requester"] += sharer_to_first_dropoff_time
            travel_times["sharer"] += sharer_to_first_dropoff_time + first_to_second_dropoff_time
        
        print(f"Calculating route: {requester_pickup} → {sharer_pickup} → {sharer_dropoff} → {requester_dropoff}")
        print(f"Google API URL: https://maps.googleapis.com/maps/api/directions/json?origin={requester_pickup}&destination={requester_dropoff}&waypoints=optimize:true|{sharer_pickup}|{sharer_dropoff}&key=YOUR_API_KEY")
        print("Google API Response:", json.dumps(response.json(), indent=4))
        return {
            "requester_duration": travel_times["requester"],
            "sharer_duration": travel_times["sharer"],
            "optimized_order": optimized_order
        }
    else:
        print("Google API Response:", json.dumps(response.json(), indent=4))
        return None  # Optimization failed

@csrf_exempt
def get_eta(request):
    """API endpoint to retrieve estimated travel time and distance."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            pickup = data.get("pickup_location")
            dropoff = data.get("dropoff_location")
            if not pickup or not dropoff:
                return JsonResponse({"success": False, "error": "Invalid locations."}, status=400)
            estimated_info = get_estimated_info(pickup, dropoff)
            return JsonResponse({
                "success": True,
                "estimated_time": estimated_info["duration_text"],
                "estimated_distance": estimated_info["distance_text"],
            })
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)
    return JsonResponse({"success": False, "error": "Invalid method."}, status=405)

@login_required
def request_ride(request):
    """Handles ride requests and provides an estimated arrival time."""
    if request.method == 'POST':
        form = RideRequestForm(request.POST)
        if form.is_valid():
            ride = form.save(commit=False)
            ride.rider = request.user
            ride.total_passengers += form.cleaned_data.get("passenger_count", 1)
            ride.status = 'PENDING'
            ride.save()  # 🚀 Assigns an ID
            
            return redirect('rider_dashboard')
        # else:
            #messages.error(request, 'There was an error in your ride request. Please check your input.')

    else:
        form = RideRequestForm()

    return render(request, 'rider/request_ride.html', {
        "form": form,
        "GOOGLE_MAPS_API_KEY": GOOGLE_MAPS_API_KEY
    })

@login_required
def edit_ride(request, ride_id):
    """Prevents editing confirmed rides."""
    ride = get_object_or_404(Ride, id=ride_id, rider=request.user)

    if ride.status != 'PENDING':
        #messages.error(request, "You cannot edit a confirmed or completed ride.")
        return redirect("rider_dashboard")

    if request.method == 'POST':
        form = RideRequestForm(request.POST, instance=ride)
        if form.is_valid():
            form.save()
            ride.updated_at = now()
            ride.save()
            #messages.success(request, "Ride updated successfully.")
            return redirect('rider_dashboard')
        # else:
            #messages.error(request, "There was an error updating your ride.")
    else:
        form = RideRequestForm(instance=ride)

    return render(request, 'rider/edit_ride.html', {
        'form': form,
        'ride': ride,
        "GOOGLE_MAPS_API_KEY": GOOGLE_MAPS_API_KEY
    })
    
@login_required
def cancel_ride(request, ride_id):
    """Allow the ride owner to cancel a pending ride and auto-cancel all sharers."""
    ride = get_object_or_404(Ride, id=ride_id, rider=request.user, status='PENDING')

    # Mark the ride as cancelled
    ride.status = 'CANCELLED'
    ride.save()

    # Cancel all associated RideShare entries
    for share in ride.shared_rides.all():
        share.status = 'CANCELLED'
        share.save()

    messages.success(request, "Ride and all shared bookings have been cancelled successfully.")
    return redirect('rider_dashboard')

@login_required
def rider_dashboard(request):
    # Owner's rides:
    open_rides = Ride.objects.filter(
        rider=request.user, status__in=['PENDING', 'CONFIRMED']
    ).order_by('-created_at')

    # For rides the user has joined as a sharer, separate active from history.
    active_sharer_rides = RideShare.objects.filter(
        rider=request.user, status__in=['PENDING', 'CONFIRMED']
    ).select_related('ride')
    
    has_active_rides = open_rides.exists() or active_sharer_rides.exists()
    
    closed_rides = Ride.objects.filter(
        rider=request.user, status__in=['COMPLETED', 'CANCELLED']
    ).order_by('-created_at')
    sharer_history = RideShare.objects.filter(
        rider=request.user
    ).exclude(status='PENDING').select_related('ride')

    search_results = []
    search_performed = False

    if request.method == "POST":
        if "join_ride_id" in request.POST:
            ride_id = request.POST.get("join_ride_id")
            sharer_pickup = request.POST.get("sharer_pickup")
            sharer_dropoff = request.POST.get("sharer_dropoff")
            passenger_count = int(request.POST.get("passenger_count", 1))

            ride = get_object_or_404(Ride, id=ride_id, status='PENDING', allow_sharing=True)

            # Create RideShare entry
            RideShare.objects.create(
                ride=ride,
                rider=request.user,
                status='PENDING',
                passenger_count=passenger_count,
                pickup_location=sharer_pickup,
                dropoff_location=sharer_dropoff,
                created_at=now()
            )

            # Update total_passengers (just for record-keeping)
            ride.total_passengers += passenger_count
            ride.save()

            messages.success(request, "Successfully joined the ride!")
            return redirect("rider_dashboard")

        elif "leave_ride_id" in request.POST:
            share_id = request.POST.get("leave_ride_id")
            # Ensure we are only processing an active share ride.
            ride_share = get_object_or_404(RideShare, id=share_id, rider=request.user, status='PENDING')
            ride = ride_share.ride

            # Update the total_passengers count on the parent ride.
            ride.total_passengers -= ride_share.passenger_count
            ride.save()

            # Change the RideShare status to CANCELLED.
            ride_share.status = 'CANCELLED'
            ride_share.save()

            messages.success(request, "Successfully left the ride.")
            return redirect("rider_dashboard")

    # Handle Searching for Rides (unchanged)...
    if request.method == "GET" and "search" in request.GET:
        sharer_pickup = request.GET.get("sharer_pickup", "").strip()
        sharer_dropoff = request.GET.get("sharer_dropoff", "").strip()
        earliest_arrival = request.GET.get("earliest_arrival")
        latest_arrival = request.GET.get("latest_arrival")
        passenger_count = request.GET.get("passenger_count")

        query = Q(status="PENDING", allow_sharing=True)
        candidate_rides = Ride.objects.filter(query).exclude(rider=request.user).order_by('required_arrival_time')

        valid_rides = []
        for ride in candidate_rides:
            route_info = get_optimized_route(
                requester_pickup=ride.pickup_location,
                requester_dropoff=ride.dropoff_location,
                sharer_pickup=sharer_pickup,
                sharer_dropoff=sharer_dropoff,
            )
            if route_info:
                valid_rides.append(ride)

        search_results = valid_rides
        search_performed = True

    context = {
        "has_active_rides": has_active_rides,
        "open_rides": open_rides,
        "active_sharer_rides": active_sharer_rides,
        "sharer_history": sharer_history,
        "closed_rides": closed_rides,
        "search_results": search_results,
        "search_performed": search_performed,
        "GOOGLE_MAPS_API_KEY": GOOGLE_MAPS_API_KEY,
    }
    return render(request, "rider/dashboard.html", context)


class RideDetailView(LoginRequiredMixin, DetailView):
    model = Ride
    template_name = 'rider/ride_detail.html'
    context_object_name = 'ride'

    def get_queryset(self):
        return Ride.objects.all()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["assigned_driver"] = self.object.driver
        return context
        
@login_required
def confirm_ride(request, ride_id):
    """Confirms a ride and assigns a driver."""
    ride = get_object_or_404(Ride, id=ride_id, status='PENDING')

    if ride.driver:  # If already assigned, prevent reassignment
        # messages.error(request, "This ride is already confirmed with a driver.")
        return redirect("rider_dashboard")

    available_driver = Driver.objects.filter(is_available=True).first()

    if not available_driver:
        # messages.error(request, "No available drivers at the moment. Please try again later.")
        return redirect("rider_dashboard")

    # Assign the driver and update the ride status
    ride.driver = available_driver
    ride.status = 'CONFIRMED'
    ride.save()

    # Mark the driver as unavailable
    available_driver.is_available = False
    available_driver.save()

    # messages.success(request, f"Ride confirmed! Driver {available_driver.user.username} assigned.")
    return redirect("rider_dashboard")
