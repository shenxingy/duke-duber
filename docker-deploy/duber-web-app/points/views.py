from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import UserPoints, PointsTransaction
from django.contrib import messages


TREE_COST = 1000  # Assume 1000 points to plant a tree
SUCCULENT_COST = 300  # 多肉植物兑换成本
PRODUCE_COST = 500  # 蔬果兑换成本
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
            transaction_type='redeem',
            redemption_item='tree',  #
        )

    return redirect('points:my_points')


@login_required
def redeem_succulent(request):
    user_points = UserPoints.objects.get(user=request.user)

    if user_points.points >= SUCCULENT_COST:
        user_points.points -= SUCCULENT_COST
        user_points.save()

        PointsTransaction.objects.create(
            user=request.user, points=SUCCULENT_COST, transaction_type='redeem', redemption_item='succulent',
        )

        messages.success(request, "Congratulations! You got a succulent from Duke Garden!")
    else:
        messages.error(request, "Not enough points to redeem a succulent.")

    return redirect('points:my_points')

@login_required
def redeem_produce(request):
    user_points = UserPoints.objects.get(user=request.user)

    if user_points.points >= PRODUCE_COST:
        user_points.points -= PRODUCE_COST
        user_points.save()

        PointsTransaction.objects.create(
            user=request.user, points=PRODUCE_COST, transaction_type='redeem',redemption_item='produce', 
        )

        messages.success(request, "Congratulations! You got fresh produce from Duke Farm!")
    else:
        messages.error(request, "Not enough points to redeem produce.")

    return redirect('points:my_points')

# points/views.py

CARBON_PER_MILE = 0.404  # example

@login_required
def my_points(request):
    user_points, created = UserPoints.objects.get_or_create(user=request.user)
    transactions = PointsTransaction.objects.filter(user=request.user).order_by('-timestamp')
    
    # Query how many times each item was redeemed
    trees_planted = transactions.filter(transaction_type="redeem", redemption_item="tree").count()
    succulents_redeemed = transactions.filter(transaction_type="redeem", redemption_item="succulent").count()
    produce_redeemed = transactions.filter(transaction_type="redeem", redemption_item="produce").count()

    # 1 点 = 1/1000 英里
    total_miles = user_points.total_points_earned / 1000
    carbon_saved_kg = total_miles * CARBON_PER_MILE

    return render(request, 'points/my_points.html', {
        'user_points': user_points,
        'transactions': transactions,
        'trees_planted': trees_planted,
        'succulents_redeemed': succulents_redeemed,
        'produce_redeemed': produce_redeemed,
        'total_miles': total_miles,
        'carbon_saved_kg': carbon_saved_kg,
    })