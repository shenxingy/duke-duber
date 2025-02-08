from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import UserPoints, PointsTransaction
from django.shortcuts import redirect
from django.contrib import messages    

TREE_COST = 1000  # Assume 1000 points to plant a tree

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

    return redirect('my_points')

@login_required
def my_points(request):
    user_points, created = UserPoints.objects.get_or_create(user=request.user)
    transactions = PointsTransaction.objects.filter(user=request.user).order_by('-timestamp')

    return render(request, 'points/my_points.html', {
        'user_points': user_points,
        'transactions': transactions
    })