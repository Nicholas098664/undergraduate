from django import forms
from .models import Medication, Schedule, Profile
from django.utils.html import format_html


class MedicationForm(forms.ModelForm):
    dose_time = forms.TimeField(
        required=False,
        widget=forms.TimeInput(attrs={'type': 'time'}),
        label='Dose Time'
    )

    class Meta:
        model = Medication
        fields = ['drug_name', 'dosage', 'instructions', 'start_date', 'end_date', 'dose_time']

class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ['send_sms', 'send_email', 'is_active']




class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone_number', 'diagnosis', 'profile_picture']