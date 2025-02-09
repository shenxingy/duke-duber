from django.urls import path
from .views import my_points, redeem_tree, redeem_succulent, redeem_produce

app_name = "points"

urlpatterns = [
    path('my-points/', my_points, name='my_points'),
    path('redeem-tree/', redeem_tree, name='redeem_tree'),
    path('redeem-succulent/', redeem_succulent, name='redeem_succulent'),
    path('redeem-produce/', redeem_produce, name='redeem_produce'),
]
