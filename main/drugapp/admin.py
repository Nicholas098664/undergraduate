
from django.contrib import admin
from .models import Medication, Schedule, Notification, PasswordResetRequest
from django.utils.html import format_html
from django.contrib import admin
from .models import Profile

@admin.register(Medication)
class MedicationAdmin(admin.ModelAdmin):
    list_display = ('drug_name', 'user', 'dosage', 'start_date', 'end_date')
    search_fields = ('drug_name', 'user__username')
    list_filter = ('start_date',)

    fields = (
        'drug_name',
        'user',
        'dosage',
        'instructions',
        'start_date',
        'end_date',
    )

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('medication', 'send_sms', 'send_email', 'is_active')
    list_filter = ('send_sms', 'send_email', 'is_active')
    search_fields = ('medication__drug_name',)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('get_schedule_info', 'sent_at', 'status')
    list_filter = ('status',)

    def get_schedule_info(self, obj):
        return obj.schedule  # or obj.schedule.reminder_time or any info you want

    get_schedule_info.short_description = 'Schedule'



@admin.register(PasswordResetRequest)
class PasswordResetRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'is_used')
    search_fields = ('user__username',)




@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'diagnosis', 'profile_picture_preview')
    search_fields = ('user__username', 'user__email', 'phone_number', 'diagnosis')

    def profile_picture_preview(self, obj):
        if obj.profile_picture:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 50%;" />', obj.profile_picture.url)
        return "No Image"

    profile_picture_preview.short_description = "Profile Picture"
  