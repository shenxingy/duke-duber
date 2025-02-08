from django.db.models.signals import post_save
from django.dispatch import receiver
from ride.models import Ride, RideShare
from points.models import UserPoints, PointsTransaction

@receiver(post_save, sender=Ride)
def award_points(sender, instance, created, **kwargs):
    if not created and instance.status == 'COMPLETED':  # Order completed
        distance = instance.distance
        base_points = int(distance * 10)  # 10 points per mile

        # ✅ Give tokens to the main ride requester (rider)
        if instance.rider:
            rider_points, _ = UserPoints.objects.get_or_create(user=instance.rider)
            rider_points.points += base_points
            rider_points.save()

            PointsTransaction.objects.create(user=instance.rider, ride=instance, points=base_points, transaction_type='earn')

        # ✅ Give tokens to the driver
        if instance.driver and instance.driver.driver:
            driver_points, _ = UserPoints.objects.get_or_create(user=instance.driver.driver)
            driver_points.points += base_points
            driver_points.save()

            PointsTransaction.objects.create(user=instance.driver.driver, ride=instance, points=base_points, transaction_type='earn')

        # ✅ Give tokens to all shared ride participants
        sharers = RideShare.objects.filter(ride=instance)
        for share in sharers:
            sharer_points, _ = UserPoints.objects.get_or_create(user=share.rider)
            sharer_points.points += base_points  # Or adjust based on shared distance
            sharer_points.save()

            PointsTransaction.objects.create(user=share.rider, ride=instance, points=base_points, transaction_type='earn')