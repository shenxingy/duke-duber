from django.urls import path
from . import views
from .views import DriverRideDetailView

urlpatterns = [
    path('dashboard/', views.driver_dashboard, name='driver_dashboard'),
    path('register/', views.vehicle_registration, name='vehicle_registration'),
    path('update/', views.update_vehicle, name='update_vehicle'),
    path('accept_ride/<int:ride_id>/', views.accept_ride, name='accept_ride'),
    path('finish_ride/<int:ride_id>/', views.finish_ride, name='finish_ride'),
    path('driver/ride_detail/<int:pk>/', DriverRideDetailView.as_view(), name='driver_ride_detail'),
] 
