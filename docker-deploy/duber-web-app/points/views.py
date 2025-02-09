from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import UserPoints, PointsTransaction
from django.shortcuts import redirect
from django.contrib import messages    

TREE_COST = 1000  # Assume 1000 points to plant a tree
SUCCULENT_COST = 300  # 多肉植物兑换成本
PRODUCE_COST = 500  # 蔬果兑换成本

@login_required
def redeem_tree(request):
    user_points = UserPoints.objects.get(user=request.user)

    if user_points.points >= TREE_COST:
        user_points.points -= TREE_COST
        user_points.save()

        PointsTransaction.objects.create(
            user=request.user, points=TREE_COST, transaction_type='redeem'
        )

        messages.success(request, "Congratulations! You planted a tree in Duke Forest!")
    else:
        messages.error(request, "Not enough points to redeem a tree.")

    return redirect('points:my_points')

@login_required
def redeem_succulent(request):
    user_points = UserPoints.objects.get(user=request.user)

    if user_points.points >= SUCCULENT_COST:
        user_points.points -= SUCCULENT_COST
        user_points.save()

        PointsTransaction.objects.create(
            user=request.user, points=SUCCULENT_COST, transaction_type='redeem'
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
            user=request.user, points=PRODUCE_COST, transaction_type='redeem'
        )

        messages.success(request, "Congratulations! You got fresh produce from Duke Farm!")
    else:
        messages.error(request, "Not enough points to redeem produce.")

    return redirect('points:my_points')

@login_required
def my_points(request):
    user_points, created = UserPoints.objects.get_or_create(user=request.user)
    transactions = PointsTransaction.objects.filter(user=request.user).order_by('-timestamp')

    return render(request, 'points/my_points.html', {
        'user_points': user_points,
        'transactions': transactions
    })
