from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserProfileForm

# Create your views here.

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # 创建用户但不立即保存
            user = form.save(commit=False)
            # 获取并设置邮箱
            email = request.POST.get('email')
            if email:
                user.email = email
                user.save()
                # 登录用户
                login(request, user)
                # messages.success(request, 'Registration successful!')
                return redirect('home')
            # else:
                # messages.error(request, 'Email is required!')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        # else:
            # messages.error(request, 'Invalid username or password')
    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    return redirect('/')

@login_required
def profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            # messages.success(request, 'Your profile has been updated!')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'accounts/profile.html', {'form': form})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            # messages.success(request, 'Your password was successfully updated!')
            return redirect('accounts:profile')
        # else:
            # messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'accounts/change_password.html', {'form': form})

