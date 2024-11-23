from django.shortcuts import render

# Create your views here.

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout

from django.core.mail import send_mail
from django.utils import timezone
from django.http import JsonResponse
from django.contrib import messages
from .models import UserProfile, Task, User
from .forms import TaskForm, RegistrationForm, LoginForm, OTPForm
from .templates import *
import random

from datetime import datetime
import calendar
from django.utils.timezone import now
# from django.contrib.auth.models import User

def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')

    # Get the current month and year from query parameters or use today's date
    current_month = int(request.GET.get('month', now().month))
    current_year = int(request.GET.get('year', now().year))

    # Get the first day of the current month and calculate next/previous months
    first_day_of_month = datetime(current_year, current_month, 1)
    _, last_day = calendar.monthrange(current_year, current_month)

    # Calculate the previous and next months
    previous_month = current_month - 1 if current_month > 1 else 12
    previous_year = current_year if current_month > 1 else current_year - 1
    next_month = current_month + 1 if current_month < 12 else 1
    next_year = current_year if current_month < 12 else current_year + 1

    # Get tasks for the user
    tasks = Task.objects.filter(user=request.user)

    # Calculate padding days for the first week
    first_weekday = first_day_of_month.weekday()  # Monday = 0, Sunday = 6
    days_in_month = []

    # Padding for the empty days before the first day
    for _ in range(first_weekday):
        days_in_month.append({'day': None, 'tasks': []})

    # Add actual days with tasks
    for day in range(1, last_day + 1):
        date = datetime(current_year, current_month, day)
        day_tasks = tasks.filter(due_date=date)

        # Convert day_tasks queryset to a list of dictionaries
        task_list = []
        for task in day_tasks:
            task_list.append({
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'is_completed': task.is_completed,
            })

        days_in_month.append({
            'day': day,
            'tasks': task_list
        })

    context = {
        'tasks': tasks,
        'days_in_month': days_in_month,
        'current_month': first_day_of_month.strftime('%B'),
        'current_year': current_year,
        'previous_month': previous_month,
        'previous_year': previous_year,
        'next_month': next_month,
        'next_year': next_year,
    }

    return render(request, 'dashboard.html', context)

# Create Task
def create_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            return redirect('dashboard')
    else:
        form = TaskForm()
    return render(request, 'task_form.html', {'form': form})

# Update Task
def update_task(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = TaskForm(instance=task)
    return render(request, 'task_form.html', {'form': form, 'task': task})

# Delete Task
def delete_task(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('dashboard')
    return render(request, 'confirm_delete.html', {'task': task, 'action': 'delete'})

# Mark Task as Completed
def mark_task_completed(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    task.is_completed = True
    task.save()
    return redirect('dashboard')

# User Registration View
def register_user(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # Create the user
            user.email = form.cleaned_data.get('email')
            user.username = form.cleaned_data.get('email')
            email = form.cleaned_data.get('email')
            # print(User.objects.get(username=email).query)
            print(User.objects.filter(username=email))
            # return None
            if User.objects.filter(username=email):
                print("user already exists")
                messages.error(request, 'user already exists')
                return render(request, 'register.html', {'form': form})

            print("password", user.password)
            user.save()
            # user = User.objects.create_user(user)

            # Create user profile
            user_profile = UserProfile.objects.create(user=user)

            # Automatically log in the user after registration
            messages.success(request,"user created successfully....redirecting")
            login(request, user)
            return redirect('dashboard')
    else:
        form = RegistrationForm()

    return render(request, 'register.html', {'form': form})


# OTP Generation and Validation in login_user view

def login_user(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        otp = request.POST.get('otp')
        print("received otp: ",otp)
        action = request.POST.get('action')
        print(action)

        if action == 'login':
            # Regular login
            print(email, password)
            user_get = User.objects.get(email = email)
            print("user_get",user_get)
            user = authenticate(request, username=email, password=password)
            print(user)
            
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                print("from login if")
                messages.error(request, 'Invalid email or password.')

        elif action == 'send_otp':
            try:
                user = User.objects.get(email=email)
                otp_code = generate_otp()
                user_profile = UserProfile.objects.get(user=user)
                print("user profile: ",user_profile)
                user_profile.otp = otp_code
                # user.profile.otp_code = otp_code  # Assuming OTP is stored in the user profile
                user_profile.otp_created_at = timezone.now() + timezone.timedelta(minutes=10)  # Valid for 10 minutes
                user_profile.save()
                
                # Send OTP via email
                send_mail(
                    'Your OTP Code',
                    f'Your OTP code is {otp_code}. It is valid for 10 minutes.',
                    'realistworld1@gmail.com',  # Replace with your email
                    [email],
                    fail_silently=False,
                )
                return JsonResponse({'message': 'OTP sent to your email. Please check your inbox.'}, status=200)
                messages.success(request, 'OTP sent to your email. Please check your inbox.')
            except User.DoesNotExist:
                print('from except')
                return JsonResponse({'error': 'Email not found.'}, status=400)                
                # messages.error(request, 'Email not found.')

        elif action == 'login_with_otp':
            print("in elif")
            try:
                user = User.objects.get(email=email)
                user_profile = UserProfile.objects.get(user=user)
                print("user: ",user)
                if user_profile.otp == otp and timezone.now() < user_profile.otp_created_at:
                    print("otp validated")
                    login(request, user)
                    return redirect('dashboard')
                else:
                    print("form login with otp else")
                    return JsonResponse({'error': 'Invalid otp'}, status=400)
                    messages.error(request, 'Invalid or expired OTP.')
            except User.DoesNotExist:
                messages.error(request, 'Email not found.')

    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')


def generate_otp():
    return random.randint(100000, 999999)
