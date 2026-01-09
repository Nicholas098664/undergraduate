from django.shortcuts import render, redirect, get_object_or_404

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from .forms import MedicationForm, ScheduleForm, ProfileForm
from .models import Medication, Schedule, Profile, Notification





def index(request):
    return render(request, 'index.html')


def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, 'Passwords do not match')
            return redirect('signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('signup')

        User.objects.create_user(
            username=username,
            email=email,
            password=password1
        )

        messages.success(request, 'Account created successfully')
        return redirect('signin')

    return render(request, 'signup.html')


def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')
            return redirect('signin')

    return render(request, 'signin.html')


def signout(request):
    logout(request)
    return redirect('signin')







def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, 'No account found with this email.')
            return redirect('forgot_password')

        # generate token
        token = get_random_string(50)

        # save token in session (simple approach)
        request.session['reset_token'] = token
        request.session['reset_user'] = user.id

        reset_link = request.build_absolute_uri(
            f"/reset-password/{token}/"
        )

        send_mail(
            subject='Password Reset Request',
            message=f'Click the link to reset your password:\n{reset_link}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )

        messages.success(request, 'Password reset link sent to your email.')
        return redirect('signin')

    return render(request, 'registration/forgot_password.html')





def reset_password(request, token):
    session_token = request.session.get('reset_token')
    user_id = request.session.get('reset_user')

    if not session_token or session_token != token:
        messages.error(request, 'Invalid or expired reset link.')
        return redirect('forgot_password')

    if request.method == 'POST':
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return redirect('reset_password', token=token)

        user = User.objects.get(id=user_id)
        user.set_password(password1)
        user.save()

        # cleanup session
        del request.session['reset_token']
        del request.session['reset_user']

        messages.success(request, 'Password reset successful. Please sign in.')
        return redirect('signin')

    return render(request, 'registration/reset_password.html')






def dashboard(request):
    meds = Medication.objects.filter(user=request.user)

    unread_notifications_count = Notification.objects.filter(
        schedule__medication__user=request.user,
        is_read=False
    ).count()

    return render(request, 'dashboard.html', {
        'medications': meds,
        'unread_notifications_count': unread_notifications_count,
    })


def add_medication(request):
    if request.method == 'POST':
        form = MedicationForm(request.POST)
        if form.is_valid():
            med = form.save(commit=False)
            med.user = request.user
            med.save()
            return redirect('dashboard')
    else:
        form = MedicationForm()
    return render(request, 'add_medication.html', {'form': form})


def add_schedule(request, med_id):
    medication = get_object_or_404(Medication, id=med_id, user=request.user)
    if request.method == 'POST':
        form = ScheduleForm(request.POST)
        if form.is_valid():
            schedule = form.save(commit=False)
            schedule.medication = medication
            schedule.save()
            return redirect('dashboard')
    else:
        form = ScheduleForm()
    return render(request, 'schedule.html', {'form': form, 'medication': medication})




def profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = ProfileForm(instance=profile)
    
    return render(request, 'profile.html', {'form': form})







def notification_list(request):
    notifications = Notification.objects.filter(
        schedule__medication__user=request.user
    ).select_related(
        'schedule',
        'schedule__medication'
    ).order_by('-sent_at')

    notifications.filter(is_read=False).update(is_read=True)

    return render(request, 'notifications/list.html', {
        'notifications': notifications
    })

def mark_taken(request, pk):
    notification = get_object_or_404(Notification, pk=pk)
    notification.adherence = 'TAKEN'
    notification.save()
    return redirect('notification_list')

def mark_missed(request, pk):
    notification = get_object_or_404(Notification, pk=pk)
    notification.adherence = 'MISSED'
    notification.save()
    return redirect('notification_list')




def delete_medication(request, med_id):
    medication = get_object_or_404(Medication, id=med_id, user=request.user)

    if request.method == "POST":
        medication.delete()

    return redirect("dashboard")


def delete_schedule(request, schedule_id):
    schedule = get_object_or_404(
        Schedule,
        id=schedule_id,
        medication__user=request.user
    )

    if request.method == "POST":
        schedule.delete()

    return redirect("dashboard")  