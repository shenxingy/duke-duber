from django.urls import path
from .views import request_ride, get_eta, rider_dashboard, edit_ride, cancel_ride, RideDetailView

urlpatterns = [
    path("request/", request_ride, name="request_ride"),
    path("dashboard/", rider_dashboard, name="rider_dashboard"),
    path("edit/<int:ride_id>/", edit_ride, name="edit_ride"),  
    path("get_eta/", get_eta, name="get_eta"),
    # Other URL patterns
    path('cancel_ride/<int:ride_id>/', cancel_ride, name='cancel_ride'),
    path('ride/<int:pk>/', RideDetailView.as_view(), name='ride_detail'),
]