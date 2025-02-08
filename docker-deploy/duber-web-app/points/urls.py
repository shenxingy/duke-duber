from django.urls import path
from .views import my_points, redeem_tree

app_name = "points"

urlpatterns = [
    path('my-points/', my_points, name='my_points'),
    path('redeem-tree/', redeem_tree, name='redeem_tree'),
]