
from django.db import models
from django.contrib.auth.models import User

from django.utils.html import format_html


# Medication model
from django.db import models

class Medication(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    drug_name = models.CharField(max_length=200)
    dosage = models.CharField(max_length=100)
    instructions = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    dose_time = models.TimeField(null=True, blank=True)  # <-- Add this

    def __str__(self):
        return f"{self.drug_name} ({self.user.username})"

# Reminder Schedule model
class Schedule(models.Model):
    medication = models.ForeignKey(
        Medication,
        on_delete=models.CASCADE,
        related_name="schedules"
    )

    send_sms = models.BooleanField(default=False)
    send_email = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.medication.drug_name} @ {self.medication.dose_time}"

# Notification log model
class Notification(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    sent_at = models.DateTimeField(auto_now_add=True)

    status = models.CharField(
        max_length=20,
        choices=[
            ('SENT', 'Sent'),
            ('FAILED', 'Failed')
        ]
    )

    adherence = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending'),
            ('TAKEN', 'Taken'),
            ('MISSED', 'Missed')
        ],
        default='PENDING'
    )

    # ✅ ADD THIS FIELD
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.schedule.medication.drug_name} - {self.sent_at}"


# Password reset request (for forgotten password flow)
class PasswordResetRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"Password reset for {self.user.username}"




def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return f'user_{instance.user.id}/{filename}'

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20, blank=True)
    diagnosis = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to=user_directory_path, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s profile"
