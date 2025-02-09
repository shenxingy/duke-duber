from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import UserPoints, PointsTransaction

TREE_COST = 1000  # 兑换一棵树所需的积分
CARBON_PER_MILE = 0.404  # 假设每英里约减少 0.404 kg 的 CO₂

@login_required
def redeem_tree(request):
    user_points = UserPoints.objects.get(user=request.user)

    if user_points.points >= TREE_COST:
        user_points.points -= TREE_COST
        user_points.save()

        PointsTransaction.objects.create(
            user=request.user, 
            points=TREE_COST, 
            transaction_type='redeem'
        )

    return redirect('points:my_points')


@login_required
def my_points(request):
    user_points, created = UserPoints.objects.get_or_create(user=request.user)
    transactions = PointsTransaction.objects.filter(user=request.user).order_by('-timestamp')
    trees_planted = transactions.filter(transaction_type="redeem").count()

    # 1 点 = 1/1000 英里，因此总里程 = 总积分 / 1000
    total_miles = user_points.total_points_earned / 1000

    # 根据总里程计算预计碳排放减排量（单位：kg）
    carbon_saved_kg = total_miles * CARBON_PER_MILE

    return render(request, 'points/my_points.html', {
        'user_points': user_points,
        'transactions': transactions,
        'trees_planted': trees_planted,
        'total_miles': total_miles,
        'carbon_saved_kg': carbon_saved_kg,
    })