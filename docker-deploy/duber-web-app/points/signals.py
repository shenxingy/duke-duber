from django.db.models.signals import post_save
from django.dispatch import receiver
from ride.models import Ride
from points.models import UserPoints, PointsTransaction

@receiver(post_save, sender=Ride)
def award_points(sender, instance, created, **kwargs):
    if not created and instance.status == 'COMPLETED':  # 订单完成
        user = instance.rider
        distance = instance.distance

        points_earned = int(distance * 10)  # 1 英里 = 10 积分
        if instance.allow_sharing:
            points_earned += 50  

        user_points, _ = UserPoints.objects.get_or_create(user=user)
        user_points.points += points_earned
        user_points.save()

        PointsTransaction.objects.create(user=user, ride=instance, points=points_earned, transaction_type='earn')